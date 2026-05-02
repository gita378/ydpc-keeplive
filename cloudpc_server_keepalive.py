#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cron-friendly ZTE Cloud PC keepalive runner.

Run this from a server every 10 minutes. One run does:

1. Login to SOHO control plane.
2. Fetch fresh getFirmAuth data.
3. Perform the ZTEC/CAG three-stage auth.
4. Keep the CAG socket open for a short hold window, then close it.

It intentionally does not start a viewer, does not request a display, and does
not call /cc/cloudPc/logout/v2. A successful CAG auth can still kick an active
official client session because the platform treats it as another login.
"""

from __future__ import annotations

import argparse
import fcntl
import logging
import os
import random
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from cloudpc_protocol import CloudPcClient
from cloudpc_ztec import (
    AUTH_TYPE_RADIUS,
    build_ztec_stage1,
    build_ztec_stage3_radius,
    parse_cag_reply_code,
    parse_ztec_stage2,
    recv_exact,
)


LOG = logging.getLogger("cloudpc_server_keepalive")


@dataclass(frozen=True)
class KeepaliveResult:
    ok: bool
    reply_code: int | None
    vm_id: str
    vmc: str
    cag: str
    client_key: int
    server_key: int | None
    aes_flag: int | None


class SingleInstanceLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None

    def __enter__(self) -> "SingleInstanceLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a+")
        try:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another keepalive run is active: {self.path}") from exc
        self._fh.seek(0)
        self._fh.truncate()
        self._fh.write(str(os.getpid()))
        self._fh.flush()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fh is not None:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            self._fh.close()


def cag_auth_hold(
    *,
    cag_host: str,
    cag_port: int,
    vmc_host: str,
    vmc_port: int,
    vm_id: str,
    vm_username: str,
    vm_password: str,
    hold_seconds: float,
    timeout: float,
) -> KeepaliveResult:
    client_key = random.getrandbits(32)
    server_key = None
    aes_flag = None
    reply_code = None

    stage1 = build_ztec_stage1(
        auth_type=AUTH_TYPE_RADIUS,
        vm_id=vm_id,
        client_key=client_key,
    )

    with socket.create_connection((cag_host, cag_port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(stage1)

        stage2_raw = recv_exact(sock, 50)
        stage2 = parse_ztec_stage2(stage2_raw)
        server_key = stage2.server_key
        aes_flag = stage2.aes_flag

        stage3 = build_ztec_stage3_radius(
            dest_host=vmc_host,
            dest_port=vmc_port,
            username=vm_username,
            password=vm_password,
            client_key=client_key,
            server_key=server_key,
            aes_flag=aes_flag,
        )
        sock.sendall(stage3)
        reply_raw = recv_exact(sock, 36)
        reply_code = parse_cag_reply_code(reply_raw)

        LOG.info(
            "CAG auth reply=%s client_key=0x%08x server_key=0x%08x aes_flag=0x%x",
            reply_code,
            client_key,
            server_key,
            aes_flag,
        )
        if reply_code != 200:
            return KeepaliveResult(
                ok=False,
                reply_code=reply_code,
                vm_id=vm_id,
                vmc=f"{vmc_host}:{vmc_port}",
                cag=f"{cag_host}:{cag_port}",
                client_key=client_key,
                server_key=server_key,
                aes_flag=aes_flag,
            )

        if hold_seconds > 0:
            LOG.info("holding authenticated CAG socket for %.1fs", hold_seconds)
            deadline = time.monotonic() + hold_seconds
            while time.monotonic() < deadline:
                time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))

    return KeepaliveResult(
        ok=True,
        reply_code=reply_code,
        vm_id=vm_id,
        vmc=f"{vmc_host}:{vmc_port}",
        cag=f"{cag_host}:{cag_port}",
        client_key=client_key,
        server_key=server_key,
        aes_flag=aes_flag,
    )


def run_once(args: argparse.Namespace) -> KeepaliveResult:
    client = CloudPcClient(verify_tls=not args.no_verify_tls)
    client.bootstrap_public_key()
    client.login_pwd(args.username, args.password)

    vms = client.list_cloud_pcs()
    if not vms:
        raise RuntimeError("no cloud PC found under this account")
    if args.vm_index < 0 or args.vm_index >= len(vms):
        raise RuntimeError(f"vm index {args.vm_index} out of range, total={len(vms)}")

    vm = vms[args.vm_index]
    user_service_id = int(vm["userServiceId"])
    LOG.info(
        "target userServiceId=%s vmName=%s status=%s",
        user_service_id,
        vm.get("vmName"),
        vm.get("vmStatusShow"),
    )

    auth = client.get_firm_auth(user_service_id)
    LOG.info(
        "firmAuth vm=%s vmc=%s:%s cag=%s:%s",
        auth.get("vmId"),
        auth.get("vmcIp"),
        auth.get("vmcPort"),
        auth.get("cagIp"),
        auth.get("cagPort"),
    )

    if args.platform_heartbeat:
        try:
            hb = client.heartbeat(user_service_id)
            LOG.info("platform heartbeat code=%s msg=%s", hb.get("code"), hb.get("msg"))
        except Exception as exc:
            LOG.warning("platform heartbeat ignored: %s", exc)

    return cag_auth_hold(
        cag_host=str(auth["cagIp"]),
        cag_port=int(auth["cagPort"]),
        vmc_host=str(auth["vmcIp"]),
        vmc_port=int(auth["vmcPort"]),
        vm_id=str(auth["vmId"]),
        vm_username=str(auth["vmUserName"]),
        vm_password=str(auth["vmPassword"]),
        hold_seconds=args.hold_seconds,
        timeout=args.timeout,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one ZTE Cloud PC keepalive cycle")
    parser.add_argument("--username", default=os.environ.get("UN"), help="SOHO account, or env UN")
    parser.add_argument("--password", default=os.environ.get("PW"), help="SOHO password, or env PW")
    parser.add_argument("--vm-index", type=int, default=int(os.environ.get("VM_INDEX", "0")))
    parser.add_argument("--hold-seconds", type=float, default=float(os.environ.get("HOLD_SECONDS", "45")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TIMEOUT", "10")))
    parser.add_argument("--lock-file", type=Path, default=Path(os.environ.get("LOCK_FILE", "/tmp/cloudpc_server_keepalive.lock")))
    parser.add_argument("--platform-heartbeat", action="store_true", help="also call SOHO heartbeat once")
    parser.add_argument("--no-verify-tls", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if not args.username or not args.password:
        parser.error("need --username/--password, or set UN/PW environment variables")

    try:
        with SingleInstanceLock(args.lock_file):
            result = run_once(args)
    except RuntimeError as exc:
        LOG.warning("%s", exc)
        return 0 if "another keepalive run is active" in str(exc) else 1
    except Exception:
        LOG.exception("keepalive failed")
        return 1

    if result.ok:
        LOG.info("keepalive OK vm=%s vmc=%s cag=%s", result.vm_id, result.vmc, result.cag)
        return 0

    LOG.error("keepalive failed reply=%s vm=%s vmc=%s cag=%s", result.reply_code, result.vm_id, result.vmc, result.cag)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
