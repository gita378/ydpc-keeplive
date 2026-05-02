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
python3 cloudpc_protocol.py --username zhaoboy3 --password 'ZXCzxc199692*'
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
