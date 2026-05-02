# jiatingyun_pc_automation 仓库审计结论

仓库地址: `https://github.com/Rgoogle/jiatingyun_pc_automation`

## 结论

该仓库不是协议级实现，也没有还原 CAG/SPICE 私有认证包。它的方案是：

```text
Docker Ubuntu 20.04
-> 安装官方 Linux vdi-client.deb
-> Xvfb/openbox 提供虚拟桌面
-> x11vnc/noVNC 提供可视化访问
-> Playwright/CDP 自动登录官方客户端
-> 检测 uSmartView 进程
-> 会话中周期性派发鼠标移动事件
```

这属于“官方客户端黑盒自动化”，不是“远程连接协议还原”。

## 仓库结构

- `vdi_release/source_install/install.sh`: 多实例 Docker 启动脚本，按实例 ID 映射 `5900+n` 和 `6080+n`。
- `vdi_release/source_install/docker/Dockerfile`: 构建 Ubuntu GUI 容器，安装 Xvfb、openbox、x11vnc、noVNC、Playwright、pyautogui 等依赖。
- `vdi_release/source_install/config/credentials.conf`: 保存手机号、密码、连接索引、保活间隔、VNC/noVNC 开关。
- `vdi_release/source_install/config/supervisord.conf`: 启动 Xvfb、openbox、x11vnc、noVNC、官方 VDI 客户端和自动化脚本。
- `vdi_release/source_install/automation/vdi_automation_jty.py`: 家庭云电脑自动化状态机。
- `vdi_stealth_toolkit/src/stealth_injector.c`: `LD_PRELOAD` 注入器，用于给 Electron 主进程追加远程调试和 sandbox 参数。

## 自动化状态机

`vdi_automation_jty.py` 的核心状态：

- `LOGIN`: 登录页，填账号密码并点击登录。
- `DESKTOP_LIST`: 云电脑列表页，点击指定 `connect_index` 的连接按钮。
- `CONNECTING`: 连接中，超时后刷新 UI。
- `IN_SESSION`: 检测到 `uSmartView` 进程后认为进入会话。
- `WAIT`: 检测到其他设备登录、已分配、已回收等冲突文案后等待。
- `ZOMBIE`: 检测到僵尸进程后杀掉 viewer。
- `UNKNOWN`: 页面异常或 CDP 无响应，超时后刷新或重启组件。

该脚本通过 Chromium DevTools Protocol 操作官方客户端 UI，包括：

- 读取页面 URL 和 DOM。
- 按选择器计算元素坐标。
- 派发鼠标点击。
- 向输入框插入账号和密码。
- 会话中按随机间隔派发鼠标移动事件。

## 风险点

1. 仓库没有 LICENSE 文件，直接复制代码有版权风险。
2. `credentials.conf` 明文保存手机号和密码。
3. 默认 VNC 密码较弱，且 noVNC 暴露后风险很高。
4. 容器使用 `--cap-add=NET_ADMIN`、`--cap-add=SYS_ADMIN`、`seccomp=unconfined`，权限过大。
5. `entrypoint.sh` 包含反检测和进程名伪装逻辑，会删除容器标记并伪装 supervisor。
6. `libudev-shim.so` 与 `vdi_stealth_toolkit` 里的二进制哈希一致，是 `LD_PRELOAD` 注入器。
7. `stealth_injector.c` 会拦截 `__libc_start_main`，给目标 Electron 主进程追加 `--remote-debugging-port=9222`、`--no-sandbox`、`--remote-allow-origins=*`。
8. `--remote-allow-origins=*` 与开放 CDP 端口组合会扩大本机攻击面。
9. 自动化保活是鼠标移动，不是官方 24h 能力或协议能力证明。

## 对当前协议分析的价值

可参考：

- 官方 Linux 客户端的 Docker 运行依赖列表。
- 官方客户端启动、登录、连接、断线重启的状态机思路。
- 用 `uSmartView` 进程存在与否判断是否进入远控会话。
- 多实例目录隔离和端口映射思路。

不建议参考：

- `LD_PRELOAD` stealth 注入器。
- 反检测/伪装容器环境逻辑。
- 明文密码配置。
- 鼠标随机移动式保活作为协议结论。

## 与本地 macOS 样本的关系

该仓库使用 Linux 官方客户端；本地样本是 macOS Electron 客户端。两者控制面和业务流程相似：

```text
登录 -> 云电脑列表 -> getFirmAuth/厂商参数 -> native viewer -> 心跳/上报
```

但数据面实现可能有平台差异。当前本地日志确认的是 ZTE 分支：

```text
chuanyunAddOn-zte -> chuanyunsdk.node -> libvdconn.dylib -> libcag.dylib -> uSmartView/SPICE
```

该仓库没有提供比 IDA/本地日志更多的 CAG/SPICE 协议字段信息。

## 建议路线

如果目标是合规使用官方 24h 能力，应优先找官方文档、套餐说明或客户端内的正式开关/API。这个仓库只能证明“有人用官方客户端容器 + UI 自动化跑起来”，不能证明“官方开放了协议级保活接口”。

如果要做工程化的官方客户端托管，建议只保留这些安全部分：

- Docker 跑官方客户端。
- Xvfb/openbox/noVNC 可视化。
- supervisor 拉起进程。
- 自动登录状态机。
- 日志和健康检查。

同时删除或替换：

- `LD_PRELOAD` 注入器。
- 反检测/进程伪装逻辑。
- 明文密码文件。
- 随机鼠标移动保活逻辑。

