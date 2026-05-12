# 移动云电脑 ZTE 分支 — 完整协议逆向文档

> 日期: 2026-05-02 (最后更新)
> 账号: zhaoboy / zhaoboy2 / zhaoboy3 (spuCode=zte-cloud-pc)
> 目标: 协议级保活（防休眠）+ CSAP startDesktop 桌面画面获取
> 方法: Electron asar 解包 + IDA 反编译 + tcpdump 抓包 + cag.log/client.log 日志分析

---

## 一、总结

移动云电脑 ZTE 分支的完整连接链路是 **6 层协议栈**：

```
Layer 6  SPICE 协议 (main/display/inputs/cursor/playback/record)
Layer 5  CAG Tunnel 多路复用 (send_tunnel_add_link, 4B ProxyProtocolHeader)
Layer 4  TLS 1.3 (over KCP/UDT)
Layer 3  KCP/UDT (可靠 UDP 传输, IKCP_CONV_AUTH + SYNACK)
Layer 2  UDP (cagIp:8899, dest IPv6:60065)
Layer 1  TCP (仅控制面: ZTEC 连通性测试 + SOHO HTTP API)
```

保活的关键触发点是 **SPICE DISPLAY_INIT**（Layer 6），但它必须在 Layer 2-5 全部建立之后才能发送。

---

## 二、分支判定

### 2.1 三个厂商分支

| spuCode 前缀 | 厂商 | native 进程 | 传输协议 |
|---|---|---|---|
| `zte-*` | 中兴 | uSmartView_VDI_Client | KCP/UDT + TLS + CAG Tunnel |
| `wave-*` | 浪潮 | CloudPC.exe (仅Win) | 浪潮私有 |
| 其他 | 自研穿云 | 移动云电脑(jwae) | ChuanyunHead + SCG + NxTCP |

### 2.2 分流代码 (src/main/index.js:549)

```js
if (options.spuCode.includes('wave-'))  → inspurConnect()
if (options.spuCode.includes('zte-'))   → zteWorker.connect()  // ★ 本账号
else                                    → runWorker.connect()
```

### 2.3 确认依据（6 重证据）

1. getFirmAuth 返回 `spuCode = "zte-cloud-pc"`
2. JS 源码 `includes('zte-')` 分流
3. 运行时 `ps aux` 只看到 `uSmartView_VDI_Client` 进程
4. 抓包目标 36.133.100.80:8899 + 响应 `Proxy-agent: CAG2.0`
5. 手动启动自研 native → `jwae_start()=-4` 失败（scgIp/scAuthCode 为空）
6. cag.log 记录完整 ZTEC 鉴权流程

---

## 三、Layer 1 — HTTP 控制面 ✅ 已完全还原

### 3.1 签名算法

```
HMAC-SHA256(
  key  = bytes.fromhex(APP_SECRET),
  data = "{METHOD}&{path}&{X-SOHO-AppKey=v&...排序固定...}" 
       + ("&body={encrypted_b64}" if body else "")
)
```

- APP_KEY = `ef80482854c2a2a36311a46011f3303f144bdf69b4b4223cf916f4c7f0f55135`
- APP_SECRET = `cd58cf413dc43b07993f82f532b0f8e83d259d3ae2305de76811ccd1303853f7`
- Header 拼接顺序固定（不是字母序），空值跳过
- **selftest 通过**：与真实 curl 样本字节级一致

### 3.2 Body 加密

```
RSA-1024 NoPadding, 117B 分块, 左 0 填充到 128B
密码字段用独立的 /login/publicKey/v1 返回的公钥（不是 body 加密公钥）
```

### 3.3 接口列表（全部实测通过）

```
POST /login/encryptKey/v1         启动公钥
POST /system/settings/v1          系统配置
POST /login/publicKey/v1          登录公钥
POST /login/namePwdLogin/v1       主账号密码登录
POST /cc/cloudPc/list/v6          云电脑列表 (含 remainDurationTime)
POST /cc/getFirmAuth/v1           厂商连接凭证
POST /cc/cloudPc/heartbeat/v2     心跳 (30s)
POST /cc/cloudPc/infoReport/v2    设备信息上报
POST /cc/cloudPc/logout/v2        断连通知
POST /token/checkToken/v1         Token 校验
```

### 3.4 getFirmAuth 返回值

```json
{
  "spuCode": "zte-cloud-pc",
  "vmUserName": "42569521fb5974a3",
  "vmPassword": "{guid}{userId}",
  "vmId": "{guid}",
  "vmcIp": "10.21.2.232", "vmcPort": 8443,
  "cagIp": "36.133.100.80", "cagIpv6": "2409:8c70:3a50:2085::25c",
  "cagPort": 8899,
  "scgIp": "", "scgTcpPort": 0, "scAuthCode": "",
  "bizCode": "10002"
}
```

### 3.5 保活验证指标

```
remainDurationTime (在 /cc/cloudPc/list/v6 返回)
- 云电脑运行中: 每 30s 减 1
- 云电脑休眠: 停止减少
- 观察 2 次间隔 35s 的值差即可判断保活是否有效
```

### 3.6 Python 实现

**文件: `cloudpc_protocol.py`** — 完整可运行
```bash
python3 cloudpc_protocol.py --username "$UN" --password "$PW"
# 输出: bootstrap → login → list → getFirmAuth → 完整连接参数
python3 cloudpc_protocol.py --selftest
# 输出: ✓ PASS (签名验证)
```

