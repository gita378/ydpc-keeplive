#!/usr/bin/env python3
"""拦截 libChuanyunSDK 的 OAuth token 请求，提取 client_id/secret。
用法: 在终端中先运行官方客户端连接家庭云电脑，然后运行此脚本 attach 到进程。"""
import ctypes, os, struct, subprocess, sys

def find_pid():
    result = subprocess.check_output(['pgrep', '-f', '移动云电脑'], text=True).strip()
    pids = result.split('\n')
    for pid in pids:
        try:
            cmd = subprocess.check_output(['ps', '-p', pid, '-o', 'comm='], text=True).strip()
            if 'MacOS/移动云电脑' in cmd or '移动云电脑' in cmd:
                return int(pid)
        except:
            pass
    return None

# 方法: 直接从已运行的 dylib 内存中读取 clientID/clientSecret
# 通过加载同一个 dylib 到我们的进程中来读取
os.chdir('/Applications/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/lib')
os.environ['DYLD_LIBRARY_PATH'] = os.getcwd()

print("Loading libChuanyunSDK.dylib...")
lib = ctypes.CDLL('./libChuanyunSDK.dylib')

# 找 dylib 在内存中的 slide
libdyld = ctypes.CDLL(None)
cnt_fn = libdyld._dyld_image_count; cnt_fn.restype = ctypes.c_uint32
name_fn = libdyld._dyld_get_image_name; name_fn.restype = ctypes.c_char_p; name_fn.argtypes = [ctypes.c_uint32]
slide_fn = libdyld._dyld_get_image_vmaddr_slide; slide_fn.restype = ctypes.c_long; slide_fn.argtypes = [ctypes.c_uint32]

slide = 0
for i in range(cnt_fn()):
    n = name_fn(i)
    if n and b'libChuanyunSDK' in n:
        slide = slide_fn(i)
        break

print(f"Slide: 0x{slide:x}")

# 先调 init 来触发 clientID/clientSecret 的设置
# init callback
CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)
def dummy_callback(msg, a, b, c, d):
    pass

cb = CALLBACK(dummy_callback)
init_fn = lib.chuanyun_init
init_fn.argtypes = [ctypes.c_char_p, ctypes.c_int, CALLBACK, ctypes.c_char_p, ctypes.c_char_p]
init_fn.restype = ctypes.c_int

print("Calling chuanyun_init...")
try:
    ret = init_fn(b"api.soho.komect.com", 1443, cb, b"TEST-SN", b"Mac")
    print(f"init ret={ret}")
except Exception as e:
    print(f"init error: {e}")

import time
time.sleep(1)

# 读 clientID 和 clientSecret
# nm 地址 (从之前找到的):
# clientID accessor: 0x27260 (旧版) 或重新查
result = subprocess.check_output(['nm', './libChuanyunSDK.dylib'], text=True)
addrs = {}
for line in result.split('\n'):
    for key in ['8clientIDSSvau', '12clientSecretSSvau']:
        if key in line:
            parts = line.strip().split()
            addrs[key] = int(parts[0], 16)
            print(f"  {key} at 0x{addrs[key]:x}")

for label, key in [('clientID', '8clientIDSSvau'), ('clientSecret', '12clientSecretSSvau')]:
    if key not in addrs:
        print(f"{label}: symbol not found")
        continue
    fn_addr = slide + addrs[key]
    FUNC = ctypes.CFUNCTYPE(ctypes.c_void_p)
    fn = FUNC(fn_addr)
    ptr = fn()
    if not ptr:
        print(f"{label}: null")
        continue
    raw = bytes((ctypes.c_ubyte * 16).from_address(ptr))
    flags = raw[15]
    if flags & 0x80:
        length = flags & 0x0f
        val = raw[:length].decode('ascii', errors='replace')
        print(f'{label} = "{val}"')
    else:
        buf = struct.unpack('<Q', raw[0:8])[0]
        cnt = struct.unpack('<Q', raw[8:16])[0] & 0x0FFFFFFFFFFFF
        if buf and cnt < 500:
            val = ctypes.string_at(buf, cnt).decode('utf-8', errors='replace')
            print(f'{label} = "{val}"')
        else:
            print(f"{label}: buf=0x{buf:x} cnt={cnt}")
