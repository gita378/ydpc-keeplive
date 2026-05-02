# 移动云电脑协议分析（ZTE / ICE-KCP 最终修正版）

> 更新日期: 2026-05-01  
> 范围: 本地日志、Electron 资源、native SDK、IDA 导出结果的协议链路分析  
> 注意: 本文只记录可复核的架构与证据，不包含可复用的认证密钥、账号凭据、会话 ID 或可直接生成远程桌面数据包的实现细节。

## 0. 当前结论

之前把 `CAG 200 OK` 后的链路判断成“同一条 TCP 隧道里直接发送 SPICE `REDQ`”是不完整的。成功日志显示，当前 ZTE 分支的远程桌面数据面走 `proxy_type[ice]` 路径，SPICE/GSpice 先连接本机 loopback socketpair，再交给 proxy thread；proxy thread 通过 UDP/KCP/UDT-style 会话和 SSL/TLS 1.3 承载真实远程桌面数据。

因此，`CAG` 鉴权成功后直接在 TCP socket 上发送 SPICE `REDQ` 超时是预期结果：发送位置处在错误传输层。正确的解释是：

```
SOHO API / getFirmAuth
  -> ZTE native SDK
  -> uSmartView_VDI_Client / GSpice
  -> SPICE channel socket connect to 127.0.0.1:<local-port>
  -> proxy thread 创建 SPICE UDP proxy fd session
  -> ICE 参数初始化: host=<SPICE-IPv6>, port=5100, s_proxy_port=60065
  -> UDP/KCP 会话认证与 SYNACK
  -> SSL/TLS 1.3 over KCP/UDT-style link
  -> send_tunnel_add_link 注册 SPICE channel
  -> SPICE/GSpice channel handshake
  -> display / inputs / cursor / audio 等通道连接成功
```

当前不继续实现 `pykcp` 级别的协议保活客户端。后续工作只做三类安全内容：脱敏分析文档、日志/抓包证据归档、官方客户端路径或官方 24h 能力的配置验证。

## 1. 分支与组件

本地客户端是 Electron + native SDK 组合：

```
移动云电脑.app
  Contents/Resources/app.asar
    -> JS 主进程: 登录、设备列表、getFirmAuth、心跳等 HTTP 控制面
  app.asar.unpacked/node_modules/chuanyunAddOn-zte
    -> jsCysdk.js / chuanyunsdk.node
    -> libvdconn.dylib
    -> libcag.dylib
    -> uSmartView_VDI_Client.app
```

账号当前命中的业务分支是 `spuCode = zte-cloud-pc`。这意味着有效链路走 ZTE SDK，不是 `jwae.framework + SCG:10800` 那条自研分支。`jwae.framework` 仍存在于客户端包内，但不是当前成功连接日志的主路径。

## 2. 控制面

HTTP 控制面仍由 Electron 主进程负责，核心流程是：

```
登录
  -> 云电脑列表
  -> getFirmAuth
  -> native SDK connectDesktop
  -> 官方客户端进程 uSmartView_VDI_Client
```

`getFirmAuth` 返回的数据包含厂商分支、网关、VM、临时凭据等字段。报告中不记录原始 `APP_KEY`、`APP_SECRET`、`vmUserName`、`vmPassword`、`vmId`、token、签名值。需要复核时用本地 `1.log` 和官方客户端日志，通过 `cloudpc_flow_analyzer.py` 生成脱敏报告。

## 3. 数据面修正

### 3.0 ZTEC 的实际角色

`libcag` 里的 ZTEC 鉴权能返回 `200 OK`，但本地日志里能看到 ZTEC 阶段完成后很快 `notify_quit`。这说明它更像前置连通性/控制面测试或 CAG 能力探测，不是后续 SPICE channel 的直接承载通道。

真正桌面连接由 `uSmartView_VDI_Client` 内部的 GSpice/proxy thread 建立，入口不是外部 TCP，而是本机 loopback socketpair：

```text
session_connect before m_pHost[], m_pPort[5100]
session_connect after m_pHost[<SPICE-IPv6>], m_pPort[5100]
main-1:0: socket connect to 127.0.0.1:<local-port> success with 127.0.0.1:<peer-port>
[PROXY] Creating proxy fd session
[PROXY] Setting up spice proxy link with SSL=1
[PROXY] Creating UDP proxy fd session
[PROXY] Assigning SPICE proxy socket
```

这个结构解释了为什么直接连 CAG TCP 或直接写 `REDQ` 都不对：SPICE 客户端以为自己连的是本地 socket，真实网络传输由 SDK 内部 proxy thread 接管。

### 3.1 关键日志证据

成功连接日志中的关键点：

```text
session_connect after m_pHost[<SPICE-IPv6>], m_pPort[5100]
main-1:0: socket connect to 127.0.0.1:<local-port> success with 127.0.0.1:<peer-port>
[PROXY] Setting up spice proxy link with SSL=1
[PROXY] Creating UDP proxy fd session
udt_init_ssl_ctx ... init SSL CTX for udt ok
initRedirectParams ... port[5100] proxy_port[] s_proxy_port[60065] proxy_type[ice]
init_local_rw_sock_pair_udp ... client is support quic:0 (... be_ssl:1 kcp->be_ssl:1 ... proxy_sock->use_quic:0)
deal_kcp_auth_cmd ... recv IKCP_CONV_AUTH_HEAD_ACK from:<CAG>:8899
deal_kcp_auth_cmd ... recv IKCP_CONV_AUTH_ACK from:<CAG>:8899
deal_kcp_sync_ack_cmd ... recv IKCP_CONV_SYNACK from:<CAG>:8899
deal_kcp_sync_ack_cmd ... be_quic=0 be_using_stream=0 be_ssl=1
deal_udt_ssl_connect ... SSL_connect connect and current version TLS1.3(0x304)
deal_udt_ssl_connect ... udt ssl connect success
send_tunnel_add_link ... destination [IPv6]:60065, channel type 1 -> virtual channel ID 1
spice_session_channel_connected ... all channel 6/6 connect success
```

