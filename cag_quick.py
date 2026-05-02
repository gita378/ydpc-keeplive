#!/usr/bin/env python3
"""getFirmAuth 后立刻试 CAG，看凭证有没有时效"""
import os, sys, base64, socket, ssl, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloudpc_protocol import CloudPcClient

c = CloudPcClient()
c.bootstrap_public_key()
c.login_pwd(os.environ["UN"], os.environ["PW"])
vms = c.list_cloud_pcs()
usid = vms[0]["userServiceId"]

# 先调 connectableCheck
try:
    chk = c.connectable_check(usid)
    print("connectableCheck:", chk.get("code"), chk.get("msg"))
except Exception as e:
    print("connectableCheck err:", e)

# 立刻 firmAuth → 立刻 CAG
auth = c.get_firm_auth(usid)
t0 = time.time()
print(f"\nfirmAuth: vm={auth['vmUserName']} vmcIp={auth['vmcIp']}:{auth['vmcPort']}")
print(f"  cagIp={auth['cagIp']}:{auth['cagPort']} scAuthCode_len={len(auth.get('scAuthCode',''))}")

# 立刻发心跳让平台层知道我们在线
hb = c.heartbeat(usid)
print(f"heartbeat: code={hb.get('code')} msg={hb.get('msg')}")

# CAG TLS + CONNECT
def cag_connect(headers_str, label, with_sni=False):
    raw = socket.create_connection((auth["cagIp"], auth["cagPort"]), timeout=8)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["http/1.1"])
    # 抓包显示官方客户端不带 SNI 扩展
    sock = ctx.wrap_socket(raw, server_hostname=(auth["cagIp"] if with_sni else None))
    sock.sendall(headers_str.encode())
    sock.settimeout(5)
    resp = b""
    try:
        while b"\r\n\r\n" not in resp:
            chunk = sock.recv(4096)
            if not chunk: break
            resp += chunk
    except: pass
    sock.close()
    head = resp.split(b"\r\n\r\n",1)[0].decode("utf-8","replace")
    print(f"\n[{label}]")
    print(head)
    return head

vu, vp = auth["vmUserName"], auth["vmPassword"]
mi, mp = auth["vmcIp"], auth["vmcPort"]
b64 = base64.b64encode(f"{vu}:{vp}".encode()).decode()

# 试 4 种 HTTP 方言
templates = [
    ("HTTP/1.0 + GLib UA",
     f"CONNECT {mi}:{mp} HTTP/1.0\r\nHost: {mi}:{mp}\r\nProxy-Connection: keep-alive\r\nUser-Agent: GLib/2.71\r\nProxy-Authorization: Basic {b64}\r\n\r\n"),
    ("HTTP/1.1 short (libcag style)",
     f"CONNECT {mi}:{mp} HTTP/1.1\r\nHost: {mi}:{mp}\r\nProxy-Connection: keep-alive\r\nProxy-Authorization: Basic {b64}\r\n\r\n"),
    ("HTTP/1.0 minimal",
     f"CONNECT {mi}:{mp} HTTP/1.0\r\nProxy-Authorization: Basic {b64}\r\n\r\n"),
    ("HTTP/1.1 with full auth",
     f"CONNECT {mi}:{mp} HTTP/1.1\r\nHost: {mi}:{mp}\r\nUser-Agent: USmartView_VDI_Client\r\nProxy-Authorization: Basic {b64}\r\n\r\n"),
]
for label, hdrs in templates:
    elapsed = time.time() - t0
    cag_connect(hdrs, f"{label}  (t+{elapsed:.1f}s)")
    time.sleep(0.5)