---

## 四、Layer 1 — ZTEC 连通性测试 ✅ 已完全还原

### 4.1 角色

ZTEC 鉴权是 **前置连通性测试**，不是 SPICE 数据面承载通道。
cag.log 确认: ZTEC 200 OK 后立刻 `notify_quit` 关闭。

### 4.2 三阶段协议

```
TCP → cagIp:8899 (明文, 不经 TLS)

Stage 1: 客户端 → 服务端 (50 bytes)
  [0:6]   "ZTEC,\0"  magic
  [6:10]  auth_type + 100  (RADIUS=101)
  [10:14] client_key = random u32
  [14:18] data_len = 220 (RADIUS)
  [18:34] vmId[:16] (16B key material)
  [34:46] reserved = 0
  [46:50] flags = 0x03

Stage 2: 服务端 → 客户端 (50 bytes)
  [10:14] server_key
  [46:50] flags → aes_flag
          bit0: 0=AES-128, 1=AES-256
          bit1: 0=ECB, 1=CBC
          官方实测: aes_flag=258 (0x102=AES-256-CBC)

Stage 3: 客户端 → 服务端 (RADIUS=220 bytes)
  [0:2]   cag_port
  [4:20]  cag_ip (IPv4 BE + 12B padding)
  [20:60] 40B extra (通常为空)
  [60:124] AES(username, 64B)
  [124:188] AES(XOR(password, 99), 64B)  ← RADIUS 模式密码先 XOR 99
  [188:190] flags

Response: 36 bytes
  [0:4] code = 200 (success)
  [4:36] zeros

→ 200 OK 后立刻关闭 TCP
```

### 4.3 AES Key 派生

```python
mixed_client = client_key & 0xABACACAB
mixed_server = server_key | 0x98979798
key_str = f"{client_key:08x}{server_key:08x}" + 8 bytes hex from mixed values
# AES-128: key = key_str[:16].encode('ascii')
# AES-256: key = key_str[:32].encode('ascii')
```

### 4.4 Python 实现

**文件: `cloudpc_keepalive.py`** — ZTEC 部分已实测 200 OK

---

## 五、Layer 2-5 — 数据面 ★ 核心发现

### 5.1 真实连接架构 (来自 client.log 22:03 成功日志)

```
uSmartView_VDI_Client 内部:
  ┌──────────────────────────────────────────────────────────┐
  │ SPICE channels (main/display/inputs/cursor/play/record)  │
  │    ↕ socketpair (127.0.0.1:<local> ↔ 127.0.0.1:<peer>)  │
  │ proxy thread                                             │
  │    ↕ KCP/UDT session                                     │
  │    ↕ TLS 1.3 (over KCP)                                  │
  │    ↕ UDP → cagIp:8899 → [IPv6]:60065                    │
  │    ↕ send_tunnel_add_link (CAG Tunnel 虚拟通道注册)       │
  └──────────────────────────────────────────────────────────┘
```

### 5.2 日志证据链 (client.log 时序)

```
22:03:19.294  initRedirectParams: port[5100] s_proxy_port[60065] proxy_type[ice]
22:03:19.309  session_connect before m_pHost[], m_pPort[5100]
22:03:19.411  spice_session_connect: g_udt_thread_run: 0
22:03:19.413  session_connect after m_pHost[2409:8c70:3a50:22eb::535], m_pPort[5100]
22:03:19.415  main-1:0: socket connect to 127.0.0.1:52578 ← 本地 socketpair!
22:03:19.415  [PROXY] Setting up spice proxy link with SSL=1
22:03:19.416  [SSL] Initializing SSL context for SPICE proxy
22:03:19.418  init SSL CTX for udt ok
22:03:19.418  client is support quic:0 ... be_ssl:1 kcp->be_ssl:1
22:03:19.457  kcp(syn_id=0x3ffd2849, conv=0xb200b5d5) be_ssl=1
22:03:19.475  SSL_connect ... TLS1.3(0x304) ... udt ssl connect success
22:03:19.475  send_tunnel_add_link: dest [IPv6]:60065, ch_type 1 → vch_id 1
22:03:19.475  spice_channel_send_link main-1:0
22:03:19.489  spice_channel_recv_link_hdr main-1:0
22:03:19.521  session needs 6 channels total
22:03:19.535  spice_channel_send_link playback-5:0
22:03:19.588  all channel 6/6 connect success ✅
```

### 5.3 关键参数（不在 getFirmAuth 里！来自共享内存连接字符串）

| 参数 | 值 | 来源 |
|------|-----|------|
| SPICE host | `2409:8c70:3a50:22eb::535` (IPv6) | 连接字符串 |
| SPICE port | 5100 | 连接字符串 |
| CAG proxy port | 60065 | 连接字符串 (s_proxy_port) |
| proxy_type | ice (ICE 协议) | 连接字符串 |
| 传输 | KCP/UDT + TLS 1.3 | 硬编码 |
| QUIC | 0 (未启用) | 配置 |

### 5.4 ProxyProtocolHeader (CAG Tunnel 帧头, 4 bytes)

