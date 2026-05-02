# 移动云电脑 ZTE 分支详细架构

> 日期: 2026-05-01  
> 范围: 本地 macOS 客户端、日志、native SDK、IDA 导出证据。  
> 边界: 本文只写架构、职责、时序和可观测证据；不保存账号凭据、token、会话 ID，也不提供可直接复刻远程连接的发包实现。

## 1. 总体结论

当前账号命中的是 `zte-cloud-pc` 分支。它不是简单的 “Electron 调 HTTP 后直连 VM”，而是四层架构：

```text
HTTP 控制面
  Electron Main/Renderer
  SOHO API: 登录、列表、getFirmAuth、heartbeat、infoReport、logout

Native 调度层
  chuanyunAddOn-zte/jsCysdk.js
  chuanyunsdk.node
  libvdconn.dylib
  uSmartView_VDI_Client

传输代理层
  libcag / CAG access gateway
  ZTEC/RADIUS 前置认证或连通性检查
  ICE 参数初始化
  UDP/KCP/UDT-style reliable transport
  TLS 1.3 over proxy transport
  CAG tunnel virtual link multiplexer

桌面协议层
  GSpice / SPICE channels
  main, display, inputs, cursor, playback, record
  DISPLAY_INIT / surface / draw / ping / ack
```

关键点：SPICE 并不直接跑在外层 TCP 上。GSpice 先连接本地 `127.0.0.1` socketpair，真实网络由 native proxy thread 接管，再通过 ICE/KCP/UDT/TLS 和 CAG tunnel 转发到云端。

## 2. 组件边界

### 2.1 Electron 控制面

Electron 负责用户态业务：

```text
登录
  -> 拉系统配置
  -> 拉云电脑列表
  -> 点击连接后调用 getFirmAuth
  -> 按 spuCode 分流 native SDK
  -> 接收 native connect/reconnect/disconnect callback
  -> 上报 heartbeat/infoReport/logout
```

已确认的关键接口：

```text
/login/encryptKey/v1
/login/publicKey/v1
/login/home/namePwdLogin/v1
/cc/cloudPc/list/v6
/cc/getFirmAuth/v1
/cc/cloudPc/heartbeat/v2
/cc/cloudPc/infoReport/v2
/cc/cloudPc/logout/v2
```

`getFirmAuth` 返回厂商连接字段形态：

```text
spuCode
vmUserName
vmPassword
vmId
vmcIp / vmcPort
cagIp / cagPort / cagIpv6
scgIp / scgTcpPort / scgUdpPort
bizCode
scAuthCode
```

在当前 ZTE 分支里，`scg*` 字段不是主路径；实际数据面围绕 ZTE SDK、CAG、ICE/KCP 和 GSpice。

### 2.2 Native 入口

Electron 到 native 的路径：

```text
src/main/index.js
  -> spuCode includes "zte-"
  -> zteWorker.connect(...)
  -> chuanyunAddOn-zte/jsCysdk.js
  -> chuanyunsdk.node
  -> dlsym/connectDesktop
  -> libvdconn.dylib
  -> uSmartView_VDI_Client.app
```

关键 native 导出：

```c
connectDesktop(...)
restartDesktop(...)
disconnectDesktop(...)
```

`libvdconn.dylib` 负责把 HTTP 控制面拿到的厂商参数改造成 `uSmartView_VDI_Client` 的启动/共享内存连接参数。日志里的典型参数形态：

```text
-p 5100
--hv6 <SPICE-IPv6>
--pv6 5100
--proxy-sport 60065
--type ice
--udt-multiex 1
--quic-enable 2
--https 1
--ag-ip <CAG-IP>
--ag-port 8899
--vmcip <VMC-IP>
--vmcport 8443
```

其中 `<SPICE-IPv6>:5100` 和 `60065` 是当前远控数据面更关键的目标参数；不能只看 `vmcIp:8443`。

## 3. 完整连接时序

### 3.1 点击连接前后

```text
用户点击连接
  -> Electron 调 /cc/getFirmAuth/v1
  -> 根据 spuCode=zte-cloud-pc 进入 zteWorker.connect
  -> chuanyunsdk.node 调 libvdconn connectDesktop
  -> libvdconn 构造连接参数
  -> 启动或驱动 uSmartView_VDI_Client
```

native callback 是业务侧“连接中/连接成功”的依据：

```text
connectDesktopRet ... Success to Connectting desktop
connectDesktopRet ... Success to Connect desktop
```

