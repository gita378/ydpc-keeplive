# SC 家庭云电脑开机 - getConnectInfo RSA 调试状态

## 背景

移动云电脑当前分两条连接链路：

- ZTE 云电脑 (`zte-cloud-pc`): 开机与基础保活已实现
- 家庭云电脑 (`sc-cloud-pc`): SOHO 鉴权、SC OAuth、开机、ready 查询与基础保活已打通

## 已确认流程

1. SOHO login
2. `getFirmAuth(userServiceId)` 获取 `scAuthCode`、`vmId`、`bizCode`
3. `POST https://api.soho.komect.com:1443/gzs/auth/oauth/token`
   - `grant_type=ext`
   - `client_id=sc-user-5e38ece5`
   - `token=scAuthCode`
   - 返回 `access_token`
4. `GET https://api.soho.komect.com:1443/gzs/auth/oauth/rsa-public-key`
   - 返回 RSA-1024 公钥
   - 已确认等于 SDK 内置 `sdk1` 公钥
   - 但 `getConnectInfo` 实测必须使用 SDK 内置 `sdk2` 公钥
5. `POST https://api.soho.komect.com:1443/sc/open-portal/openapi/terminal/v1/getConnectInfo`
   - Body: `{"vmId":"{rsa}BASE64URL(RSA_PKCS1v15(vmIdString))"}`
   - 成功时返回 `traceId` / `scgIp` / `scgPort` 等连接参数，并触发/完成连接准备
6. `POST https://api.soho.komect.com:1443/sc/open-portal/openapi/terminal/v1/getVmReadyStatus`
   - Body: `{"vmId":"{rsa}BASE64URL(RSA_PKCS1v15(vmIdString))","traceId":"明文traceId"}`
   - `vmId` 仍然必须用 `sdk2` 公钥 RSA 加密；`traceId` 保持明文
7. SOHO heartbeat
   - 默认使用 `/terminal/cc/cloudPc/heartbeat/v1`，30 秒一跳
   - 官方 H5/SDK 会调用 `/heartbeat/v2`，但无密码解锁态可能返回 `4041`，可作为非致命响应观察

## /tmp/h5.log 的关键证据

`/tmp/h5.log` 中官方客户端成功样本：

```text
userServiceId=37268191
vmId=960490
bizCode=10002
connectVMID=960490
getConnectInfo returnCode=00000
getVMReadyStatus(vmID:"960490") readyStatus=1
```

官方 SC SDK 请求头：

```text
User-Agent: cdpsdk-macos-2.18.23(2.18.23.213)
gzs-client-id: sc-user-5e38ece5
sc-terminal-sn: J6V4WFH06C-62:99:6f:93:cd:dc
sc-unit-type: Mac17,9
sc-network-type: 2
```

官方 `base64ConnectVMID` 使用 URL-safe base64：

```text
base64url(RSA_PKCS1v15(utf8(vmId))).rstrip("=")
```

## 已排除或修正

- 不是标准 base64；官方使用 base64url 字母表 `-`、`_`
- 不是保留 padding；官方去掉末尾 `=`
- 不是 RSA-OAEP；官方 Swift/SwiftyRSA 调用 `kSecKeyAlgorithmRSAEncryptionPKCS1`
- `/gzs/auth/oauth/rsa-public-key` 与 SDK 内置 `sdk1` 公钥一致，但用于 `getConnectInfo` 会返回 `90010002`
- SDK 内置 `sdk2` 公钥用于 `getConnectInfo` 成功返回 `00000`
- `getVmReadyStatus` 不是明文 `vmId`；实测明文会返回 `90010002`，必须继续传 `{rsa}BASE64URL(RSA_PKCS1v15(vmId))`
- `getVmReadyStatus` 的 `traceId` 不能 RSA 加密，必须使用 `getConnectInfo` 返回的明文 `traceId`
- 不能只用默认 `--vm-index` 猜测目标 VM；应先对齐 `userServiceId` 与 `vmId`
- 新版头部不是旧文档里的 `sc-unit-type: Mac`，而是 `Mac17,9`

## 当前脚本

主脚本：

```text
cloudpc_sc_client.py
```

已实现：

- SOHO 登录复用 `cloudpc_protocol.py`
- 枚举 `sc-cloud-pc`
- `getFirmAuth`
- OAuth `grant_type=ext`
- RSA PKCS1v15 加密
- base64url 去 padding
- 可选 `getConnectInfo`
- 可选 `getVMReadyStatus`
- 可选 30 秒节奏 heartbeat 保活
- 默认使用 `sdk2` 公钥；可选 `api/sdk1` 与 `sdk2` 公钥 profile
- 可选 macOS Security.framework RSA 实现

## 建议验证顺序

先列出 SC VM 并确认 `firm_vmId`：

```bash
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --list-sc --probe-firm-auth
```

按 `/tmp/h5.log` 成功样本指定 `userServiceId`：

```bash
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --user-service-id 37268191 --connect-info --ready-status
```

如果仍返回 `90010002`，再做 A/B：

```bash
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --user-service-id 37268191 --public-key-profile api --connect-info
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --user-service-id 37268191 --rsa-provider security --connect-info
```

当前实测结论：

```text
api/sdk1 + cryptography -> 90010002
api/sdk1 + Security.framework -> 90010002
sdk2 + cryptography -> 00000
sdk2 getVmReadyStatus(encrypted vmId + plain traceId) -> 00000 readyStatus=1
heartbeat/v1 -> 2000 SUCCESS
```

## 保活命令

持续 10 分钟，每 30 秒发送一次 heartbeat，并顺带查询 ready 状态：

```bash
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --user-service-id 37268191 --connect-info --ready-status --keepalive-seconds 600 --heartbeat-interval 30
```

如果要完全对齐官方 H5 的 v2 心跳：

```bash
python3 cloudpc_sc_client.py --un "$UN" --pw "$PW" --user-service-id 37268191 --connect-info --ready-status --keepalive-seconds 600 --heartbeat-interval 30 --heartbeat-api v2
```

`v2` 返回 `4041 当前云电脑处于解锁状态,且无密码` 时不要直接当失败；官方日志也出现这个响应。

## 逆向留档

如果后续 SDK 版本变化，优先抓官方 SDK 的实际 `getConnectInfo` body：

```bash
frida -p <官方客户端PID> -l hook_sc_rsa_frida.js
```

hook 输出中的 `plain_ascii` 应为当前 `vmId`，`cipher_b64url` 应与官方日志 `base64ConnectVMID` 同格式。

敏感信息不要写入文档；账号、密码、token 统一通过环境变量或一次性终端输入传入。