```
[0] u8  cmd
      0x0A (10)  = DATA      (SPICE 数据帧)
      0x1A (26)  = ADD_LINK  (注册虚拟通道, payload=154B)
      0x2A (42)  = CLOSE     (关闭通道)
      0x3A (58)  = VM_INFO   (VM 信息确认)
      所有 cmd 的低 4 位都是 0xA (check_proxy_header 校验)
[1] u8  link_id   (虚拟通道 ID)
[2] u16 data_len  (payload 长度, LE)
```

### 5.5 ADD_LINK payload (154 bytes, channel_link_info_ex)

```
[0:2]    u16  Port
[2]      u8   Priority
[3]      u8   LinkType (0=SPICE, 其他=outband)
[4:77]   dest IP + routing info
[77]     u8   Protocol
[78]     u8   Emergency flag
[79:81]  u16  BW (KB/s)
[81:83]  u16  TotalBW (KB/s)
[83]     u8   QoS
[84:88]  u32  ChannelType (1=main 2=display 3=inputs 4=cursor 5=playback 6=record 12=outband)
[88:104] u32[4] Extend
[104:154] reserved
```

### 5.6 KCP 会话建立 (从 client.log)

```
deal_kcp_auth_cmd: recv IKCP_CONV_AUTH_HEAD_ACK from cagIp:8899
deal_kcp_auth_cmd: recv IKCP_CONV_AUTH_ACK from cagIp:8899
deal_kcp_sync_ack_cmd: recv IKCP_CONV_SYNACK from cagIp:8899
deal_kcp_sync_ack_cmd: be_quic=0 be_using_stream=0 be_ssl=1
deal_udt_ssl_connect: SSL_connect TLS1.3(0x304) success
```

---

## 六、Native 层 IDA 反编译总结

### 6.1 chuanyunsdk_zte.node (78 KB)

```
N-API 跳板
JS runWorker.runSimpleAsyncWorker('connect', vmUserName, ..., cagPort, cb)
  → dlopen("libvdconn.dylib") + dlsym("connectDesktop")
  → connectDesktop(vmUserName, vmPassword, vmId, vmcIp, vmcPort, cagIp, cagPort, cb)
```

### 6.2 libvdconn.dylib (3.5 MB)

```
connectDesktop @ 0x1cc560
  → 分离线程 SohoSdk_DoConnectDesktop
    → LoginManager::SohoSdk_connectDesktop
      → ClientManager::SohoSdk_StartConnectDesktop
        → AddCagAndInternalParm + AddPwdAndNameParm + AddVmcIpAndPort
        → ConnectStrAesEncode (6 位数字 key, 有效熵 19.9 bit)
        → ConnectStrWriteShareMemory (共享内存: [nRandom u32][cipher_len u32][cipher])
        → StartSpiceProcess: fork + exec ./uSmartView_VDI_Client --vmid tempvmidXXX
```

### 6.3 libcag.dylib (72 KB)

```
connect_to_access_gateway @ 0x5680: ZTEC 3 阶段 (连通性测试)
tn_deal_aes_code @ 0x6e90: AES key 派生 (client_key & 0xABACACAB / server_key | 0x98979798)
generate_http_msg @ 0x5fc0: HTTP CONNECT 格式 (仅测试路径, 非生产)
create_http_tunnel_proxy @ 0x61b0: HTTP CONNECT 执行 (仅测试)
```

### 6.4 uSmartView_VDI_Client (48 MB, x86_64 Rosetta 2)

```
spice-gtk fork + Qt
SPICE 函数: spice_inputs_button_press / key_press 等
CAG 属性: ag-ip / ag-port / ag-intraip
proxy thread: KCP/UDT + TLS 1.3
tunnel: send_tunnel_add_link / send_tunnel_delete_link
ProxyProtocolHeader: 4B 帧头 (cmd + link_id + data_len)
```

---

## 七、与自研分支 (jwae+SCG) 的完整对比

| 维度 | 自研 (jwae) | ZTE (CAG) |
|------|------------|-----------|
| native 核心 | jwae.framework (Rust, 36MB) | libvdconn + libcag (C++, 3.5MB) |
| 网关 | SCG:10800 | CAG:8899 |
| 前置鉴权 | AES-128-CTR (硬编码 key/IV) | ZTEC 3 阶段 (key 派生) |
| 传输 | TCP + ChuanyunHead 24B 帧 | UDP + KCP/UDT + TLS 1.3 |
| 多路复用帧 | ChuanyunHead 24B | ProxyProtocolHeader 4B |
| 身份令牌 | scAuthCode (JWT ~400 chars) | vmUserName + vmPassword |
| SPICE 入口 | 127.0.0.1:10800 (jwae 代理) | 127.0.0.1:socketpair (proxy thread) |
| 保活关键 | DISPLAY_INIT | DISPLAY_INIT (相同) |

---

## 八、保活实现路线

### 8.1 已完成 ✅

| 组件 | 文件 | 状态 |
|------|------|------|
| SOHO HTTP 控制面 | cloudpc_protocol.py | ✅ 签名 selftest + 实测全通 |
| ZTEC 连通性测试 | cloudpc_keepalive.py | ✅ 200 OK |
| SOHO heartbeat 循环 | cloudpc_keepalive.py | ✅ 30s 间隔 |

### 8.2 待实现 🔧

