#!/usr/bin/env python3
"""
Build a redacted ZTE/ICE/KCP session timeline from Mobile Cloud PC logs.

This is an analysis helper only. It does not create network connections,
does not implement KCP/UDT/SPICE, and does not replay authentication data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_LOG_DIR = (
    Path.cwd()
    / "移动云电脑.app"
    / "Contents"
    / "Resources"
    / "app.asar.unpacked"
    / "node_modules"
    / "chuanyunAddOn-zte"
    / "ccsdk"
    / "mac"
    / "uSmartView_VDI_Client.app"
    / "Contents"
    / "log"
)


CHANNEL_NAMES = {
    "1": "main",
    "2": "display",
    "3": "inputs",
    "4": "cursor",
    "5": "playback",
    "6": "record",
    "12": "outband",
}

PROXY_CMDS = {
    0x0A: "DATA",
    0x1A: "ADD_LINK",
    0x2A: "CLOSE",
    0x3A: "VM_INFO",
}


@dataclass
class Event:
    sort_time: str
    time: str
    source: str
    line: int
    category: str
    detail: str


@dataclass
class Summary:
    spice_host: str | None = None
    spice_port: str | None = None
    proxy_type: str | None = None
    proxy_secure_port: str | None = None
    cag_host: str | None = None
    cag_port: str | None = None
    tls_version: str | None = None
    quic: str | None = None
    be_ssl: str | None = None
    kcp_be_ssl: str | None = None
    spice_add_links: int = 0
    outband_add_links: int = 0
    all_channels_connected: bool = False
    ztec_notify_quit_seen: bool = False


TIME_PATTERNS = [
    re.compile(r"^(?P<ts>\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})"),
    re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"),
]


EVENT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ztec", re.compile(r"notify_quit", re.I)),
    ("launch", re.compile(r"StartSpiceProcess AddConnectParm cmd:", re.I)),
    ("session", re.compile(r"session_connect (?:before|after)", re.I)),
    ("local-spice", re.compile(r"spice_channel_print_connect_info", re.I)),
    ("proxy", re.compile(r"\[PROXY\]|deal_create_proxy_fd_session", re.I)),
    ("ssl", re.compile(r"udt_init_ssl_ctx|deal_udt_ssl_connect|TLS1\.3|ssl connect", re.I)),
    ("ice", re.compile(r"initRedirectParams|proxy_type\[ice\]|s_proxy_port", re.I)),
    ("kcp", re.compile(r"init_local_rw_sock_pair_udp|deal_kcp_auth_cmd|deal_kcp_sync_ack_cmd|IKCP_CONV|be_quic", re.I)),
    ("tunnel", re.compile(r"send_tunnel_add_link", re.I)),
    ("spice-link", re.compile(r"spice_channel_(?:send|recv)_link", re.I)),
    ("spice", re.compile(r"spice_session_channel_connected|all channel .* connect success", re.I)),
    ("result", re.compile(r"connect success|session connect success", re.I)),
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract a redacted ZTE ICE/KCP/TLS/SPICE timeline from local logs."
    )
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR, help="Directory containing client.log/cag.log")
    parser.add_argument("--log", action="append", type=Path, default=[], help="Extra log file; can be repeated")
    parser.add_argument("--out", type=Path, help="Write Markdown report to this path")
    parser.add_argument("--json", type=Path, help="Write JSON event data to this path")
    parser.add_argument("--grep", help="Only include events whose redacted detail contains this text")
    parser.add_argument("--frame-hex", help="Decode one offline CAG proxy frame header from hex; no network is used")
    parser.add_argument("--limit", type=int, default=220, help="Maximum events to print")
    return parser.parse_args(argv)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def redact(text: str) -> str:
    """Redact credentials and session identifiers while preserving protocol shape."""
    if not text:
        return text

    rules = [
        (r"(--(?:guest-passwd|guest-usr|accessToken|pass-through|vmid|sn|cpsid|qoe-name|otlp-trace-id|otlp-parent-id)\s+)(\"[^\"]*\"|\S+)", r"\1<redacted>"),
        (r"(\b(?:syn_id|conv|traceId|parentSpanId|spanId)\s*=\s*)(0x[0-9a-f]+|[0-9a-f]{8,})", r"\1<redacted>"),
        (r'("?(?:vmid|vmId|userno|accessToken|pass-through|traceId|parentSpanId|spanId)"?\s*[:=]\s*")([^"]*)(")', r"\1<redacted>\3"),
        (r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", r"<uuid>"),
    ]
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = re.sub(r"([A-Fa-f0-9]{4})[A-Fa-f0-9]{8,}([A-Fa-f0-9]{4})", r"\1****\2", text)
    return text


def extract_time(line: str) -> tuple[str, str]:
    for pattern in TIME_PATTERNS:
        match = pattern.search(line)
        if not match:
            continue
        raw = match.group("ts")
        if len(raw) >= 21 and raw[2] == "-":
            parsed = dt.datetime.strptime(raw, "%y-%m-%d %H:%M:%S.%f")
        else:
            parsed = dt.datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
        return raw, parsed.isoformat(timespec="milliseconds")
    return "", ""


def classify(line: str) -> str | None:
    for category, pattern in EVENT_PATTERNS:
        if pattern.search(line):
            return category
    return None


def strip_prefix(line: str) -> str:
    """Keep protocol message, drop most logging boilerplate."""
    line = re.sub(r"^\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+", "", line)
    line = re.sub(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+", "", line)
    line = re.sub(r"^\[[A-Z]+\s*\]\s+\d+#\s*\d+\s+", "", line)
    return line.strip()


def discover_logs(log_dir: Path, extras: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    if log_dir.exists():
        for pattern in ("client.log*", "cag.log*", "vdconn.log*"):
            files.extend(sorted(log_dir.glob(pattern)))
    files.extend(Path(p) for p in extras)

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved.exists() and resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def update_summary(summary: Summary, line: str) -> None:
    if "notify_quit" in line:
        summary.ztec_notify_quit_seen = True

    if match := re.search(r"session_connect after m_pHost\[([^\]]*)\], m_pPort\[(\d+)\]", line):
        summary.spice_host = match.group(1)
        summary.spice_port = match.group(2)

    if match := re.search(r"s_proxy_port\[(\d+)\]\s+proxy_type\[([^\]]+)\]", line):
        summary.proxy_secure_port = match.group(1)
        summary.proxy_type = match.group(2)

    if match := re.search(r"from:([0-9a-fA-F:.]+):(\d+)", line):
        summary.cag_host = match.group(1)
        summary.cag_port = match.group(2)

    if match := re.search(r"TLS([0-9.]+)\(0x[0-9a-f]+\)", line, re.I):
        summary.tls_version = "TLS" + match.group(1)

    if match := re.search(r"support quic:(\d).*?proxy_sock->be_ssl:(\d).*?kcp->be_ssl:(\d)", line):
        summary.quic = match.group(1)
        summary.be_ssl = match.group(2)
        summary.kcp_be_ssl = match.group(3)

    if re.search(r"all channel\s+\d+/\d+\s+connect success", line, re.I):
        summary.all_channels_connected = True

    if "send_tunnel_add_link" in line:
        if "non-SPICE" in line or "outband" in line:
            summary.outband_add_links += 1
        elif "channel type" in line:
            summary.spice_add_links += 1


def decode_proxy_frame_header(frame_hex: str) -> dict[str, object]:
    """Decode the 4-byte proxy header from an offline hex dump."""
    compact = re.sub(r"[^0-9a-fA-F]", "", frame_hex)
    if len(compact) < 8:
        raise ValueError("need at least 4 bytes of hex")
    data = bytes.fromhex(compact[:8])
    cmd = data[0]
    link_id = data[1]
    data_len = data[2] | (data[3] << 8)
    return {
        "cmd": cmd,
        "cmd_name": PROXY_CMDS.get(cmd, "UNKNOWN"),
        "link_id": link_id,
        "data_len": data_len,
    }


def extract_events(paths: Iterable[Path], grep: str | None = None) -> tuple[list[Event], Summary]:
    events: list[Event] = []
    summary = Summary()
    grep_lower = grep.lower() if grep else None

    for path in paths:
        for number, raw_line in enumerate(read_text(path).splitlines(), 1):
            category = classify(raw_line)
            if not category:
                continue
            when, sort_time = extract_time(raw_line)
            detail = redact(strip_prefix(raw_line))
            if grep_lower and grep_lower not in detail.lower():
                continue
            update_summary(summary, detail)
            events.append(
                Event(
                    sort_time=sort_time,
                    time=when,
                    source=path.name,
                    line=number,
                    category=category,
                    detail=detail,
                )
            )

    events.sort(key=lambda item: (item.sort_time, item.source, item.line))
    return events, summary


def channel_name(channel_type: str | None) -> str:
    if not channel_type:
        return ""
    return CHANNEL_NAMES.get(channel_type, f"type-{channel_type}")


def tcpdump_filter(summary: Summary) -> str:
    parts = []
    if summary.cag_host:
        parts.append(f"host {summary.cag_host}")
    for port in (summary.cag_port, summary.proxy_secure_port, summary.spice_port):
        if port:
            parts.append(f"port {port}")
    if not parts:
        return "(udp or tcp) and (port 8899 or port 60065 or port 5100)"
    return "(udp or tcp) and (" + " or ".join(dict.fromkeys(parts)) + ")"


def render_markdown(events: list[Event], summary: Summary, limit: int) -> str:
    shown = events[: max(0, limit)]
    lines: list[str] = []
    lines.append("# ZTE ICE/KCP Session Timeline")
    lines.append("")
    lines.append("This report is redacted and analysis-only. It does not contain packet replay code.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- SPICE host: `{summary.spice_host or '<unknown>'}`")
    lines.append(f"- SPICE port: `{summary.spice_port or '<unknown>'}`")
    lines.append(f"- Proxy type: `{summary.proxy_type or '<unknown>'}`")
    lines.append(f"- Secure proxy port: `{summary.proxy_secure_port or '<unknown>'}`")
    lines.append(f"- CAG endpoint: `{summary.cag_host or '<unknown>'}:{summary.cag_port or '<unknown>'}`")
    lines.append(f"- QUIC enabled: `{summary.quic or '<unknown>'}`")
    lines.append(f"- proxy be_ssl: `{summary.be_ssl or '<unknown>'}`")
    lines.append(f"- kcp be_ssl: `{summary.kcp_be_ssl or '<unknown>'}`")
    lines.append(f"- TLS version: `{summary.tls_version or '<unknown>'}`")
    lines.append(f"- SPICE add_link events: `{summary.spice_add_links}`")
    lines.append(f"- outband add_link events: `{summary.outband_add_links}`")
    lines.append(f"- all channels connected: `{summary.all_channels_connected}`")
    lines.append(f"- ZTEC notify_quit seen: `{summary.ztec_notify_quit_seen}`")
    lines.append("")
    lines.append("## Capture Filter")
    lines.append("")
    lines.append("```tcpdump")
    lines.append(tcpdump_filter(summary))
    lines.append("```")
    lines.append("")
    lines.append("## Events")
    lines.append("")
    lines.append("| Time | Source | Line | Category | Detail |")
    lines.append("|---|---:|---:|---|---|")
    for event in shown:
        detail = event.detail.replace("|", "\\|")
        lines.append(f"| `{event.time or '-'}` | `{event.source}` | {event.line} | `{event.category}` | {detail} |")
    if len(events) > len(shown):
        lines.append(f"| ... | ... | ... | ... | {len(events) - len(shown)} events omitted by --limit |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    logs = discover_logs(args.log_dir, args.log)
    if not logs:
        print(f"no logs found under {args.log_dir}", file=sys.stderr)
        return 2

    events, summary = extract_events(logs, args.grep)
    report = render_markdown(events, summary, args.limit)

    if args.frame_hex:
        decoded = decode_proxy_frame_header(args.frame_hex)
        report += "\n## Offline Proxy Header Decode\n\n"
        report += "```json\n"
        report += json.dumps(decoded, ensure_ascii=False, indent=2)
        report += "\n```\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": asdict(summary),
            "events": [asdict(event) for event in events],
            "tcpdump_filter": tcpdump_filter(summary),
        }
        if args.frame_hex:
            payload["frame_header"] = decode_proxy_frame_header(args.frame_hex)
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