本地可复核位置：

```text
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:125
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:138
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:143
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:144
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:150
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:151
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:156
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log:597
移动云电脑.app/.../uSmartView_VDI_Client.app/Contents/log/client.log.1:29213
```

### 3.2 对旧结论的修正

旧结论：

```text
ZTEC auth -> CAG 200 OK -> TCP tunnel -> 直接发送 SPICE REDQ
```

修正后：

```text
ZTEC/CAG 控制阶段
  -> GSpice 连接本机 127.0.0.1 socketpair
  -> proxy thread 接管本地 SPICE socket
  -> ICE redirect 参数 proxy_type[ice] / s_proxy_port[60065]
  -> UDP/KCP 会话认证: AUTH_HEAD_ACK / AUTH_ACK / SYNACK
  -> 按 be_ssl 配置进行 SSL/TLS 1.3 握手
  -> tunnel add_link 绑定虚拟通道
  -> 每个 SPICE channel 在已建立的虚拟链路内完成 GSpice 握手
```

这也解释了为什么只复现 HTTP API 和 CAG TCP 鉴权不足以获得桌面：`REDQ` 必须出现在官方 native SDK 建好的 channel 上，而不是出现在最外层 CAG TCP 连接上。

## 4. SPICE 层位置

SPICE 仍然是最终桌面协议，但它位于 GSpice/native SDK 封装之后。日志里的 `main-1:0`、`display-2:0`、`inputs-3:0`、`cursor-4:0`、`playback-5:0`、`record-6:0` 说明官方客户端仍按 SPICE channel 组织远程桌面会话。

关键差异是传输层：

| 项目 | 早期错误判断 | 当前日志支持的判断 |
|---|---|---|
| 网关入口 | TCP 直接承载 SPICE | CAG + ICE/KCP/UDT-style UDP |
| SPICE 本地入口 | 无 | `127.0.0.1:<local-port>` socketpair |
| QUIC | 未区分 | `quic:0`，当前成功路径未启用 QUIC |
| 加密 | 外层 TLS/TCP | `be_ssl:1` / `kcp->be_ssl:1` 后进入 TLS 1.3 |
| SPICE `REDQ` | 直接写 TCP | 写入 native SDK 建好的 virtual channel |
| 端口角色 | `8899` 即 SPICE 承载 | `8899` 是 CAG/KCP 侧关键入口，`60065` 是 ICE/secure proxy 参数 |

## 5. 抓包方向

下一轮抓包不应再只盯 TCP `8899`。应该同时观察：

```text
udp and host <CAG-IP> and port 8899
udp and port 60065
tcp and host <CAG-IP> and port 8899
```

抓包目标不是解密或伪造会话，而是验证三件事：

1. `IKCP_CONV_*` 日志事件与 UDP 包时序是否一一对应。
2. `be_ssl=1` 后是否能在包长/方向上看到 TLS 握手阶段特征。
3. `send_tunnel_add_link` 与后续 SPICE channel success 的时间关系。

如果用 Proxyman，它更适合 HTTP 控制面和可见 TLS 代理流量；这类 UDP/KCP 数据面更适合 Wireshark/tcpdump 直接抓网卡。

## 6. 当前文件状态

已有本地辅助文件：

```text
cloudpc_flow_analyzer.py
  用途: 解包 Electron、提取日志/字符串/IDA 证据、生成脱敏报告。

cloudpc_analysis/REPORT.md
  用途: 自动生成的控制面与 native 证据摘要。

cloudpc_analysis/ZTE_PROTOCOL_NOTES.md
  用途: ZTE native 分支的安全分析笔记。

cloudpc_analysis/JIATINGYUN_REPO_REVIEW.md
  用途: jiatingyun_pc_automation 仓库评审，结论是官方 Linux 客户端 + GUI 自动化，不是协议级实现。
```

不建议继续维护早期按 TCP/CAG 思路写的保活脚本。那条路径的核心假设已经被 ICE/KCP 成功日志推翻。

## 7. 后续可做

可继续做：

1. 更新 `cloudpc_flow_analyzer.py`，把 `proxy_type[ice]`、`IKCP_CONV_*`、`be_ssl`、`udt ssl connect success` 纳入默认证据。
2. 用 tcpdump/Wireshark 建立 UDP/KCP 时序图，和 `client.log` 时间戳对齐。
3. 验证官方客户端、官方 24h 不关机配置、容器化官方客户端方案，选择维护成本最低的保活方式。

不继续做：

1. 不实现可复用的 KCP/UDP/TLS/SPICE 伪客户端。
2. 不在文档中保存明文 token、签名密钥、账号、VM 凭据、会话 ID。
3. 不把 `DISPLAY_INIT` 或 SPICE 认证流程整理成可直接投递到网关的包生成器。