| 组件 | 复杂度 | 说明 |
|------|--------|------|
| KCP 会话 (AUTH + SYNACK) | 高 | Python `kcp` 库可用 (pip install kcp) |
| UDT over KCP | 中 | 可靠 UDP 传输 |
| TLS 1.3 over KCP/UDT | 中 | ssl.wrap_socket 但底层是 KCP 不是 TCP |
| CAG Tunnel add_link | 低 | 4B header + 154B payload, 格式已知 |
| SPICE REDQ 握手 | 低 | 标准协议, 代码已写好 |
| SPICE DISPLAY_INIT | 低 | 14B payload, 保活触发点 |

### 8.3 验证指标

```python
# 每 35s 刷一次 list/v6, 看 remainDurationTime 是否减少
vms = client.list_cloud_pcs()
print(vms[0]["remainDurationTime"])  # 减少 = 云电脑在跑 = 保活成功
```

---

## 九、动态分析限制记录

| 工具 | 结果 | 原因 |
|------|------|------|
| frida attach | ❌ unable to read process memory | x86_64 Rosetta 2 进程, ARM64 frida 不兼容 |
| dtrace | ❌ cannot instrument translated processes | 同上 |
| DYLD_INSERT_LIBRARIES | ⚠️ hook 加载但 SSL_write 未触发 | Rosetta 下 symbol interposition 不工作 |
| lldb process save-core | ⚠️ 精简 core 缺 heap | 需 --style full |
| gcore | ⚠️ 13GB 但搜不到字符串 | 部分内存页不可读 |
| tcpdump | ✅ 抓到 TLS 流量 | 但无法解密 |
| **cag.log** | ✅ 完整 ZTEC 协议日志 | 官方自带日志！ |
| **client.log** | ✅ 完整 SPICE/KCP/tunnel 日志 | 官方自带日志！最终突破口 |

**最终方案**: 直接读官方日志 (`cag.log` + `client.log`) 获得全部协议信息，不需要动态 hook。

---

## 十、文件清单

```
/Users/zxc/Desktop/移动云电脑/
├── ZTE_PROTOCOL_FINAL.md        ← 本文件 (完整协议文档)
├── ANALYSIS.md                   ← 早期分析报告 (已被本文取代)
├── cloudpc_protocol.py           ← SOHO HTTP 控制面 Python 实现 ✅
├── cloudpc_keepalive.py          ← 保活客户端 (ZTEC + tunnel, 进行中)
├── cag_auth_probe.py             ← CAG 凭证枚举测试工具
├── cag_quick.py                  ← CAG 快速连接测试
├── ida_targets/                  ← IDA 反编译目标
│   ├── P0_chuanyunsdk_zte.node
│   ├── P0_libvdconn.dylib
│   ├── P1_libcag.dylib
│   └── P1_uSmartView_VDI_Client
├── cloudpc_extract/              ← asar 解包 (JS 源码 + native)
├── cloudpc_analysis/             ← 早期自动分析报告
└── 移动云电脑.app/               ← 官方客户端
    └── .../uSmartView_VDI_Client.app/Contents/log/
        ├── cag.log               ← ZTEC 鉴权日志 (关键!)
        ├── client.log            ← SPICE/KCP/tunnel 日志 (关键!)
        └── vdconn.log            ← libvdconn 日志
```

---

## 十一、保活实测结论

### 11.1 验证结果

| 账号 | 套餐 | 跑脚本 | 结果 |
|------|------|--------|------|
| zhaoboy | 包月 (remain=None) | 一整夜 | **没关机** ✅ |
| zhaoboy | 包月 | 脚本停后 | 关机了 ❌ (A/B对照) |
| zhaoboy3 | 按时长 (remain=70982) | 1小时+ | **没关机** ✅ |
| zhaoboy2 | 3台云电脑 | 单次测试 | 3台全部 ZTEC=200 ✅ |

### 11.2 结论

**`cloudpc_keepalive_multi.py` 是最终方案。** 只需 ZTEC 鉴权 + SOHO heartbeat，不需要 KCP/SPICE/DISPLAY_INIT。

cron 配置：
```
*/10 * * * * /usr/bin/python3 /path/cloudpc_keepalive_multi.py >> /path/keepalive.log 2>&1
```

---

## 十二、CSAP startDesktop 1000100 问题（未解决）

### 12.1 问题描述

CSAP `cs_startDesktop.action` 返回 `1000100 用户会话已失效`。
阻止获取 fresh `session-key`，无法完成 SPICE DISPLAY_INIT。

**不影响保活**（保活已用更简方案解决）。只影响"桌面画面获取"功能。

### 12.2 已排除的原因

| 排查项 | 结果 |
|--------|------|
| ZTEC 鉴权是前置条件 | ❌ 先 ZTEC 200 OK 再 CSAP 仍 1000100 |
| Cookie/JSESSIONID 管理 | ❌ requests.Session 正确保存/发送 |
| serialNum 不一致 | ❌ 用官方固定值仍 1000100 |
| body 字段差异 | ❌ 加密前 JSON 完全一致 |
| AES 加密不一致 | ❌ 加密后 hex 前缀与官方一致 |
| 官方客户端在线/离线 | ❌ 都是 1000100 |
| 账号/VM 选错 | ❌ vmId 匹配已验证 |
| HTTP 客户端 | ❌ 系统 curl 发同一 body 仍 1000100 |

### 12.3 调用链状态

```
cs_sysConfig.action          ✅ OK
cs_getToken.action           ✅ OK (返回 accessToken)
cs_getDesktopList.action     ✅ OK (返回 desktop 列表)
cs_startDesktop.action       ❌ 1000100
```

