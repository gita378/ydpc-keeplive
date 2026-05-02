# 移动云电脑连接链路分析报告

- 生成时间: 2026-05-01T22:46:17
- 应用路径: `/Users/zxc/Desktop/移动云电脑/移动云电脑.app`
- 操作系统: `macOS-15.7.4-arm64-arm-64bit`
- 脱敏策略: token、密码、签名、authCode、APP_SECRET 默认写为 `<redacted>`

## 结论

这个客户端是 Electron 壳加 native 远控 SDK。Electron 负责登录、列表、接口鉴权和 IPC 分发；真正的画面、键鼠、音频、USB/剪贴板等远控数据面在 native SDK/嵌入客户端里。

当前 ZTE 成功日志支持的桌面数据面不是 `CAG 200 OK` 后直接在 TCP 上写 SPICE `REDQ`。实际链路是 GSpice 先连接本机 `127.0.0.1` socketpair，native proxy thread 创建 UDP proxy fd session，再按 `proxy_type[ice]` 建立 KCP/UDT-style 会话，`be_ssl=1` 时进入 TLS 1.3，之后通过 `send_tunnel_add_link` 为 main/display/inputs/cursor/playback/record 等 SPICE channel 绑定虚拟通道。

`libcag`/ZTEC 日志里的 `notify_quit` 表明该阶段可作为前置连通性或控制面证据，但不应把它误判为最终 SPICE 数据承载 socket。

主要链路如下:

1. 启动后请求 `/login/encryptKey/v1` 获取 RSA 公钥，再请求 `/system/settings/v1` 拉配置。
2. 登录请求走 `/login/publicKey/v1`、`/login/home/namePwdLogin/v1` 等接口，登录态保存为 `sohoToken`/`userId`。
3. 云电脑列表来自 `/cc/cloudPc/list/v6`，点击连接后请求 `/cc/getFirmAuth/v1`。
4. `/cc/getFirmAuth/v1` 返回一次性厂商连接参数，字段形态包括 `vmUserName`、`vmPassword`、`vmId`、`vmcIp`、`vmcPort`、`cagIp`、`cagPort`、`scgIp`、`scgTcpPort`、`scgUdpPort`、`spuCode`、`bizCode`、`scAuthCode`。
5. Renderer 通过 preload 暴露的 `mainApi.connectWorker()` 调 Electron 主进程 IPC `worker-connect`。
6. 主进程按 `spuCode` 分流: `zte-*` 调 `chuanyunAddOn-zte`/`connectDesktop`；`wave-*` 在 Windows 拉起 `CloudPC.exe token=...`；其他走 `chuanyunAddOn`/`connectVm`。
7. native 层回调 `connect/reconnect/disconnect` 给 Electron，Electron 再通知页面，并启动 `/cc/cloudPc/heartbeat/v2` 和 `/cc/cloudPc/infoReport/v2`。
8. ZTE 数据面关键日志顺序: `session_connect after m_pHost[...]` -> `socket connect to 127.0.0.1` -> `[PROXY] Setting up spice proxy link with SSL=1` -> `IKCP_CONV_*` -> `TLS1.3` -> `send_tunnel_add_link` -> `all channel 6/6 connect success`。

## 关键配置

- 未解析到配置，可能 asar 未成功解包。

## 接口清单

- `/login/encryptKey/v1`: 0 个源码引用
- `/login/publicKey/v1`: 0 个源码引用
- `/login/home/namePwdLogin/v1`: 0 个源码引用
- `/token/checkToken/v1`: 0 个源码引用
- `/cc/cloudPc/list/v6`: 0 个源码引用
- `/cc/getFirmAuth/v1`: 0 个源码引用
- `/cc/getRebootAuth/v1`: 0 个源码引用
- `/cc/getDisasterAuth/v1`: 0 个源码引用
- `/cc/cloudPc/heartbeat/v2`: 0 个源码引用
- `/cc/cloudPc/infoReport/v2`: 0 个源码引用
- `/cc/cloudPc/logout/v2`: 0 个源码引用

- 其他 URL/接口引用数: 0

## Native SDK 边界

