#!/usr/bin/env python3
"""试多种 Basic-Auth 凭证组合 + CONNECT 目标格式，看哪个响应不是 404
（先用 cloudpc_protocol 拿 firmAuth，然后枚举 N 种格式）
"""
import os, sys, base64, socket, ssl, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloudpc_protocol import CloudPcClient

def try_connect(cag_ip, cag_port, dest_host, dest_port, b64_creds, label):
    raw = socket.create_connection((cag_ip, cag_port), timeout=8)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["http/1.1"])
    sock = ctx.wrap_socket(raw, server_hostname=cag_ip)
    # ★ 实际官方走的是 GLib g_http_proxy_connect 的格式（HTTP/1.0 + User-Agent: GLib/x.y）
    headers = (f"CONNECT {dest_host}:{dest_port} HTTP/1.0\r\n"
               f"Host: {dest_host}:{dest_port}\r\n"
               f"Proxy-Connection: keep-alive\r\n"
               f"User-Agent: GLib/2.71\r\n"
               f"Proxy-Authorization: Basic {b64_creds}\r\n\r\n").encode()
    sock.sendall(headers)
    sock.settimeout(5)
    resp = b""
    try:
        while b"\r\n\r\n" not in resp:
            chunk = sock.recv(4096)
            if not chunk: break
            resp += chunk
    except Exception as e:
        resp += f"<exc:{e}>".encode()
    sock.close()
    head = resp.split(b"\r\n\r\n", 1)[0].decode("utf-8", errors="replace")
    status = head.split("\r\n", 1)[0]
    print(f"[{label:>30s}] dest={dest_host}:{dest_port:<5} → {status}")
    return status

def b64(s): return base64.b64encode(s.encode()).decode()

c = CloudPcClient()
c.bootstrap_public_key()
c.login_pwd(os.environ["UN"], os.environ["PW"])
vms = c.list_cloud_pcs()
auth = c.get_firm_auth(vms[0]["userServiceId"])

vu = auth["vmUserName"]
vp = auth["vmPassword"]
vi = auth["vmId"]
ci = auth["cagIp"]
cp = auth["cagPort"]
mi = auth["vmcIp"]
mp = auth["vmcPort"]
bc = auth["bizCode"]
uu = auth["uuid"]
ui = c.store.userId
print(f"\nvm={vu} vp={vp[:8]}... vmId={vi}\n")

# 组合矩阵：(creds_plaintext, dest_host)
trials = [
    # 凭证不同变体，目标用 vmcIp
    (f"{vu}:{vp}",                                  mi, mp, "user:pwd"),
    (f"{vi}:{vp}",                                  mi, mp, "vmId:pwd"),
    (f"{vu}",                                       mi, mp, "user only"),
    (f":{vp}",                                      mi, mp, ":pwd"),
    (f"{vi}",                                       mi, mp, "vmId only"),
    (f"{vi}:{vu}:{vp}",                             mi, mp, "vmId:user:pwd"),
    (f"{vu}:{vi}:{vp}",                             mi, mp, "user:vmId:pwd"),
    (f"{vu}:{vp}:{vi}",                             mi, mp, "user:pwd:vmId"),
    (f"{ui}:{vp}",                                  mi, mp, "userId:pwd"),
    (f"{vi}:{bc}",                                  mi, mp, "vmId:bizCode"),
    (f"{uu}:{vp}",                                  mi, mp, "uuid:pwd"),
    # 目标用 vmId 而非 vmcIp
    (f"{vu}:{vp}",                                  vi, mp, "user:pwd → vmId"),
    (f"{vi}:{vp}",                                  vi, mp, "vmId:pwd → vmId"),
]

for plain, host, port, label in trials:
    try:
        try_connect(ci, cp, host, port, b64(plain), label)
    except Exception as e:
        print(f"[{label:>30s}] dest={host}:{port:<5} → ERR {e}")
    time.sleep(0.5)
