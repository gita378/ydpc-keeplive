#!/usr/bin/env python3
"""
移动云电脑 VM 开机/连接脚本。

通过 SOHO API 获取 firmAuth，然后 CSAP 协议完成 VM 启动。
支持 VM 处于关机状态的唤醒和已开机状态的直连。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cloudpc_ztec_client import (
    ZteCsapClient,
    fetch_firm_auth_from_soho,
    load_zte_crypto_keys,
)



def boot_vm(
    username: str,
    password: str,
    vm_index: int = 0,
    poll_timeout: float = 90.0,
) -> int:
    print(f"[*] SOHO 登录: {username} (VM索引 {vm_index})")
    auth = fetch_firm_auth_from_soho(
        username=username, password=password, vm_index=vm_index, verify_tls=False
    )
    print(f"    CAG={auth.cag_host}:{auth.cag_port} VMC={auth.vmc_host}:{auth.vmc_port}")
    print(f"    vmId={auth.vm_id}")

    keys = load_zte_crypto_keys()

    csap = ZteCsapClient(auth, keys, timeout=30.0, verify_tls=False)
    print(f"[*] CSAP 开始 (trace={csap.trace_id[:12]}...)")

    try:
        result = csap.get_fresh_connect_command(poll_timeout=poll_timeout)
    except RuntimeError as e:
        print(f"[!] 失败: {e}")
        return 1

    cmd = result.connect_command
    print(f"\n[+] VM 就绪!")
    print(f"    session_key = {cmd.session_key[:16]}...")
    print(f"    spice_host  = {cmd.spice_host}")
    print(f"    kcp_port    = {cmd.kcp_dest_port}")
    print(f"    spice_port  = {cmd.spice_port}")
    print(f"    vm_id       = {cmd.vm_id}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="移动云电脑 VM 开机")
    parser.add_argument("--un", default=os.environ.get("UN", "zhaoboy"))
    parser.add_argument("--pw", default=os.environ.get("PW", ""))
    parser.add_argument("--vm-index", type=int, default=0)
    parser.add_argument("--poll-timeout", type=float, default=90.0)
    args = parser.parse_args()

    if not args.pw:
        print("用法: python3 cloudpc_start_desktop.py --un <用户名> --pw <密码>")
        sys.exit(1)

    sys.exit(boot_vm(args.un, args.pw, args.vm_index, args.poll_timeout))


if __name__ == "__main__":
    main()