- `chuanyunAddOn/jsCysdk.js`: JS 包装 `init/connect/restart/disconnect/callback`，底层调用 `runSimpleAsyncWorker`。
- `chuanyun_api.h`: 暴露 `chuanyun_init`、`connectVm`、`restartVm`、`disconnectVm`。
- `chuanyunAddOn-zte/jsCysdk.js`: JS 包装 ZTE 连接参数，传入 `vmUserName/vmPassword/vmId/vmc/cag/scg`。
- `SohoSdk.h`: 暴露 `connectDesktop`、`restartDesktop`、`disconnectDesktop`、网络状态、视频参数等接口。
- 当前日志中的 `spuCode=zte-cloud-pc` 会进入 ZTE 分支：`chuanyunsdk.node` -> `libvdconn.dylib` -> `libcag.dylib`/`uSmartView_VDI_Client`。
- 嵌入的 ZTE 客户端包含 `libcag`、`libusbredirect`、`libclipboard_mac`、`QtNetwork` 等；自研 viewer 依赖 `spice-client-glib`、`usbredir`、`gstreamer`、`libx264`、`opus` 等。
- 另一个 `chuanyunAddOn` 分支包含 `libChuanyunSDK.dylib`、内嵌 `jwae.framework` 和 `spice-client-glib`，字符串中可见 CEM/OAuth/getConnectInfo、SCG、trunk/TLS/auth 等线索；但它不是这份日志实际命中的 ZTE 分支。
- 可用 `cloudpc_zte_session_trace.py` 从 `client.log`/`cag.log` 生成脱敏时序，重点观察 socketpair、PROXY、KCP、TLS1.3、add_link 和 channel success。

- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:20: let result = runWorker.notifyEvent((command, vmID, iCode, msg) => {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:21: if (command == 'restart') {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:22: command = 'reconnect';`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:34: function connect(options) {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:37: console.log("connect -  cur directory:", __dirname);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:40: console.log(`Connecting with params: <redacted>`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:42: let result = runWorker.runSimpleAsyncWorker('connect', options, () => { });`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:47: function reconnect(options) {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:50: console.log("reconnect -  cur directory:", __dirname);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:52: let result = runWorker.runSimpleAsyncWorker('restart', options, ()=>{});`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:57: function disconnect(options) {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:60: console.log("disconnect -  cur directory:", __dirname);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:62: let result = runWorker.runSimpleAsyncWorker('disconnect', options, ()=>{});`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:73: const result = runWorker.runSimpleAsyncWorker('init', options, ()=>{});`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:80: connect,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:81: disconnect,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/jsCysdk.js:82: reconnect,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:17: DesktopConnected = 0,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:18: DesktopConnectFailed,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:19: DesktopDisConnected,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:20: DesktopDisConnectedSeized,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:21: DesktopRestart,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:23: DesktopConnecting`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:26: typedef void(*ConnectStatusCb)(const char* strVmid, int mCode, const char*  errCode, const char* strErrorMsg, void* pUser);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:36: ConnectStatusCb pConnStateFunc;`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:37: } chuanyunInitParam_t;`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:39: int chuanyun_init(chuanyunInitParam_t *initParam);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:41: int connectVm(const char* strVMID, const char* strUserName, const char* strAuthCode, const char* strBizCode);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:43: int restartVm(const char* strVMID, const char* strUserName, const char* strAuthCode, const char* strBizCode);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn/ccsdk/mac/include/chuanyun_api.h:45: int disconnectVm(const char* strVMID);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:17: let result = runWorker.notifyEvent((command, vmID, iCode, msg) => {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:18: if (command == 'restart') {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:19: command = 'reconnect';`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:31: function connect(vmUserName, vmPassword, vmId, vmcIp, vmcPort, cagIp, cagPort, scgIp, scgTcpPort, scgUdpPort) {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:33: `Connecting with params: <redacted>`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:36: let result = runWorker.runSimpleAsyncWorker('connect', vmUserName, vmPassword, vmId, vmcIp, vmcPort, cagIp, cagPort, () => { });`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:41: function reconnect(vmUserName, vmPassword, vmId, vmcIp, vmcPort, cagIp, cagPort, scgIp, scgTcpPort, scgUdpPort) {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:42: let result = runWorker.runSimpleAsyncWorker('restart', vmUserName, vmPassword, vmId, vmcIp, vmcPort, cagIp, cagPort, () => { });`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:47: function disconnect(vmId) {`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:48: let result = runWorker.runSimpleAsyncWorker('disconnect', vmId, () => { });`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:58: connect,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:59: disconnect,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/jsCysdk.js:60: reconnect,`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/ccsdk/mac/SohoSdk.h:9: typedef void ( *connectDesktopCallbackFunc)(int iCode, int iExtCode, const char *cMesg, const char *vmId);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/ccsdk/mac/SohoSdk.h:11: VDCONNSHARED_EXPORT int connectDesktop(char *vmUserName, char *vmPassword, char *vmId, char *vmcIp, int vmcPort, char *cagIp, int cagPort, connectDesktopCallbackFunc pconnectDesktopCallbackFunc);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/ccsdk/mac/SohoSdk.h:12: VDCONNSHARED_EXPORT int disconnectDesktop(char *vmId, connectDesktopCallbackFunc pconnectDesktopCallbackFunc);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/ccsdk/mac/SohoSdk.h:13: VDCONNSHARED_EXPORT int restartDesktop(char *vmUserName, char *vmPassword, char *vmId, char *vmcIp, int vmcPort, char *cagIp, int cagPort, connectDesktopCallbackFunc pconnectDesktopCallbackFunc);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/ccsdk/mac/SohoSdk.h:30: //void qoeagent_init(const char *appInstallPath, const char *appName);`
- `/Users/zxc/Desktop/移动云电脑/移动云电脑.app/Contents/Resources/app.asar.unpacked/node_modules/chuanyunAddOn-zte/ccsdk/mac/SohoSdk.h:31: void qoeagent_init(const char *appInstallPath, const char *appName, const char *thirdPath, const QoeCallback *pQoeCallBack);`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/chuanyunsdk.node.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/libChuanyunSDK.dylib.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/jwae.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/spice-client-glib-2.0.8.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/chuanyunsdk.node.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/uSmartView_VDI_Client.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/libvdconn.dylib.strings.txt`
- `strings evidence: /Users/zxc/Desktop/移动云电脑/cloudpc_analysis/evidence/libcag.dylib.strings.txt`

## IDA 静态证据

以下是 ida-multi-mcp 导出的关键函数摘要，只列函数/字符串命中点，不写入运行时账号凭证。

- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/chuanyunsdk_zte_node/0x1280_0x1280.c:42: "connect callback function code: ",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/chuanyunsdk_zte_node/0x1850_0x1850.c:25: "disconnect callback function code: ",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/chuanyunsdk_zte_node/0x2760_0x2760.c:567: "********************** do connect **********************/n",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x47d0_0x47d0.c:2: __int64 __fastcall send_access_gateway_local_key(__int64 a1, int a2)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x47d0_0x47d0.c:25: strcpy((char *)__b, "ZTEC,"); /*0x4815*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x47d0_0x47d0.c:31: write_log((unsigned int)"send_access_gateway_local_key", 846, (unsigned int)"auth type is %s", (_DWORD)v4, v2, v3); /*0x487d*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x47d0_0x47d0.c:64: (unsigned int)"send_access_gateway_local_key",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x47d0_0x47d0.c:75: (unsigned int)"send_access_gateway_local_key",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x47d0_0x47d0.c:87: write_log((unsigned int)"send_access_gateway_local_key", 870, (unsigned int)"ERROR: malloc failed", 0, v5, v6);`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4ae0_0x4ae0.c:2: __int64 __fastcall recv_access_gateway_key(unsigned int a1, _DWORD *a2, int *a3, unsigned int a4)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4ae0_0x4ae0.c:26: write_log((unsigned int)"recv_access_gateway_key", 893, (unsigned int)"recv_access_gateway_key start!!!", v4, v5, v6); /*0x4b45*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4ae0_0x4ae0.c:41: (unsigned int)"recv_access_gateway_key",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4ae0_0x4ae0.c:43: (unsigned int)"recv server key from cag success, key = %u, aes_flag = %d",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4ae0_0x4ae0.c:52: (unsigned int)"recv_access_gateway_key",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:2: __int64 __fastcall send_access_gateway_connect_info(unsigned int *a1, int a2, int a3, int a4, int a5, int a6)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:66: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:68: (unsigned int)"start send connect info to cag...",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:85: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:91: tn_deal_aes_code((__int64)(v60 + 38), 0x40u, (__int64)&v62[30], v59, v58, 0, v57); /*0x4e53*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:93: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:104: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:112: xor_with_key(__b, v16, 99); /*0x4f39*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:117: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:128: tn_deal_aes_code((__int64)v55, 0x40u, (__int64)&v62[62], v59, v58, 0, v57); /*0x502e*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:133: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x4c70_0x4c70.c:153: (unsigned int)"send_access_gateway_connect_info",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5680_0x5680.c:2: __int64 __fastcall connect_to_access_gateway(unsigned int *a1)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5680_0x5680.c:20: (unsigned int)"connect_to_access_gateway",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5680_0x5680.c:29: v8 = send_access_gateway_local_key((__int64)v9, v5); /*0x5704*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5680_0x5680.c:32: v8 = recv_access_gateway_key(*v9, &v6, &v7, v9[21]); /*0x5731*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5680_0x5680.c:34: return (unsigned int)send_access_gateway_connect_info(v9, v5, v6, v7, v2, v3); /*0x5754*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5fc0_0x5fc0.c:2: __int64 __fastcall generate_http_msg(__int64 a1, int a2, __int64 a3, int a4)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5fc0_0x5fc0.c:10: (unsigned int)"CONNECT [%s]:%d HTTP/1.1\r\n"`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5fc0_0x5fc0.c:24: (unsigned int)"CONNECT %s:%d HTTP/1.1\r\n"`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5fc0_0x5fc0.c:41: (unsigned int)"CONNECT [%s]:%d HTTP/1.1\r\nHost: %s:%d\r\nProxy-Connection: keep-alive\r\n\r\n",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x5fc0_0x5fc0.c:52: (unsigned int)"CONNECT %s:%d HTTP/1.1\r\nHost: %s:%d\r\nProxy-Connection: keep-alive\r\n\r\n",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:2: __int64 __fastcall create_http_tunnel_proxy(int a1, __int64 a2, int a3, __int64 a4, int a5)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:48: (unsigned int)"create_http_tunnel_proxy",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:50: (unsigned int)"create_http_tunnel_proxy begin sock_fd %d",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:57: generate_http_msg(a2, v26, v25, (int)__b); /*0x625f*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:81: (unsigned int)"create_http_tunnel_proxy",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:109: (unsigned int)"create_http_tunnel_proxy",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:120: (unsigned int)"create_http_tunnel_proxy",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:131: (unsigned int)"create_http_tunnel_proxy",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:133: (unsigned int)"create_http_tunnel_proxy end sock_fd %d",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x61b0_0x61b0.c:140: write_log((unsigned int)"create_http_tunnel_proxy", 1132, (unsigned int)"msg send failed! result %d", v21, v8, v9); /*0x62d7*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:2: __int64 __fastcall tn_deal_aes_code(__int64 a1, unsigned int a2, __int64 a3, int a4, int a5, char a6, int a7)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:16: AES_KEY key; // [rsp+78h] [rbp-198h] BYREF`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:75: AES_set_decrypt_key(userKey, (unsigned __int8)a7 << 7, &key); /*0x71af*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:79: AES_cbc_encrypt( /*0x7247*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:87: AES_decrypt( /*0x7208*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:96: AES_set_encrypt_key(userKey, (unsigned __int8)a7 << 7, &key); /*0x70db*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:100: AES_cbc_encrypt( /*0x7176*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x6e90_0x6e90.c:108: AES_encrypt( /*0x7134*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libcag/0x72a0_0x72a0.c:2: void xor_with_key()`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x131910_0x131910.c:2: __int64 __fastcall buildCAGParam(int a1, const std::string *a2, unsigned int a3, __int64 a4)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x131910_0x131910.c:46: strcpy(v35, "--guest-usr "); /*0x13194f*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x131910_0x131910.c:76: write_log(3, 0, "buildCAGParam", 6113, "buildCAGParam fail, get usename or password fail."); /*0x131a8f*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x131910_0x131910.c:175: "buildCAGParam",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x131910_0x131910.c:188: "buildCAGParam",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:2: void __fastcall ClientManager::StartSpiceProcess(__int64 a1, const std::string *a2, _DWORD *a3, unsigned int a4)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:153: write_log(0, 0, "StartSpiceProcess", 1458, "StartSpiceProcess test1"); /*0x172e9*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:173: v19 = AesDecodeConnStrFromCsap(data, v18, v16, (unsigned int)(v18 + 1)); /*0x17369*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:174: write_log(0, 0, "StartSpiceProcess", 1468, "StartSpiceProcess AesDecodeConnStrFromCsap ret:%d", v19); /*0x17387*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:225: "Failed to connect to desktop, please click to connect to desktop again [Error code: 20042]");`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:378: strcpy(v88, "--guest-usr "); /*0x17842*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:387: strcpy(v90, "--guest-passwd "); /*0x178b2*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:422: write_log(0, 0, "StartSpiceProcess", 1522, "StartSpiceProcess AddConnectParm cmd:%s", v43); /*0x17a63*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:442: write_log(1, 0, "StartSpiceProcess", 1555, "handle:%p buf:%p", v93, v94); /*0x17d16*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:461: write_log(1, 0, "StartSpiceProcess", 1588, "--vmid %s", v51); /*0x17dac*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x17220_0x17220.c:548: ClientManager::StartSpiceProcessinSandBox(v25, &__str); /*0x17b1a*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x1cff0_0x1cff0.c:2: _DWORD *__fastcall ClientManager::ConnectStrAesEncode(__int64 a1, unsigned __int8 *a2)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x1cff0_0x1cff0.c:147: write_log(1, 0, "ConnectStrAesEncode", 1186, "nRandom:%d len:%d", v32, v27); /*0x1d26d*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x1cff0_0x1cff0.c:148: CBC_AESEncryptStr(v26, v27, v33, v32, v32 - 1, 1); /*0x1d289*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x23940_0x23940.c:2: __int64 __fastcall ClientManager::AddCagAndInternalParm(ClientManager *a1, unsigned __int8 *a2, int a3, _DWORD *a4)`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x23940_0x23940.c:404: "AddCagAndInternalParm",`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x23940_0x23940.c:536: write_log(3, 0, "AddCagAndInternalParm", 1909, "CAG: get cag for VDI failed,telnetCagConnectPoolNet !");`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x23940_0x23940.c:546: write_log(3, 0, "AddCagAndInternalParm", 1913, "CAG: get cag for VDI failed!");`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x4def0_0x4def0.c:268: AesCbcEncode(&v85, &v76); /*0x4e430*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x4def0_0x4def0.c:306: AesCbcEncode(v67, &v78); /*0x4e54a*/`
- `/Users/zxc/Desktop/移动云电脑/cloudpc_analysis/ida_decompiled/libvdconn/0x4def0_0x4def0.c:373: AesEncodeForCsap(v56, (unsigned int)(v57 + ~(_DWORD)v56), *(_QWORD *)(v83 + 3608) + 3080LL, 1024, 1); /*0x4e6d6*/`

## 日志证据

- `https://point.soho.komect.com/point/custom/cc/v1`: 515
- `https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2`: 208
- `https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2`: 94
- `https://soho.komect.com/terminal/system/logReport/config/v2`: 78
- `https://soho.komect.com/terminal/cc/cloudPc/list/v6`: 55
- `https://soho.komect.com/terminal/cc/getFirmAuth/v1`: 33
- `https://soho.komect.com/terminal/cc/cloudPc/logout/v2`: 29
- `https://soho.komect.com/terminal/cc/cloudPc/notice`: 22
- `https://soho.komect.com/terminal/cc/getCustomerCenterPicUrl/v1`: 19
- `https://soho.komect.com/terminal/active/claimActivityList/v2`: 18
- `https://soho.komect.com/terminal/cc/checkVersion/v2`: 18
- `https://soho.komect.com/terminal/cc/collectInfo/v1`: 18
- `https://soho.komect.com/terminal/token/checkToken/v1`: 18
- `https://soho.komect.com/terminal/cc/get/feedbackUrl/v2`: 14
- `https://soho.komect.com/terminal/cc/getCommonManual/v1`: 14
- `https://soho.komect.com/terminal/cc/getPrivacyVersion/v1`: 14
- `https://soho.komect.com/terminal/login/encryptKey/v1`: 14
- `https://soho.komect.com/terminal/system/settings/v1`: 14
- `https://soho.komect.com/terminal/login/publicKey/v1`: 8
- `https://soho.komect.com/terminal/cc/cloudPc/detail/v1`: 6
- `https://soho.komect.com/terminal/login/logout/v1`: 6
- `https://soho.komect.com/terminal/login/namePwdLogin/v1`: 5
- `https://soho.komect.com/terminal/cc/cloudPc/sublist/v3`: 3
- `https://soho.komect.com/terminal/login/home/namePwdLogin/v1`: 2
- `https://soho.komect.com/terminal/cc/cloudPc/stickTop/v1`: 1
- `https://soho.komect.com/terminal/cc/getRebootAuth/v1`: 1
- `https://soho.komect.com/terminal/login/modifyUsername/v1`: 1
- `https://soho.komect.com/terminal/login/sms/login/v1`: 1
- `https://soho.komect.com/terminal/login/sms/send/v1`: 1

已在日志中发现厂商连接参数结构，以下只展示字段形态:
- `bizCode, cagIp, cagPort, scAuthCode, scgIp, scgTcpPort, scgUdpPort, spuCode, vmId, vmPassword, vmUserName, vmcIp, vmcPort`

云电脑列表返回结构摘要:
- `total=None`, `pageSize=None`
- `total=2`, `pageSize=100`
- `spuCode=zte-cloud-pc`, `skuName=2C4G版云电脑月包`, `skuSpec=CPU2核|内存4G`, `cloudPcType=1`, `vmStatusShow=运行中`, `serviceStatus=1`, `activate=1`
- `spuCode=zte-cloud-pc`, `skuName=8C16G版云电脑月包`, `skuSpec=CPU8核|内存16G`, `cloudPcType=1`, `vmStatusShow=运行中`, `serviceStatus=1`, `activate=1`
- `total=1`, `pageSize=100`
- `spuCode=zte-cloud-pc`, `skuName=2C4G版云电脑月包`, `skuSpec=CPU2核|内存4G`, `cloudPcType=1`, `vmStatusShow=运行中`, `serviceStatus=1`, `activate=1`
- `total=1`, `pageSize=100`
- `spuCode=zte-cloud-pc`, `skuName=移动云电脑资源包大众版A`, `skuSpec=CPU4核|内存8G`, `cloudPcType=1`, `vmStatusShow=运行中`, `serviceStatus=1`, `activate=1`

## 控制面时序

以下来自客户端日志，按出现顺序脱敏汇总；同一秒内多个埋点/接口可能并发。

- `2026-05-01 17:16:01.529` `request` https://soho.komect.com/terminal/login/encryptKey/v1
- `2026-05-01 17:16:01.534` `response` https://soho.komect.com/terminal/login/encryptKey/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:01.624` `response` https://soho.komect.com/terminal/cc/getPrivacyVersion/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:02.342` `response` https://soho.komect.com/terminal/system/settings/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:03.423` `response` https://soho.komect.com/terminal/cc/getCommonManual/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:03.476` `response` https://soho.komect.com/terminal/cc/get/feedbackUrl/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:04.992` `response` https://soho.komect.com/terminal/cc/checkVersion/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:05.601` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:08.468` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:20.806` `request` https://soho.komect.com/terminal/login/publicKey/v1
- `2026-05-01 17:16:20.809` `response` https://soho.komect.com/terminal/login/publicKey/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:20.854` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:20.894` `request` https://soho.komect.com/terminal/login/home/namePwdLogin/v1
- `2026-05-01 17:16:20.895` `response` https://soho.komect.com/terminal/login/home/namePwdLogin/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.037` `response` https://soho.komect.com/terminal/cc/collectInfo/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.045` `response` https://soho.komect.com/terminal/cc/collectInfo/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.092` `response` https://soho.komect.com/terminal/cc/getCustomerCenterPicUrl/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.102` `response` https://soho.komect.com/terminal/cc/collectInfo/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.743` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.780` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.791` `response` https://soho.komect.com/terminal/cc/cloudPc/notice -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.791` `cloud-list` total=None, items=0
- `2026-05-01 17:16:21.856` `request` https://soho.komect.com/terminal/cc/cloudPc/list/v6
- `2026-05-01 17:16:21.857` `response` https://soho.komect.com/terminal/cc/cloudPc/list/v6 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:21.857` `cloud-list` total=2, items=2
- `2026-05-01 17:16:21.943` `response` https://soho.komect.com/terminal/system/logReport/config/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:22.011` `request` https://soho.komect.com/terminal/token/checkToken/v1
- `2026-05-01 17:16:22.011` `response` https://soho.komect.com/terminal/token/checkToken/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:27.281` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:27.392` `request` https://soho.komect.com/terminal/cc/getFirmAuth/v1
- `2026-05-01 17:16:27.393` `response` https://soho.komect.com/terminal/cc/getFirmAuth/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:27.393` `credential-shape` bizCode, cagIp, cagPort, scAuthCode, scgIp, scgTcpPort, scgUdpPort, spuCode, vmId, vmPassword, vmUserName, vmcIp, vmcPort
- `2026-05-01 17:16:27.481` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:46.357` `native-callback` connect: iCode=0, msg=Success to Connectting desktop
- `2026-05-01 17:16:46.468` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:46.472` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:46.505` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:46.564` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:16:46.564` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:16:48.822` `request` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2
- `2026-05-01 17:16:48.827` `response` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:49.561` `native-callback` connect: iCode=0, msg=Success to Connect desktop
- `2026-05-01 17:16:49.618` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:49.620` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:49.624` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:16:49.687` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:16:49.687` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:16:51.110` `request` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2
- `2026-05-01 17:16:51.111` `response` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:17:20.201` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:17:20.259` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:17:20.259` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:17:51.717` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:17:51.844` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:17:51.846` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:18:23.201` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:18:23.320` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:18:23.321` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:18:53.117` `request` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2
- `2026-05-01 17:18:53.119` `response` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:18:54.304` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:18:54.400` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:18:54.400` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:19:26.178` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:19:26.254` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:19:26.254` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:19:34.959` `native-callback` disconnect: iCode=0, msg=Success to Disconnect desktop
- `2026-05-01 17:19:35.057` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:19:35.135` `request` https://soho.komect.com/terminal/cc/cloudPc/list/v6
- `2026-05-01 17:19:35.136` `response` https://soho.komect.com/terminal/cc/cloudPc/list/v6 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:19:35.136` `cloud-list` total=2, items=2
- `2026-05-01 17:19:35.198` `request` https://soho.komect.com/terminal/cc/cloudPc/logout/v2
- `2026-05-01 17:19:35.198` `response` https://soho.komect.com/terminal/cc/cloudPc/logout/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:19:39.194` `response` https://soho.komect.com/terminal/cc/cloudPc/detail/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:19:53.434` `response` https://soho.komect.com/terminal/cc/cloudPc/detail/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:00.357` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:00.555` `request` https://soho.komect.com/terminal/cc/getFirmAuth/v1
- `2026-05-01 17:20:00.557` `response` https://soho.komect.com/terminal/cc/getFirmAuth/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:00.557` `credential-shape` bizCode, cagIp, cagPort, scAuthCode, scgIp, scgTcpPort, scgUdpPort, spuCode, vmId, vmPassword, vmUserName, vmcIp, vmcPort
- `2026-05-01 17:20:00.646` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:02.219` `native-callback` connect: iCode=0, msg=Success to Connectting desktop
- `2026-05-01 17:20:02.294` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:02.352` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:02.381` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:02.657` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:20:02.657` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:20:03.145` `native-callback` connect: iCode=0, msg=Success to Connect desktop
- `2026-05-01 17:20:03.208` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:03.210` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:03.212` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:03.538` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:20:03.539` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:20:03.824` `request` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2
- `2026-05-01 17:20:03.825` `response` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:04.733` `request` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2
- `2026-05-01 17:20:04.733` `response` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:34.227` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:34.336` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:20:34.337` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:20:34.691` `native-callback` disconnect: iCode=0, msg=Success to Disconnect desktop
- `2026-05-01 17:20:34.776` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:34.787` `request` https://soho.komect.com/terminal/cc/cloudPc/logout/v2
- `2026-05-01 17:20:34.788` `response` https://soho.komect.com/terminal/cc/cloudPc/logout/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:34.885` `request` https://soho.komect.com/terminal/cc/cloudPc/list/v6
- `2026-05-01 17:20:34.887` `response` https://soho.komect.com/terminal/cc/cloudPc/list/v6 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:34.887` `cloud-list` total=2, items=2
- `2026-05-01 17:20:38.388` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:38.486` `request` https://soho.komect.com/terminal/cc/getFirmAuth/v1
- `2026-05-01 17:20:38.486` `response` https://soho.komect.com/terminal/cc/getFirmAuth/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:38.486` `credential-shape` bizCode, cagIp, cagPort, scAuthCode, scgIp, scgTcpPort, scgUdpPort, spuCode, vmId, vmPassword, vmUserName, vmcIp, vmcPort
- `2026-05-01 17:20:38.538` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:39.977` `native-callback` connect: iCode=0, msg=Success to Connectting desktop
- `2026-05-01 17:20:40.074` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:40.075` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:40.148` `request` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2
- `2026-05-01 17:20:40.148` `response` https://soho.komect.com/terminal/cc/cloudPc/heartbeat/v2 -> code=4041, msg=当前云电脑处于解锁状态,且无密码(A90020129)
- `2026-05-01 17:20:41.575` `request` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2
- `2026-05-01 17:20:41.577` `response` https://soho.komect.com/terminal/cc/cloudPc/infoReport/v2 -> code=2000, msg=SUCCESS(A2000)
- `2026-05-01 17:20:42.870` `native-callback` connect: iCode=0, msg=Success to Connect desktop
- `2026-05-01 17:20:42.922` `response` https://point.soho.komect.com/point/custom/cc/v1 -> code=2000, msg=SUCCESS(A2000)
- `...` 后续事件已省略，可看 `evidence/*.redacted.log`。

日志中出现的数据面/网关线索，供抓包过滤器使用:
- `10.21.2.232`
- `192.168.5.14`
- `2409:8c70:3a50:22eb::535`
- `36.133.100.80`
- `39.173.116.232`
- `6794`
- `8443`
- `8899`

## 抓包建议

需要抓包，但目标不是破解 HTTPS 内容，也不是复刻保活客户端，而是确认 native 数据面连接到哪些网关、端口、协议以及连接时序。控制面接口在客户端日志里已经比较完整；数据面在 native 进程里，必须结合 pcap、`lsof` 和 SDK 日志看。

建议流程:

1. 先退出客户端，清空或备份旧日志。
2. 运行本脚本 `--capture --launch --seconds 300`。
3. 在 300 秒内手动完成登录、点击连接、进入桌面、操作鼠标键盘、断开连接。
4. 查看 `REPORT.md`、`connections.log`、`cloudpc_login_to_control.pcap`、`evidence/*.redacted.log`。
5. 对 ZTE 成功连接，优先校验 UDP/KCP 与日志中的 `IKCP_CONV_*`、`TLS1.3`、`send_tunnel_add_link` 时间戳关系。

抓包过滤器:

```tcpdump
(host 10.21.2.232 or host 111.1.51.48 or host 112.13.92.159 or host 112.17.28.226 or host 112.17.28.241 or host 192.168.5.14 or host 2409:8c70:3a50:22eb::535 or host 36.133.100.80 or host 39.173.116.232 or port 443 or port 1443 or port 5100 or port 6794 or port 8443 or port 8899 or port 60065)
```