### 12.4 最大嫌疑：CAG 负载均衡

每次响应返回不同 JSESSIONID（后端实例轮换）：
```
sysConfig      → JSESSIONID=8C63...
getToken       → JSESSIONID=04F9...
getDesktopList → JSESSIONID=2960...
startDesktop   → JSESSIONID=0D35...
```

accessToken 可能绑定了 getToken 时的后端实例。startDesktop 被路由到另一个实例 → session 不存在 → 1000100。

### 12.5 下一步方向

1. 对比 Python 和官方 libcurl 的 TCP 连接复用行为
2. IDA 查 `libvdconn::SendHttpRequest` 是否有 sticky session header
3. 查 CAG `X-CCT-MS` 响应 header 含义
4. 尝试强制 TCP 连接复用确保命中同一后端

---

## 十三、云电脑开机流程（2026-05-05 实测确认）

### 13.1 完整时序（从日志还原）

```
用户点"连接"一台已关机的云电脑 (vmStatus=23)

16:37:49  Electron:
          ├── getFirmAuth(userServiceId)         ← ★ 通知平台"用户要连接"，触发后端开机调度
          │   返回 vmUserName/vmPassword/vmcIp/cagIp/cagPort
          │
          └── connectWorker(d.data)              ← 传给 native SDK

16:37:49  native SDK (libvdconn → uSmartView_VDI_Client):
          ├── ZTEC 连通性测试 → 200 OK → close
          ├── CSAP cs_sysConfig.action            ← 系统配置
          ├── CSAP cs_getToken.action             ← 拿 accessToken
          ├── CSAP cs_getDesktopList.action       ← 拿 desktop UUID
          └── CSAP cs_startDesktop.action         ← ★ result:0 触发 VM 开机

16:37:54  轮询等待 VM 就绪:
          ├── cs_startDesktop_async_query  (每 2s)
          ├── cs_startDesktop_async_query
          ├── cs_startDesktop_async_query
          ├── ...
16:38:05  └── cs_startDesktop_async_query  ← 拿到 connectStr (含 session-key/IPv6/port)

16:38:05  KCP/UDT/TLS + SPICE 连接建立
          └── all channel 6/6 connect success

~30s 后  list/v6 查询: vmStatus=1 (运行中)
```

### 13.2 关键发现

1. **`getFirmAuth` 是开机的触发点** — 调用后 ~30s VM 从已关机变运行中
2. **`cs_startDesktop.action` 是 CSAP 层的开机命令** — 官方 result:0 成功
3. **轮询 `async_query` 约 16 秒** — 等 VM 内部初始化完成返回 connectStr
4. **保活脚本有效的根本原因**: 每次 `getFirmAuth` 调用 = 通知平台"用户要连接" = 重置 30 分钟关机倒计时

### 13.3 保活为什么不需要 KCP/SPICE

```
保活脚本做的:                    平台判定:
getFirmAuth ──────────────────→ "用户请求连接" → 重置 30 分钟倒计时
heartbeat   ──────────────────→ "客户端在线"
ZTEC 200 OK ──────────────────→ "CAG 可达"

不需要做的:
cs_startDesktop               → 只在开机时需要
KCP/UDT/TLS/SPICE             → 只在显示桌面画面时需要
DISPLAY_INIT                  → 只在需要 Surface 创建时需要
```

### 13.4 Python 开机实现方向

如果需要 Python 远程开机（不连桌面）：
```python
# 1. SOHO 登录
client = soho_login(username, password)
# 2. 列出云电脑
vms = client.list_cloud_pcs()
# 3. getFirmAuth 触发开机
auth = client.get_firm_auth(vm["userServiceId"])
# 4. 等待 30s 后查询状态
time.sleep(30)
vms = client.list_cloud_pcs()
# vm["vmStatusShow"] 应该变成 "运行中"
```

注意：`getFirmAuth` 对已运行的 VM 也能调（返回连接参数），不会重启它。

---

## 十四、CSAP startDesktop 1000100 深度分析（2026-05-05）

### 14.1 官方成功 vs Python 失败对比

**官方成功的 CSAP 序列（vdconn.log 16:52）：**

```
16:52:01.917  cs_sysConfig.action     → 200 OK (X-CCT-MS: 59 11)
16:52:02.077  cs_getToken.action      → 200 OK (X-CCT-MS: 57 6)
16:52:02.162  cs_getDesktopList.action → 200 OK (X-CCT-MS: 37 8)
16:52:02.312  cs_startDesktop.action  → 200 OK (无 X-CCT-MS!)  ← ★ 成功
16:52:07.412  async_query × N (每 2s)  → 200 OK
16:52:26.654  拿到 connectStr          → VM 就绪
16:52:27.968  "Success to Connectting desktop"
16:52:30.351  "Success to Connect desktop"
```

**Python 失败：**
```
sysConfig     → 200 OK ✅
getToken      → 200 OK ✅  
getDesktopList→ 200 OK ✅
startDesktop  → 1000100 "用户会话已失效" ❌
```

### 14.2 已确认一致的部分