### 3.2 ZTEC / CAG 前置阶段

`cag.log` 证明 ZTEC 阶段使用 RADIUS 类型，不是 UAC：

```text
auth type is radius
aes_flag = 258
destAddr is IPV6
recv cag reply 200
connect to cag success
notify_quit
```

解释：

```text
ZTEC/RADIUS 阶段
  -> 与 CAG 建立前置认证或连通性检查
  -> 使用日志中可见的 AES 参数协商结果
  -> 成功后可出现 notify_quit
```

注意：`notify_quit` 说明这条路径不能简单理解为“后续 SPICE 就在该 TCP socket 上继续跑”。真实桌面数据还要看 `client.log` 中 GSpice/proxy thread 的建链。

### 3.3 GSpice 本地 socketpair

成功日志显示，GSpice 不是直接连公网网关，而是先连接本机 loopback：

```text
session_connect before m_pHost[], m_pPort[5100]
session_connect after m_pHost[<SPICE-IPv6>], m_pPort[5100]
main-1:0: socket connect to 127.0.0.1:<local> success with 127.0.0.1:<peer>
display-2:0: socket connect to 127.0.0.1:<local> success with 127.0.0.1:<peer>
inputs-3:0: socket connect to 127.0.0.1:<local> success with 127.0.0.1:<peer>
cursor-4:0: socket connect to 127.0.0.1:<local> success with 127.0.0.1:<peer>
playback-5:0: socket connect to 127.0.0.1:<local> success with 127.0.0.1:<peer>
record-6:0: socket connect to 127.0.0.1:<local> success with 127.0.0.1:<peer>
```

这个 local socketpair 是关键架构点：

```text
GSpice channel
  -> 127.0.0.1 socketpair
  -> native proxy thread
  -> UDP/KCP/UDT/TLS/CAG tunnel
  -> 云端 SPICE server
```

因此，外部 Python 直接向 CAG TCP 发送 SPICE `REDQ` 会超时，因为它绕过了 native proxy thread 和 tunnel add_link。

### 3.4 Proxy thread 与 ICE/KCP/UDT/TLS

proxy thread 建立远端 transport：

```text
[PROXY] Creating proxy fd session
[PROXY] Setting up spice proxy link with SSL=1
[PROXY] Creating UDP proxy fd session
[PROXY] Assigning SPICE proxy socket
udt_init_ssl_ctx ... init SSL CTX for udt ok
initRedirectParams ... s_proxy_port[60065] proxy_type[ice]
init_local_rw_sock_pair_udp ... support quic:0 ... be_ssl:1 kcp->be_ssl:1
deal_kcp_auth_cmd ... IKCP_CONV_AUTH_HEAD_ACK
deal_kcp_auth_cmd ... IKCP_CONV_AUTH_ACK
deal_kcp_sync_ack_cmd ... IKCP_CONV_SYNACK
deal_kcp_sync_ack_cmd ... be_quic=0 be_using_stream=0 be_ssl=1
deal_udt_ssl_connect ... TLS1.3
deal_udt_ssl_connect ... udt ssl connect success
```

当前日志支持的判断：

```text
proxy_type = ice
quic = 0
be_ssl = 1
kcp->be_ssl = 1
TLS = 1.3
transport = UDP/KCP/UDT-style + TLS
```

## 4. CAG Tunnel 多路复用

TLS/transport 建好后，proxy thread 使用 CAG tunnel 虚拟通道承载多个 SPICE channel。日志中的关键函数是 `send_tunnel_add_link`。

### 4.1 Channel 注册

每个 SPICE channel 需要先注册一个 virtual channel ID：

```text
send_tunnel_add_link -> channel type 1 -> main
send_tunnel_add_link -> channel type 2 -> display
send_tunnel_add_link -> channel type 3 -> inputs
send_tunnel_add_link -> channel type 4 -> cursor
send_tunnel_add_link -> channel type 5 -> playback
send_tunnel_add_link -> channel type 6 -> record
```

注册完成后，标准 SPICE link/auth/data 才能在对应虚拟通道里流动：

```text
spice_channel_send_link ... send link msg
spice_channel_recv_link_hdr ... recv link hdr
spice_channel_recv_link_msg ... recv link msg
spice_session_channel_connected ... all channel 6/6 connect success
```

### 4.2 Tunnel frame 概念

离线逆向中可把 tunnel 视为一个极简多路复用层：

```text
CAG proxy frame
  -> command
  -> virtual link id
  -> payload length
  -> payload
```

