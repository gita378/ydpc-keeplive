#!/usr/bin/env python3
"""
Analyze the Mobile Cloud PC client connection flow.

This script is intentionally an analyzer/capture helper, not a replacement
remote-control client. It extracts the Electron bundle, maps the login/control
flow, identifies native SDK boundaries, parses existing logs, and optionally
captures packet metadata for an authorized local test session.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


SENSITIVE_KEYS = {
    "app_secret",
    "app_key",
    "authorization",
    "authcode",
    "bizcode",
    "deviceid",
    "password",
    "phone",
    "scauthcode",
    "signature",
    "sohotoken",
    "token",
    "userid",
    "userserviceid",
    "uuid",
    "username",
    "vmid",
    "vmusername",
    "vmPassword".lower(),
    "x-soho-appkey",
    "x-soho-apptype",
    "x-soho-deviceid",
    "x-soho-signature",
    "x-soho-sohotoken",
    "x-soho-userid",
    "x-soho-uuid",
}

FLOW_ENDPOINTS = [
    "/login/encryptKey/v1",
    "/login/publicKey/v1",
    "/login/home/namePwdLogin/v1",
    "/token/checkToken/v1",
    "/cc/cloudPc/list/v6",
    "/cc/getFirmAuth/v1",
    "/cc/getRebootAuth/v1",
    "/cc/getDisasterAuth/v1",
    "/cc/cloudPc/heartbeat/v2",
    "/cc/cloudPc/infoReport/v2",
    "/cc/cloudPc/logout/v2",
]

CONTROL_HOSTS = [
    "soho.komect.com",
    "point.soho.komect.com",
    "api.soho.komect.com",
    "log.soho.komect.com",
]

PROCESS_HINTS = [
    "移动云电脑",
    "uSmartView",
    "CloudPC",
    "Electron",
]

INTERESTING_TERMS = [
    "chuanyun",
    "connectVm",
    "restartVm",
    "disconnectVm",
    "connectDesktop",
    "restartDesktop",
    "disconnectDesktop",
    "spice",
    "usbredir",
    "gstreamer",
    "x264",
    "opus",
    "vmcIp",
    "cagIp",
    "cagPort",
    "scgIp",
    "scgTcpPort",
    "scgUdpPort",
    "jwae",
    "trunk",
    "ChuanyunHead",
    "GSpice",
    "StartSpiceProcess",
    "DISPLAY_INIT",
    "REDQ",
    "surface",
    "ICE",
    "KCP",
    "UDT",
    "QUIC",
    "IKCP_CONV",
    "proxy_type",
    "proxy-sport",
    "s_proxy_port",
    "be_ssl",
    "send_tunnel_add_link",
    "init_local_rw_sock_pair_udp",
    "deal_kcp_auth_cmd",
    "deal_kcp_sync_ack_cmd",
    "deal_udt_ssl_connect",
    "60065",
    "getConnectInfo",
    "getVMReadyStatus",
    "oauth",
    "CAG",
]


@dataclass
class Finding:
    path: str
    line: int
    text: str


@dataclass
class Analysis:
    app_path: Path
    out_dir: Path
    extracted_dir: Path | None = None
    extra_logs: list[Path] = field(default_factory=list)
    include_default_logs: bool = True
    temp_dirs: list[Path] = field(default_factory=list)
    config: dict[str, str] = field(default_factory=dict)
    endpoints: dict[str, list[Finding]] = field(default_factory=dict)
    key_findings: list[Finding] = field(default_factory=list)
    log_urls: dict[str, int] = field(default_factory=dict)
    log_timeline: list[dict[str, str]] = field(default_factory=list)
    credential_shapes: list[dict[str, str]] = field(default_factory=list)
    cloud_list_shapes: list[dict[str, object]] = field(default_factory=list)
    gateway_hints: set[str] = field(default_factory=set)
    native_evidence: list[str] = field(default_factory=list)
    ida_evidence: list[str] = field(default_factory=list)
    capture_files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def redact(text: str) -> str:
    """Best-effort redaction for tokens, passwords, signatures, and auth codes."""
    if not text:
        return text

    patterns = [
        r'("?(?:X-SOHO-SohoToken|sohoToken|vmPassword|password|scAuthCode|authCode|Authorization|X-SOHO-Signature|signature|token)"?\s*[:=]\s*")([^"]*)(")',
        r"('?(?:APP_SECRET|APP_KEY)'?\s*:\s*')([^']*)(')",
        r"((?:accessToken|token|password|authCode|scAuthCode|vmid|sn|cpsid|qoe-name)=)([^&\s]+)",
        r"(--(?:accessToken|guest-passwd|guest-usr|pass-through|vmid|sn|cpsid|qoe-name|otlp-trace-id|otlp-parent-id)\s+)(\"[^\"]*\"|[A-Za-z0-9+/=._:-]+)",
        r"(\s-t\s+)(\"[^\"]*\"|\S+)",
        r"(\b(?:userName|username|vmUserName|vmpsswd|vmPassword|vmId|vmID|phone|deviceId|sohoToken)\s*[:=]\s*)(\S+)",
        r"(\bvmI[Dd]\s*\[\s*)([^\]]+)(\])",
        r"(Connecting with params:\s*)(.*)",
        r"(\b(?:syn_id|conv|traceId|parentSpanId|spanId)\s*=\s*)(0x[0-9a-f]+|[0-9a-f]{8,})",
        r'("?(?:traceId|parentSpanId|spanId|accessToken|pass-through|qoe-name)"?\s*[:=]\s*")([^"]*)(")',
    ]
    for pattern in patterns:
        text = re.sub(pattern, lambda m: f"{m.group(1)}<redacted>{m.group(3) if len(m.groups()) >= 3 else ''}", text, flags=re.I)

    header_or_id = (
        r'("?(?:X-SOHO-AppKey|X-SOHO-AppType|X-SOHO-DeviceId|X-SOHO-UserId|'
        r'X-SOHO-Uuid|deviceId|userId|userServiceId|uuid|vmId|vmID)"?\s*[:=]\s*)'
        r'(?:"[^"]*"|\d+|[^,}\s]+)'
    )
    text = re.sub(header_or_id, r'\1"<redacted>"', text, flags=re.I)
    text = re.sub(r"(\bvmI[Dd]\s*:\s*)([A-Za-z0-9._:-]+)", r"\1<redacted>", text)
    text = re.sub(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
        "<uuid>",
        text,
        flags=re.I,
    )

    # Mask account-like long hex-ish usernames embedded in titles/URLs while
    # keeping enough shape for correlation.
    text = re.sub(r"([A-Fa-f0-9]{4})[A-Fa-f0-9]{8,}([A-Fa-f0-9]{4})", r"\1****\2", text)
    return text


def rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def run_cmd(args: list[str], cwd: Path | None = None, timeout: int = 60) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or f"timeout after {timeout}s"


def read_text(path: Path, limit: int | None = None) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if limit is not None:
        data = data[:limit]
    data = data.replace(b"\x00", b"")
    return data.decode("utf-8", errors="replace")


def iter_text_files(root: Path, suffixes: tuple[str, ...], skip_dirs: set[str] | None = None) -> Iterable[Path]:
    if not root.exists():
        return
    skip_dirs = skip_dirs or {"node_modules", "out", "assets", ".git", ".vscode", "dist", "build"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in suffixes:
                yield path


def ensure_out(out_dir: Path, force: bool = False) -> None:
    if force and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evidence").mkdir(exist_ok=True)


def extract_asar(analysis: Analysis, force: bool = False, keep_extracted: bool = False) -> None:
    asar_path = analysis.app_path / "Contents" / "Resources" / "app.asar"
    if not asar_path.exists():
        analysis.warnings.append(f"missing app.asar: {asar_path}")
        return

    if keep_extracted:
        extracted = analysis.out_dir / "extracted_asar"
        if extracted.exists() and not force:
            analysis.extracted_dir = extracted
            return
        if extracted.exists():
            shutil.rmtree(extracted)
        extracted.mkdir(parents=True)
    else:
        extracted = Path(tempfile.mkdtemp(prefix="cloudpc-asar-"))
        analysis.temp_dirs.append(extracted)

    # Use npx so the script does not require a repo-local package install.
    code, out, err = run_cmd(["npx", "--yes", "@electron/asar", "extract", str(asar_path), str(extracted)], timeout=180)
    if code != 0:
        analysis.warnings.append(f"asar extract failed: {redact(err.strip() or out.strip())}")
        shutil.rmtree(extracted, ignore_errors=True)
        return
    analysis.extracted_dir = extracted


def parse_config(analysis: Analysis) -> None:
    roots: list[Path] = []
    if analysis.extracted_dir:
        roots.append(analysis.extracted_dir)

    for root in roots:
        if sys.platform == "darwin":
            config_files = [root / "config.prod.mac.js"]
        elif sys.platform == "win32":
            config_files = [root / "config.prod.win.js"]
        else:
            config_files = [root / "config.prod.js"]
        config_files = [p for p in config_files if p.exists()] or sorted(root.glob("config.prod*.js"))[:1]
        for cfg in config_files:
            text = read_text(cfg)
            for key, value in re.findall(r"([A-Z0-9_]+)\s*:\s*'([^']*)'", text):
                if key.lower() in SENSITIVE_KEYS or "SECRET" in key or "KEY" in key:
                    analysis.config[key] = "<redacted>"
                else:
                    analysis.config[key] = value
            for key, value in re.findall(r"([A-Z0-9_]+)\s*:\s*(\d+)", text):
                analysis.config.setdefault(key, value)


def collect_endpoints(analysis: Analysis) -> None:
    if not analysis.extracted_dir:
        return
    endpoint_re = re.compile(r"['\"](/(?:login|cc|system|token|active|check|point)[^'\"]+)['\"]")
    url_re = re.compile(r"https?://[^\s\"'<>),]+")
    for path in iter_text_files(analysis.extracted_dir, (".js", ".vue", ".mjs", ".cjs")):
        for n, line in enumerate(read_text(path).splitlines(), 1):
            for endpoint in endpoint_re.findall(line):
                analysis.endpoints.setdefault(endpoint, []).append(Finding(str(path), n, redact(line.strip())))
            for url in url_re.findall(line):
                analysis.endpoints.setdefault(url, []).append(Finding(str(path), n, redact(line.strip())))


def collect_key_findings(analysis: Analysis) -> None:
    roots = []
    if analysis.extracted_dir:
        roots.append(analysis.extracted_dir / "src")
    roots.append(analysis.app_path / "Contents" / "Resources" / "app.asar.unpacked")

    pattern = re.compile("|".join(re.escape(term) for term in INTERESTING_TERMS), re.I)
    for root in roots:
        if not root.exists():
            continue
        for path in iter_text_files(root, (".js", ".vue", ".h", ".json", ".ini", ".xml", ".log")):
            text = read_text(path, limit=2_000_000)
            for n, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    analysis.key_findings.append(Finding(str(path), n, redact(line.strip())))
                    if len(analysis.key_findings) >= 600:
                        return


def parse_log_json_line(line: str) -> dict | None:
    start = line.find("{")
    if start < 0:
        return None
    payload = line[start:].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def extract_log_time(line: str) -> str:
    match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)\]", line)
    return match.group(1) if match else ""


def append_log_event(analysis: Analysis, when: str, kind: str, detail: str) -> None:
    analysis.log_timeline.append(
        {
            "time": when,
            "kind": kind,
            "detail": redact(detail),
        }
    )


def summarize_cloud_list(data: dict) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    if "list" not in data:
        return None
    items = data.get("list") or []
    summary = {
        "total": data.get("total"),
        "pageSize": data.get("pageSize"),
        "items": [],
    }
    for item in items[:20]:
        if not isinstance(item, dict):
            continue
        summary["items"].append(
            {
                "spuCode": item.get("spuCode"),
                "skuName": item.get("skuName"),
                "skuSpec": item.get("skuSpec"),
                "cloudPcType": item.get("cloudPcType"),
                "vmStatusShow": item.get("vmStatusShow"),
                "serviceStatus": item.get("serviceStatus"),
                "activate": item.get("activate"),
            }
        )
    return summary


def collect_logs(analysis: Analysis) -> None:
    log_roots = []
    if analysis.include_default_logs:
        log_roots = [
            analysis.app_path / "Contents" / "teml",
            analysis.app_path / "Contents" / "Resources" / "app.asar.unpacked" / "node_modules" / "chuanyunAddOn-zte" / "ccsdk" / "mac" / "uSmartView_VDI_Client.app" / "Contents" / "log",
        ]

    ip_port_re = re.compile(r"(?:(?:cagIp|vmcIp|scgIp|ag-ip|qoeip|address|vmcip)[=: ]+)([0-9a-fA-F:.]+)|(?:(?:cagPort|vmcPort|scgTcpPort|scgUdpPort|ag-port|vmcport)[=: ]+)(\d+)", re.I)

    log_files: list[Path] = []
    for root in log_roots:
        if not root.exists():
            continue
        log_files.extend(sorted(root.glob("*.log")))
    log_files.extend([p for p in analysis.extra_logs if p.exists()])

    for log_path in log_files:
        evidence_lines: list[str] = []
        last_url = ""
        for line in read_text(log_path, limit=5_000_000).splitlines():
            when = extract_log_time(line)
            obj = parse_log_json_line(line)
            if obj and isinstance(obj, dict):
                url = obj.get("url")
                if isinstance(url, str):
                    analysis.log_urls[url] = analysis.log_urls.get(url, 0) + 1
                    last_url = url
                    if any(endpoint in url for endpoint in FLOW_ENDPOINTS) or "getFirmAuth" in url:
                        append_log_event(analysis, when, "request", url)
                code = obj.get("code")
                if code is not None:
                    detail_url = last_url
                    append_log_event(analysis, when, "response", f"{detail_url} -> code={code}, msg={obj.get('msg', '')}")
                command = obj.get("command")
                if command and ("vmID" in obj or "iCode" in obj):
                    append_log_event(analysis, when, "native-callback", f"{command}: iCode={obj.get('iCode', '')}, msg={obj.get('msg', '')}")
                data = obj.get("data")
                if isinstance(data, dict):
                    cred_keys = {"vmUserName", "vmPassword", "vmId", "vmcIp", "vmcPort", "cagIp", "cagPort", "scgIp", "scgTcpPort", "scgUdpPort", "spuCode", "bizCode", "scAuthCode"}
                    if cred_keys.intersection(data.keys()):
                        analysis.credential_shapes.append({k: ("<redacted>" if k.lower() in SENSITIVE_KEYS else str(v)) for k, v in data.items() if k in cred_keys})
                        append_log_event(analysis, when, "credential-shape", ", ".join(sorted(k for k in data if k in cred_keys)))
                    cloud_summary = summarize_cloud_list(data)
                    if cloud_summary:
                        analysis.cloud_list_shapes.append(cloud_summary)
                        append_log_event(analysis, when, "cloud-list", f"total={cloud_summary.get('total')}, items={len(cloud_summary.get('items', []))}")
            if re.search(
                r"connectDesktop ret val|GSpice-INFO|connect callback function|StartSpiceProcess|"
                r"Connecting with params|command: connect|session_connect|spice_channel_print_connect_info|"
                r"deal_create_proxy_fd_session|udt_init_ssl_ctx|init_local_rw_sock_pair_udp|"
                r"deal_kcp_auth_cmd|deal_kcp_sync_ack_cmd|deal_udt_ssl_connect|"
                r"send_tunnel_add_link|spice_session_channel_connected|initRedirectParams|notify_quit",
                line,
            ):
                append_log_event(analysis, when, "native", line.strip())
            if re.search(
                r"getFirmAuth|connect:|StartSpiceProcess|connectDesktop|GSpice-INFO|"
                r"connect callback function|callback:|session_connect|spice_channel_print_connect_info|"
                r"\[PROXY\]|udt_init_ssl_ctx|init_local_rw_sock_pair_udp|deal_kcp|IKCP_CONV|"
                r"deal_udt_ssl_connect|send_tunnel_add_link|spice_session_channel_connected|"
                r"initRedirectParams|proxy_type|TLS1\.3|notify_quit",
                line,
            ):
                evidence_lines.append(redact(line))
            for match in ip_port_re.finditer(line):
                value = match.group(1) or match.group(2)
                if value:
                    analysis.gateway_hints.add(value)
        if evidence_lines:
            out = analysis.out_dir / "evidence" / f"{log_path.stem}.redacted.log"
            out.write_text("\n".join(evidence_lines[:300]) + "\n", encoding="utf-8")


def collect_native_evidence(analysis: Analysis) -> None:
    unpacked = analysis.app_path / "Contents" / "Resources" / "app.asar.unpacked" / "node_modules"
    paths = [
        unpacked / "chuanyunAddOn" / "jsCysdk.js",
        unpacked / "chuanyunAddOn" / "ccsdk" / "mac" / "include" / "chuanyun_api.h",
        unpacked / "chuanyunAddOn-zte" / "jsCysdk.js",
        unpacked / "chuanyunAddOn-zte" / "ccsdk" / "mac" / "SohoSdk.h",
    ]
    for path in paths:
        if path.exists():
            summary = []
            for n, line in enumerate(read_text(path).splitlines(), 1):
                if re.search(
                    r"connect|restart|disconnect|init|notifyEvent|runSimpleAsyncWorker|connectDesktop|"
                    r"connectVm|proxy_type|proxy-sport|s_proxy_port|send_tunnel_add_link|"
                    r"init_local_rw_sock_pair_udp|deal_kcp|IKCP_CONV|be_ssl|quic|udt|kcp",
                    line,
                    re.I,
                ):
                    summary.append(f"{path}:{n}: {redact(line.strip())}")
            analysis.native_evidence.extend(summary[:80])

    binaries = [
        unpacked / "chuanyunAddOn" / "build" / "Release" / "chuanyunsdk.node",
        unpacked / "chuanyunAddOn" / "ccsdk" / "mac" / "lib" / "libChuanyunSDK.dylib",
        unpacked / "chuanyunAddOn" / "ccsdk" / "mac" / "bin" / "移动云电脑 .app" / "Contents" / "Frameworks" / "jwae.framework" / "Versions" / "A" / "jwae",
        unpacked / "chuanyunAddOn" / "ccsdk" / "mac" / "bin" / "移动云电脑 .app" / "Contents" / "Frameworks" / "spice-client-glib-2.0.8.framework" / "Versions" / "A" / "spice-client-glib-2.0.8",
        unpacked / "chuanyunAddOn-zte" / "build" / "Release" / "chuanyunsdk.node",
        unpacked / "chuanyunAddOn-zte" / "ccsdk" / "mac" / "uSmartView_VDI_Client.app" / "Contents" / "MacOS" / "uSmartView_VDI_Client",
        unpacked / "chuanyunAddOn-zte" / "ccsdk" / "mac" / "uSmartView_VDI_Client.app" / "Contents" / "Frameworks" / "libvdconn.dylib",
        unpacked / "chuanyunAddOn-zte" / "ccsdk" / "mac" / "uSmartView_VDI_Client.app" / "Contents" / "Frameworks" / "libcag.dylib",
    ]
    string_pattern = re.compile(
        r"connect|disconnect|restart|spice|GSpice|REDQ|DISPLAY_INIT|surface|usbredir|"
        r"websocket|auth|oauth|token|getConnectInfo|getVMReadyStatus|vmc|cag|scg|"
        r"keyboard|mouse|clipboard|jwae|trunk|ChuanyunHead|StartSpiceProcess|AES|TLS|"
        r"ICE|KCP|UDT|QUIC|IKCP_CONV|proxy_type|proxy-sport|s_proxy_port|be_ssl|"
        r"send_tunnel_add_link|init_local_rw_sock_pair_udp|deal_kcp_auth_cmd|"
        r"deal_kcp_sync_ack_cmd|deal_udt_ssl_connect|60065",
        re.I,
    )
    for binary in binaries:
        if not binary.exists() or not shutil.which("strings"):
            continue
        code, out, err = run_cmd(["strings", "-a", str(binary)], timeout=30)
        if code == 0:
            hits = []
            for line in out.splitlines():
                if string_pattern.search(line):
                    hits.append(redact(line.strip()))
                if len(hits) >= 80:
                    break
            if hits:
                evidence_file = analysis.out_dir / "evidence" / f"{binary.name}.strings.txt"
                evidence_file.write_text("\n".join(hits) + "\n", encoding="utf-8")
                analysis.native_evidence.append(f"strings evidence: {evidence_file}")


def collect_ida_evidence(analysis: Analysis) -> None:
    """Summarize selected decompiler output exported through ida-multi-mcp."""
    root = analysis.out_dir / "ida_decompiled"
    if not root.exists():
        return

    pattern = re.compile(
        r"StartSpiceProcess|ConnectStrAesEncode|buildCAGParam|AddCagAndInternalParm|"
        r"connect_to_access_gateway|send_access_gateway|recv_access_gateway|"
        r"generate_http_msg|create_http_tunnel_proxy|tn_deal_aes_code|xor_with_key|"
        r"CONNECT |ZTEC|AES|guest-usr|guest-passwd|spice",
        re.I,
    )
    for path in sorted(root.rglob("*.c")):
        hits = []
        for n, line in enumerate(read_text(path).splitlines(), 1):
            text = line.strip()
            if pattern.search(text):
                hits.append(f"{path}:{n}: {redact(text)}")
            if len(hits) >= 12:
                break
        analysis.ida_evidence.extend(hits)


def resolve_hosts(hosts: Iterable[str]) -> set[str]:
    ips: set[str] = set()
    for host in hosts:
        try:
            for family, _, _, _, sockaddr in socket.getaddrinfo(host, None):
                if family in (socket.AF_INET, socket.AF_INET6):
                    ips.add(sockaddr[0])
        except OSError:
            continue
    return ips


def build_capture_filter(analysis: Analysis) -> str:
    ips = resolve_hosts(CONTROL_HOSTS)
    for value in analysis.gateway_hints:
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", value) or ":" in value:
            ips.add(value)

    ports = {443, 1443, 8443, 8899, 5100, 60065}
    for value in analysis.gateway_hints:
        if value.isdigit() and 1 <= int(value) <= 65535:
            ports.add(int(value))

    parts = [f"host {ip}" for ip in sorted(ips)]
    parts.extend(f"port {port}" for port in sorted(ports))
    if not parts:
        return "tcp or udp"
    return "(" + " or ".join(parts) + ")"


def snapshot_connections(out_file: Path) -> None:
    code, out, err = run_cmd(["lsof", "-nP", "-iTCP", "-iUDP"], timeout=20)
    now = dt.datetime.now().isoformat(timespec="seconds")
    with out_file.open("a", encoding="utf-8") as f:
        f.write(f"\n# {now}\n")
        if code == 0:
            for line in out.splitlines():
                if any(hint.lower() in line.lower() for hint in PROCESS_HINTS):
                    f.write(redact(line) + "\n")
        else:
            f.write(f"lsof failed: {redact(err or out)}\n")


def run_capture(analysis: Analysis, interface: str, seconds: int, launch: bool) -> None:
    if launch:
        run_cmd(["open", "-n", str(analysis.app_path)], timeout=10)

    capture_filter = build_capture_filter(analysis)
    filter_file = analysis.out_dir / "capture_filter.txt"
    filter_file.write_text(capture_filter + "\n", encoding="utf-8")
    analysis.capture_files.append(filter_file)

    conn_file = analysis.out_dir / "connections.log"
    pcap_file = analysis.out_dir / "cloudpc_login_to_control.pcap"
    analysis.capture_files.extend([conn_file, pcap_file])

    tcpdump = shutil.which("tcpdump")
    proc: subprocess.Popen | None = None
    if tcpdump:
        cmd = [tcpdump, "-i", interface, "-nn", "-s0", "-w", str(pcap_file), capture_filter]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except PermissionError:
            analysis.warnings.append("tcpdump requires sudo/root; connection snapshots were still collected")
        except OSError as exc:
            analysis.warnings.append(f"tcpdump start failed: {exc}")
    else:
        analysis.warnings.append("tcpdump not found; connection snapshots were still collected")

    end = time.time() + max(1, seconds)
    while time.time() < end:
        snapshot_connections(conn_file)
        time.sleep(min(2, max(0.2, end - time.time())))

    if proc:
        proc.send_signal(signal.SIGINT)
        try:
            _, err = proc.communicate(timeout=10)
            if proc.returncode not in (0, None):
                analysis.warnings.append(f"tcpdump exited with {proc.returncode}: {redact(err)}")
        except subprocess.TimeoutExpired:
            proc.kill()
            analysis.warnings.append("tcpdump did not exit cleanly and was killed")


def write_report(analysis: Analysis) -> Path:
    report = analysis.out_dir / "REPORT.md"
    lines: list[str] = []
    lines.append("# 移动云电脑连接链路分析报告")
    lines.append("")
    lines.append(f"- 生成时间: {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- 应用路径: `{analysis.app_path}`")
    lines.append(f"- 操作系统: `{platform.platform()}`")
    lines.append("- 脱敏策略: token、密码、签名、authCode、APP_SECRET 默认写为 `<redacted>`")
    lines.append("")

    lines.append("## 结论")
    lines.append("")
    lines.append("这个客户端是 Electron 壳加 native 远控 SDK。Electron 负责登录、列表、接口鉴权和 IPC 分发；真正的画面、键鼠、音频、USB/剪贴板等远控数据面在 native SDK/嵌入客户端里。")
    lines.append("")
    lines.append("当前 ZTE 成功日志支持的桌面数据面不是 `CAG 200 OK` 后直接在 TCP 上写 SPICE `REDQ`。实际链路是 GSpice 先连接本机 `127.0.0.1` socketpair，native proxy thread 创建 UDP proxy fd session，再按 `proxy_type[ice]` 建立 KCP/UDT-style 会话，`be_ssl=1` 时进入 TLS 1.3，之后通过 `send_tunnel_add_link` 为 main/display/inputs/cursor/playback/record 等 SPICE channel 绑定虚拟通道。")
    lines.append("")
    lines.append("`libcag`/ZTEC 日志里的 `notify_quit` 表明该阶段可作为前置连通性或控制面证据，但不应把它误判为最终 SPICE 数据承载 socket。")
    lines.append("")
    lines.append("主要链路如下:")
    lines.append("")
    lines.append("1. 启动后请求 `/login/encryptKey/v1` 获取 RSA 公钥，再请求 `/system/settings/v1` 拉配置。")
    lines.append("2. 登录请求走 `/login/publicKey/v1`、`/login/home/namePwdLogin/v1` 等接口，登录态保存为 `sohoToken`/`userId`。")
    lines.append("3. 云电脑列表来自 `/cc/cloudPc/list/v6`，点击连接后请求 `/cc/getFirmAuth/v1`。")
    lines.append("4. `/cc/getFirmAuth/v1` 返回一次性厂商连接参数，字段形态包括 `vmUserName`、`vmPassword`、`vmId`、`vmcIp`、`vmcPort`、`cagIp`、`cagPort`、`scgIp`、`scgTcpPort`、`scgUdpPort`、`spuCode`、`bizCode`、`scAuthCode`。")
    lines.append("5. Renderer 通过 preload 暴露的 `mainApi.connectWorker()` 调 Electron 主进程 IPC `worker-connect`。")
    lines.append("6. 主进程按 `spuCode` 分流: `zte-*` 调 `chuanyunAddOn-zte`/`connectDesktop`；`wave-*` 在 Windows 拉起 `CloudPC.exe token=...`；其他走 `chuanyunAddOn`/`connectVm`。")
    lines.append("7. native 层回调 `connect/reconnect/disconnect` 给 Electron，Electron 再通知页面，并启动 `/cc/cloudPc/heartbeat/v2` 和 `/cc/cloudPc/infoReport/v2`。")
    lines.append("8. ZTE 数据面关键日志顺序: `session_connect after m_pHost[...]` -> `socket connect to 127.0.0.1` -> `[PROXY] Setting up spice proxy link with SSL=1` -> `IKCP_CONV_*` -> `TLS1.3` -> `send_tunnel_add_link` -> `all channel 6/6 connect success`。")
    lines.append("")

    lines.append("## 关键配置")
    lines.append("")
    if analysis.config:
        for key in sorted(analysis.config):
            lines.append(f"- `{key}`: `{redact(str(analysis.config[key]))}`")
    else:
        lines.append("- 未解析到配置，可能 asar 未成功解包。")
    lines.append("")

    lines.append("## 接口清单")
    lines.append("")
    for endpoint in FLOW_ENDPOINTS:
        hits = analysis.endpoints.get(endpoint, [])
        lines.append(f"- `{endpoint}`: {len(hits)} 个源码引用")
    extra = sorted(k for k in analysis.endpoints if k not in FLOW_ENDPOINTS)
    lines.append("")
    lines.append(f"- 其他 URL/接口引用数: {len(extra)}")
    for endpoint in extra[:80]:
        lines.append(f"- `{redact(endpoint)}`: {len(analysis.endpoints[endpoint])} 个引用")
    lines.append("")

    lines.append("## Native SDK 边界")
    lines.append("")
    lines.append("- `chuanyunAddOn/jsCysdk.js`: JS 包装 `init/connect/restart/disconnect/callback`，底层调用 `runSimpleAsyncWorker`。")
    lines.append("- `chuanyun_api.h`: 暴露 `chuanyun_init`、`connectVm`、`restartVm`、`disconnectVm`。")
    lines.append("- `chuanyunAddOn-zte/jsCysdk.js`: JS 包装 ZTE 连接参数，传入 `vmUserName/vmPassword/vmId/vmc/cag/scg`。")
    lines.append("- `SohoSdk.h`: 暴露 `connectDesktop`、`restartDesktop`、`disconnectDesktop`、网络状态、视频参数等接口。")
    lines.append("- 当前日志中的 `spuCode=zte-cloud-pc` 会进入 ZTE 分支：`chuanyunsdk.node` -> `libvdconn.dylib` -> `libcag.dylib`/`uSmartView_VDI_Client`。")
    lines.append("- 嵌入的 ZTE 客户端包含 `libcag`、`libusbredirect`、`libclipboard_mac`、`QtNetwork` 等；自研 viewer 依赖 `spice-client-glib`、`usbredir`、`gstreamer`、`libx264`、`opus` 等。")
    lines.append("- 另一个 `chuanyunAddOn` 分支包含 `libChuanyunSDK.dylib`、内嵌 `jwae.framework` 和 `spice-client-glib`，字符串中可见 CEM/OAuth/getConnectInfo、SCG、trunk/TLS/auth 等线索；但它不是这份日志实际命中的 ZTE 分支。")
    lines.append("- 可用 `cloudpc_zte_session_trace.py` 从 `client.log`/`cag.log` 生成脱敏时序，重点观察 socketpair、PROXY、KCP、TLS1.3、add_link 和 channel success。")
    lines.append("")
    for item in analysis.native_evidence[:120]:
        lines.append(f"- `{redact(item)}`")
    lines.append("")

    if analysis.ida_evidence:
        lines.append("## IDA 静态证据")
        lines.append("")
        lines.append("以下是 ida-multi-mcp 导出的关键函数摘要，只列函数/字符串命中点，不写入运行时账号凭证。")
        lines.append("")
        for item in analysis.ida_evidence[:160]:
            lines.append(f"- `{redact(item)}`")
        lines.append("")

    lines.append("## 日志证据")
    lines.append("")
    if analysis.log_urls:
        for url, count in sorted(analysis.log_urls.items(), key=lambda x: (-x[1], x[0]))[:80]:
            lines.append(f"- `{redact(url)}`: {count}")
    else:
        lines.append("- 未解析到接口日志。")
    lines.append("")

    if analysis.credential_shapes:
        lines.append("已在日志中发现厂商连接参数结构，以下只展示字段形态:")
        seen = set()
        for shape in analysis.credential_shapes[:20]:
            keys = tuple(sorted(shape.keys()))
            if keys in seen:
                continue
            seen.add(keys)
            lines.append(f"- `{', '.join(keys)}`")
        lines.append("")

    if analysis.cloud_list_shapes:
        lines.append("云电脑列表返回结构摘要:")
        seen_clouds = set()
        for shape in analysis.cloud_list_shapes[:20]:
            key = json.dumps(shape, ensure_ascii=False, sort_keys=True)
            if key in seen_clouds:
                continue
            seen_clouds.add(key)
            lines.append(f"- `total={shape.get('total')}`, `pageSize={shape.get('pageSize')}`")
            for item in shape.get("items", [])[:5]:
                if isinstance(item, dict):
                    lines.append(
                        "- "
                        + ", ".join(
                            f"`{k}={redact(str(v))}`"
                            for k, v in item.items()
                            if v is not None
                        )
                    )
        lines.append("")

    if analysis.log_timeline:
        lines.append("## 控制面时序")
        lines.append("")
        lines.append("以下来自客户端日志，按出现顺序脱敏汇总；同一秒内多个埋点/接口可能并发。")
        lines.append("")
        previous = None
        shown = 0
        for event in analysis.log_timeline:
            item = (event["time"], event["kind"], event["detail"])
            if item == previous:
                continue
            previous = item
            lines.append(f"- `{event['time'] or '-'}` `{event['kind']}` {event['detail']}")
            shown += 1
            if shown >= 120:
                lines.append("- `...` 后续事件已省略，可看 `evidence/*.redacted.log`。")
                break
        lines.append("")

    if analysis.gateway_hints:
        lines.append("日志中出现的数据面/网关线索，供抓包过滤器使用:")
        for item in sorted(analysis.gateway_hints)[:80]:
            lines.append(f"- `{redact(item)}`")
        lines.append("")

    lines.append("## 抓包建议")
    lines.append("")
    lines.append("需要抓包，但目标不是破解 HTTPS 内容，也不是复刻保活客户端，而是确认 native 数据面连接到哪些网关、端口、协议以及连接时序。控制面接口在客户端日志里已经比较完整；数据面在 native 进程里，必须结合 pcap、`lsof` 和 SDK 日志看。")
    lines.append("")
    lines.append("建议流程:")
    lines.append("")
    lines.append("1. 先退出客户端，清空或备份旧日志。")
    lines.append("2. 运行本脚本 `--capture --launch --seconds 300`。")
    lines.append("3. 在 300 秒内手动完成登录、点击连接、进入桌面、操作鼠标键盘、断开连接。")
    lines.append("4. 查看 `REPORT.md`、`connections.log`、`cloudpc_login_to_control.pcap`、`evidence/*.redacted.log`。")
    lines.append("5. 对 ZTE 成功连接，优先校验 UDP/KCP 与日志中的 `IKCP_CONV_*`、`TLS1.3`、`send_tunnel_add_link` 时间戳关系。")
    lines.append("")
    lines.append("抓包过滤器:")
    lines.append("")
    lines.append("```tcpdump")
    lines.append(build_capture_filter(analysis))
    lines.append("```")
    lines.append("")

    if analysis.capture_files:
        lines.append("## 本次抓包输出")
        lines.append("")
        for path in analysis.capture_files:
            lines.append(f"- `{path}`")
        lines.append("")

    if analysis.warnings:
        lines.append("## 警告")
        lines.append("")
        for warning in analysis.warnings:
            lines.append(f"- {redact(warning)}")
        lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def write_evidence_index(analysis: Analysis) -> None:
    evidence = analysis.out_dir / "evidence" / "source_hits.redacted.txt"
    lines = []
    for finding in analysis.key_findings:
        lines.append(f"{finding.path}:{finding.line}: {finding.text}")
    evidence.write_text("\n".join(lines) + "\n", encoding="utf-8")

    endpoints = analysis.out_dir / "evidence" / "endpoints.redacted.json"
    payload = {
        redact(k): [
            {"path": v.path, "line": v.line, "text": v.text}
            for v in values[:20]
        ]
        for k, values in sorted(analysis.endpoints.items())
    }
    endpoints.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Mobile Cloud PC login-to-remote-control flow.")
    parser.add_argument("--app", type=Path, default=Path.cwd() / "移动云电脑.app", help="Path to 移动云电脑.app")
    parser.add_argument("--out", type=Path, default=Path.cwd() / "cloudpc_analysis", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Recreate output/extracted files")
    parser.add_argument("--no-extract", action="store_true", help="Skip app.asar extraction")
    parser.add_argument("--capture", action="store_true", help="Run tcpdump/lsof capture for an authorized live session")
    parser.add_argument("--launch", action="store_true", help="Launch the app before live capture")
    parser.add_argument("--log", action="append", type=Path, default=[], help="Additional client log file to parse; can be repeated")
    parser.add_argument("--skip-default-logs", action="store_true", help="Only parse logs passed with --log; skip bundled app/native logs")
    parser.add_argument("--keep-extracted", action="store_true", help="Keep raw extracted app.asar under the output directory")
    parser.add_argument("--interface", default="en0", help="tcpdump interface, e.g. en0 on macOS Wi-Fi")
    parser.add_argument("--seconds", type=int, default=300, help="Live capture duration")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    app_path = args.app.resolve()
    out_dir = args.out.resolve()

    if not app_path.exists():
        print(f"app not found: {app_path}", file=sys.stderr)
        return 2

    ensure_out(out_dir, force=args.force)
    analysis = Analysis(
        app_path=app_path,
        out_dir=out_dir,
        extra_logs=[p.resolve() for p in args.log],
        include_default_logs=not args.skip_default_logs,
    )

    try:
        if not args.no_extract:
            extract_asar(analysis, force=args.force, keep_extracted=args.keep_extracted)

        parse_config(analysis)
        collect_endpoints(analysis)
        collect_key_findings(analysis)
        collect_logs(analysis)
        collect_native_evidence(analysis)
        collect_ida_evidence(analysis)

        if args.capture:
            run_capture(analysis, args.interface, args.seconds, args.launch)

        write_evidence_index(analysis)
        report = write_report(analysis)
        print(report)
        return 0
    finally:
        if not args.keep_extracted:
            for temp_dir in analysis.temp_dirs:
                shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