| 项目 | 官方 | Python |
|------|------|--------|
| Header: Content-Type | application/xml | application/xml ✅ |
| Header: X-Ap-sHost | 10.21.2.232:8443 | 10.21.2.232:8443 ✅ |
| Header: process_id | 2 | 2 ✅ |
| Header: serialNum | 0001a305-...(固定) | 我们也用固定值 ✅ |
| JSESSIONID | 每次响应都换(B204→4325→2C1B→7935) | 每次也换(正常) ✅ |
| Connection | keep-alive(所有响应) | keep-alive ✅ |
| body 加密 | ZTE_Security_Params AES | 相同算法 ✅ |
| body JSON 字段 | 28 个字段 | 28 个字段相同 ✅ |

### 14.3 关键差异

1. **`X-CCT-MS` header 在 startDesktop 响应里消失** — sysConfig/getToken/getDesktopList 都有（格式 `{total_ms} {inner_ms}`），但 startDesktop 没有。说明 startDesktop 被 CAG/IAG 网关不同层处理。

2. **Thread ID 固定 `0x30d2dd000`** — 官方所有 CSAP 请求在同一个 libcurl thread 上，保证同一条 TCP + TLS 连接。Python requests.Session 理论上也复用，但无法保证 100% 同一条底层 TCP。

3. **`otlp_trace_id` 全程不变** — 官方保持 `a6f1d665c52b37706ae69999acf0d58d`。Python 每个请求生成新 trace_id。**可能 CAG 用 trace_id 做 session 路由。**

### 14.4 最可能的根因

**`otlp_trace_id` 是 CAG session 路由的 key。**

官方：所有请求用同一个 `otlp_trace_id` → CAG 识别为同一个 session → 路由到同一个后端实例 → startDesktop 能找到 getToken 时创建的 session → 成功。

Python：每个请求生成新的 `otlp_trace_id` → CAG 认为是不同 session → 路由到随机后端 → startDesktop 找不到 session → 1000100。

### 14.5 修复方向

在 `cloudpc_ztec_client.py` 的 `ZteCsapClient.__init__` 中，`self.trace_id` 已经是固定的（`os.urandom(16).hex()`），**在同一个 client 实例内不变**。但需要确认：
1. `otlp_trace_id` header 是否在所有请求中正确传递（检查 `_headers()` 方法）
2. `otlp_parent_id` 是否每次请求正确更新（官方每次不同）
3. 是否还有其他 session 绑定因素（如 TLS session ticket、TCP 连接 ID）

### 14.6 开机的完整 API 链路

```
Electron 层:
  1. list/v6 → 看到 vmStatus=23 (已关机)
  2. 用户点"连接"
  3. getFirmAuth(userServiceId) → 拿 vmUserName/vmPassword/cagIp
  4. connectWorker(d.data) → 传给 native SDK

native SDK (libvdconn):
  5. InitLogAndSocket → 初始化
  6. connectDesktop(vmId) → 开始连接
  7. SetClientSysInfoForGetToken → 设客户端信息
  
CSAP 序列 (via CAG HTTPS):
  8. cs_sysConfig.action → 系统配置
  9. cs_getToken.action → 拿 accessToken
  10. cs_getDesktopList.action → 拿 desktop UUID
  11. cs_startDesktop.action → ★ 触发 VM 开机
  12. cs_startDesktop_async_query × N → 每 2s 轮询等 VM 就绪
      → 拿到 connectStr (含 session-key/IPv6/port)

连接建立:
  13. ZTEC 连通性测试 → 200 OK → close
  14. KCP/UDT + TLS 1.3
  15. tunnel add_link
  16. SPICE 6/6 channels success
  17. 桌面画面显示
```

## 十五、startDesktop 1000100 修复（2026-05-05 已解决）

### 根因

`cs_startDesktop.action` 的参数必须放在 **query string** 中，body 发加密空字符串。
之前错误地把 28 个参数放在加密 body 里、query 为空。

IAG 网关行为：
- 无 query string → IAG 直接拒绝 (1000100 未加密)
- `?RspSecurity=1` 无 accessToken → VMC 返回 1000100 (加密)
- `?accessToken=xxx&RspSecurity=1` + 参数在 body → VMC 返回 7010001
- `?accessToken=xxx&uuid=...&vmid=...&所有参数&RspSecurity=1` + 空 body → ✅ 成功

### 正确的请求格式

```
POST /cs/cs_startDesktop.action?accessToken=xxx&uuid=yyy&vmid=zzz&type=1&connectionType=0
    &assignRelationtoString=47031,-1,63&version=V7.25.22&language=zh&requestFrom=9
    &isvm=0&encryption=1&prover=1&supportAsync=1&allowSwitchRap=1&raptype=2&netType=2
    &SNcode=xxx&hostName=xxx&localipandmac=ip,mac&diskNo=xxx
    &newpara=1&newcharsetparse=1&upmnew=1&watermarkType=1
    &allowExtUSBPolicy=1&verifyTerminalBind=11
    &supportCustomConfig=00000000000000000000000000000011&RspSecurity=1

Headers: Content-Type: application/xml
         X-Ap-sHost: {vmc_host}:{vmc_port}
         process_id: 2
         serialNum: {uuid}
         otlp_trace_id: {fixed_hex32}
         otlp_parent_id: {per_request_hex16}

Body: AES-CBC(PKCS7(""), uas_key, uas_iv).hex().upper()
```

### 结论

CSAP 的 4 个 action 统一模式：所有业务参数在 query string，body 只传加密的辅助 JSON（getToken 传 {clienttype,hardware,nettype,ostype}）或加密空字符串。startDesktop 不需要 body 参数。