已归类的 command 语义：

```text
DATA      : SPICE channel 数据
ADD_LINK  : 注册虚拟通道
CLOSE     : 关闭虚拟通道
VM_INFO   : VM 信息/状态类消息
```

这层作用类似自研分支里的 `ChuanyunHead`：把多个 SPICE channel 复用到一条受控传输链路上，但 ZTE/CAG 的帧格式和 channel 注册方式不同。

## 5. SPICE 层

SPICE 层仍然是最终桌面协议，通道语义是标准远程桌面模型：

```text
main      : 会话控制、channel 列表、能力协商
display   : 画面、surface、draw、压缩图像数据
inputs    : 键盘、鼠标、触控输入
cursor    : 光标形态和位置
playback  : 音频播放
record    : 音频录制
```

保活相关的关键不是“有没有 TCP 连接”，而是桌面会话是否完整建立。需要观察：

```text
main channel connected
display channel connected
DISPLAY_INIT sent by client
SURFACE_CREATE / DRAW / MARK 等 display 初始化完成
PING/PONG、ACK 窗口正常
SOHO heartbeat/infoReport 正常
```

目前日志能明确证明 `all channel 6/6 connect success`；display surface 级别则需要继续结合更细的 GSpice 日志或抓包解析验证。

## 6. 保活判定链路

平台态和桌面态是两套信号：

```text
业务平台态
  /cc/cloudPc/heartbeat/v2
  /cc/cloudPc/infoReport/v2
  /cc/cloudPc/logout/v2

远控会话态
  native connect callback
  CAG/ICE/KCP/TLS session
  CAG tunnel virtual links
  SPICE main/display session
  display surface/render events
```

可靠判断应该同时看：

```text
getFirmAuth 成功
uSmartView 启动成功
proxy_type[ice] 初始化
KCP AUTH/SYNACK 成功
TLS1.3 成功
send_tunnel_add_link 注册 6 个 SPICE channel
all channel 6/6 connect success
display 初始化完成
heartbeat/infoReport 持续上报
```

单独的 ZTEC `200 OK`、单独的 TCP 连接、单独的 HTTP heartbeat 都不足以证明桌面会话已完整建立。

## 7. 抓包与验证建议

控制面：

```text
Proxyman / HTTPS MITM
  -> 登录
  -> 云电脑列表
  -> getFirmAuth
  -> heartbeat/infoReport/logout
```

数据面：

```text
tcpdump / Wireshark
  -> CAG host
  -> UDP 8899
  -> UDP/TCP 60065
  -> TCP 8899
  -> loopback 127.0.0.1 local SPICE socket
```

日志对齐：

```text
client.log
  session_connect
  spice_channel_print_connect_info
  deal_create_proxy_fd_session
  initRedirectParams
  deal_kcp_auth_cmd
  deal_kcp_sync_ack_cmd
  deal_udt_ssl_connect
  send_tunnel_add_link
  spice_session_channel_connected

cag.log
  auth type is radius
  aes_flag
  destAddr is IPV6
  recv cag reply 200
  notify_quit

vdconn.log
  StartSpiceProcess AddConnectParm
  connectDesktopRet
```

## 8. 文件与工具

当前本地文件：

```text
ANALYSIS.md
  顶层分析结论。

cloudpc_analysis/ARCHITECTURE.md
  本详细架构文档。

cloudpc_flow_analyzer.py
  Electron/native/log 脱敏分析器。

cloudpc_zte_session_trace.py
  ZTE session 日志时序提取器，可离线生成 Markdown/JSON。

cloudpc_analysis/ZTE_SESSION_TIMELINE.md
  已生成的脱敏时序报告。
```

推荐复跑：

```bash
python3 cloudpc_zte_session_trace.py \
  --out cloudpc_analysis/ZTE_SESSION_TIMELINE.md \
  --json cloudpc_analysis/zte_session_timeline.json \
  --limit 260
```

## 9. 一句话架构图

```text
Electron 控制面
  -> getFirmAuth
  -> ZTE native connectDesktop
  -> libvdconn 启动 uSmartView
  -> GSpice 连接 127.0.0.1 socketpair
  -> proxy thread 创建 UDP/KCP/UDT/TLS transport
  -> CAG tunnel add_link 注册多个 virtual channel
  -> SPICE main/display/inputs/cursor/playback/record
  -> display session 建立后配合 SOHO heartbeat 维持业务在线态
```