## 十六、家庭云电脑 SC 协议逆向（2026-05-11）

### 16.1 产品区分

| 产品 | spuCode | 连接方式 | 保活 | 开机 |
|------|---------|---------|------|------|
| ZTE 云电脑 | `zte-cloud-pc` | CAG → ZTEC → KCP/UDT → SPICE | ZTEC 鉴权 + heartbeat ✅ | CSAP startDesktop ✅ |
| 家庭云电脑 | `sc-cloud-pc` | SCG → JWAE/XE → SPICE | v1 heartbeat ✅ | SC API getConnectInfo ✅ |

### 16.2 家庭云电脑保活

`/cc/cloudPc/heartbeat/v2` 对 SC 云电脑可能返回 `4043 该云电脑已在其他设备上登录`，也可能在无密码解锁态返回 `4041 当前云电脑处于解锁状态,且无密码`。官方 H5/SDK 日志里出现过 `4041`，客户端不把它当成连接流程的致命错误。

发现 **v1 接口** `/cc/cloudPc/heartbeat/v1` 直接返回 SUCCESS，不检查设备冲突。22 台 VM 全部验证通过。

当前 Python 脚本默认用 v1 做服务器保活；如需对齐官方行为，可通过参数切换到 v2。

### 16.3 SC API 协议栈

SC 云电脑使用独立的 API 服务器，基于 OAuth 2.0 认证：

```
API 服务器: https://api.soho.komect.com:1443
Native SDK: libChuanyunSDK.dylib (Swift, 使用 Alamofire + Moya + SwiftyRSA)
```

**API 端点：**
| 路径 | 用途 |
|------|------|
| `/gzs/auth/oauth/rsa-public-key` | RSA 公钥（用于加密 vmId） |
| `/gzs/auth/oauth/token` | OAuth token 获取 |
| `/sc/open-portal/openapi/terminal/v1/getConnectInfo` | 获取连接信息（触发开机） |
| `/sc/open-portal/openapi/terminal/v1/getVmReadyStatus` | 查询 VM 就绪状态 |
| `/sc/open-portal/openapi/terminal/v1/vm/handle` | VM 操作（重启等） |

### 16.4 OAuth 认证（已解决）

**关键发现：不是标准 OAuth，使用自定义 `grant_type=ext`**

```
POST /gzs/auth/oauth/token
Content-Type: application/x-www-form-urlencoded

Headers:
  gzs-client-id: sc-user-5e38ece5       ← 固定值，从 SDK 日志中捕获
  gzs-timestamp: {毫秒时间戳}
  sc-terminal-sn: {设备序列号}
  sc-unit-type: Mac17,9                 ← 2.18.23 新版实际值；旧版日志曾为 Mac
  sc-network-type: 2
  User-Agent: cdpsdk-macos-2.18.23(2.18.23.213)

Body:
  grant_type=ext                         ← 自定义扩展 grant（非 password/authorization_code）
  client_id=sc-user-5e38ece5             ← 固定应用标识
  bizCode=10002                          ← 来自 getFirmAuth 响应
  token={scAuthCode}                     ← 来自 getFirmAuth 的 JWT
  source=biz

响应：access_token (JWT, 12h有效期) + refresh_token
```

**逆向过程：**
1. `client_id` 在 SDK 二进制中始终为空（运行时设置）
2. 通过 `--ignore-certificate-errors` 启动官方客户端捕获日志
3. 从日志 `headerparamsDict` 中发现 `gzs-client-id: sc-user-5e38ece5`
4. 通过 IDA 反编译 `CloudComputerInterface.task.getter` 发现 `grant_type=ext`
5. 从反编译代码确认 `token` 参数是 `connectAuthCode`（即 scAuthCode JWT）

### 16.5 开机流程（已打通）

**官方客户端日志证实的完整流程：**

```
1. getToken (OAuth ext) → access_token ✅ Python 已实现
2. getConnectInfo (vmId RSA加密) → 触发开机 + 返回 scgConnectInfo
   - 不需要调 handleVM！getConnectInfo 本身就是开机接口
   - 关机 VM 调用后约 56 秒返回
   - 响应包含 scgIP, scgPort, traceID
3. getVmReadyStatus (RSA加密 vmId + 明文 traceId) → readyStatus=1 表示就绪
4. 连接 JWAE → SCG → SPICE 桌面
```

**getConnectInfo 请求格式：**
```
POST /sc/open-portal/openapi/terminal/v1/getConnectInfo
Content-Type: application/json
Authorization: Bearer {access_token}
gzs-client-id: sc-user-5e38ece5
gzs-timestamp: {毫秒时间戳}

Body: {"vmId": "{rsa}BASE64URL(RSA_PKCS1v15(vmIdString))"}
```

**getVmReadyStatus 请求格式：**
```
POST /sc/open-portal/openapi/terminal/v1/getVmReadyStatus
Content-Type: application/json
Authorization: Bearer {access_token}
gzs-client-id: sc-user-5e38ece5
gzs-timestamp: {毫秒时间戳}

Body: {"vmId": "{rsa}BASE64URL(RSA_PKCS1v15(vmIdString))", "traceId": "{plain_traceId}"}
```

实测组合：

| vmId | traceId | 结果 |
|------|---------|------|
| 明文 | 明文 | `90010002 参数错误或解密失败` |
| RSA 加密 | RSA 加密 | token/session 相关错误 |
| RSA 加密 | 明文 | `00000 readyStatus=1` |

**官方日志对照：**

```
connectVMID: 960470
base64ConnectVMID: kHkdr9lqXo3FhfnxwMneSW5D7txx07odgizAW6GfEXKv1w4VfYme9T6GTFdtPpNHpbTjfj8zSrQzZV3JbZalZasRZzQTfa7Vte6NUP2snEVSrn0LjpJOfz6kvvhyo3zuB20RH5ygIlGEDeoA87MPk5LAAzsyL4DUeOX1JFXle18
```

这个值长度是 **171 字符**。解码时补一个 `=` 后得到 **128 字节 RSA 密文**。

2026-05-12 新日志进一步确认官方输出会包含 `-` 和 `_`，不是标准 base64 的 `+` 和 `/`。因此请求里的 `vmId` 不是保留 padding 的标准 base64，而是：

```
{rsa} + base64url(RSA_PKCS1v15(utf8(vmId))).rstrip("=")
```

### 16.6 RSA 加密兼容性结论

之前 Python `cryptography` 库的 RSA PKCS1v15 加密结果被服务端拒绝（`90010002 参数错误或解密失败`）。结合 `/tmp/h5.log` 与 SDK 二进制复核后，根因不是 Python 的 RSA 实现，而是 **OpenPortal 使用另一把 SDK 内置公钥 `sdk2`**；base64url 去 padding 是另一个必须对齐的格式条件。

- `/gzs/auth/oauth/rsa-public-key` 返回的是 `sdk1` 公钥，和 SDK 二进制第一把硬编码值一致
- 加密算法确认正确（`kSecKeyAlgorithmRSAEncryptionPKCS1` = PKCS1v15）
- 官方 SDK 输出 128 字节密文的 base64url 后去掉末尾 `=`，最终 171 字符
- 官方 SDK 使用 SwiftyRSA → Apple Security framework
- Python `cryptography` 和 macOS `Security.framework` 都能产出 128 字节密文；PKCS1v15 padding 随机，密文每次不同是正常现象
- `/gzs/auth/oauth/rsa-public-key` 返回值和 SDK 内置第一个公钥 `sdk1` 一致，但用于 `getConnectInfo` 会返回 `90010002`
- SDK 二进制内第二个内置 RSA 公钥 `sdk2` 才是 `getConnectInfo` 实际需要的 OpenPortal 公钥；脚本默认使用 `sdk2`
- `getVmReadyStatus` 也必须继续使用同一个 `{rsa}BASE64URL(RSA_PKCS1v15(vmId))`，不能改回明文
- `traceId` 来自 `getConnectInfo` 响应，保持明文发送
- 官方日志成功样本 `connectVMID=960534`，脚本默认 `--vm-index 0` 未必选中同一台 SC VM；先用 `--list-sc --probe-firm-auth` 对齐 `firm_vmId`
- 2026-05-12 `/tmp/h5.log` 成功样本显示 `userServiceId=37268191 -> vmId=960490`，SC SDK 头为 `sc-unit-type=Mac17,9`、`User-Agent=cdpsdk-macos-2.18.23(2.18.23.213)`

**当前落地脚本：** `cloudpc_sc_client.py`

已实现：

1. SOHO 登录复用 `cloudpc_protocol.py`
2. 选择 `spuCode=sc-cloud-pc` 的家庭云电脑
3. `getFirmAuth` 拿 `vmId` / `bizCode` / `scAuthCode`
4. OAuth `grant_type=ext` 获取 access token
5. 使用 SDK 内置 `sdk2` OpenPortal RSA 公钥
6. `{rsa}` + RSA_PKCS1v15(vmId) + 去 padding base64url
7. 可选调用 `getConnectInfo`
8. 可选调用 `getVmReadyStatus`
9. 可选 heartbeat 保活循环，默认 30 秒一跳

默认不触发开机；必须显式加 `--connect-info`。

列出家庭云电脑，并打印每台 `getFirmAuth` 返回的真实 `vmId`：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --list-sc --probe-firm-auth
```

只打印加密结果、不调用开机接口：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --print-only
```

调用 `getConnectInfo`，可能触发开机：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --connect-info --ready-status
```

开机后保持 10 分钟，每 30 秒发一次 heartbeat/v1，并查询 ready：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --connect-info --ready-status --keepalive-seconds 600 --heartbeat-interval 30
```

如需完全对齐官方 H5/SDK 的 v2 心跳：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --connect-info --ready-status --keepalive-seconds 600 --heartbeat-interval 30 --heartbeat-api v2
```

如果要复现旧错误或做 A/B 验证：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --public-key-profile api --connect-info
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --rsa-provider security --connect-info
```

如果要验证旧错误，可以切回标准 base64 或保留 `=` padding：

```
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --standard-base64 --connect-info
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --keep-base64-padding --connect-info
```

官方客户端运行时抓 RSA 明文/密文：

```
frida -p <官方客户端PID> -l hook_sc_rsa_frida.js
```

保持 hook 运行后，在官方客户端点一次家庭云连接。输出里的 `plain_ascii` 应等于官方日志的 `connectVMID`，`cipher_b64url` 应等于官方日志的 `base64ConnectVMID`。
