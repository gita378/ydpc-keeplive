<img width="2642" height="1434" alt="image" src="https://github.com/user-attachments/assets/915de18e-fc4e-4937-b90c-2d4529b7e0c1" />
<img width="2698" height="1446" alt="image" src="https://github.com/user-attachments/assets/e30147fc-6431-4de8-ba17-bcc916359138" />
<img width="2718" height="1332" alt="image" src="https://github.com/user-attachments/assets/c6d52d42-e3d2-4f32-b11b-05b1a8d44c15" />

## 更新日志

### 2026-09-03：保活调度改造 + 清空日志 + 延长保持开关 + 全量状态日志

**0. 新增：未保活设备状态日志独立页 + 每次保活自动记录全量设备状态**
- **独立页 `/status-logs`**(导航栏「未保活状态」):仅展示未参与保活的设备(checked)状态日志,支持按账号/设备状态筛选、分页,字段精简(时间/账号/设备/状态/剩余时长)
- 每次保活任务执行时,除保活结果日志外,自动为未参与本次保活的 VM(单台关闭保活等)补记「状态检查」日志行
- 全部执行日志页仍可筛选「🔍 状态检查」
- 相关文件：`webapp/routes.py`、`webapp/scheduler.py`、`webapp/templates/status_logs.html`(新建)、`webapp/templates/logs.html`、`webapp/templates/base.html`

**1. 保活调度：interval 固定周期 → date 单次自循环（±1 分钟随机浮动）**
- 原逻辑：APScheduler `IntervalTrigger` 固定周期保活，节奏可预测，易被平台心跳风控识别
- 新逻辑：开启保活时立即执行第一次，每次保活**运行完成后**再排下一次 `date` 单次任务，形成自循环
- 随机浮动：基准间隔（用户网页填写值，前端未改动）+ `±[0.1, 1]` 分钟随机偏移（至少 6 秒、最多 60 秒，避免接近 0 的伪随机）
- 保护下限：任何情况下两次保活间隔不小于 3 分钟，杜绝请求过频
- 多账号任务互相隔离（`job_id = keepalive_{account_id}`），互不影响
- 关闭保活、删除任务逻辑保持不变
- 相关文件：`webapp/scheduler.py`

**2. 新增：清空执行日志功能**
- 执行日志页（`/logs`）新增「清空日志」按钮，一键清空全部保活日志（带二次确认）
- 新增后端路由 `POST /logs/clear`
- 相关文件：`webapp/routes.py`、`webapp/templates/logs.html`

**3. 新增：延长保持时间测试开关（导航栏全局）**
- 顶部导航栏新增「延长保持」开关：开启时保活连接保持时间在默认值（HOLD_SECONDS=10s）基础上 **+10 秒**；关闭恢复默认
- 开关状态存数据库（`settings` 表），重启不丢
- 对定时保活、手动保活、批量保活全部生效
- 相关文件：`webapp/database.py`、`webapp/app.py`、`webapp/routes.py`、`webapp/scheduler.py`、`webapp/templates/base.html`

### 验证
- `verify_scheduler.py`：逻辑验证（间隔区间、偏移下限 ≥6 秒、多账号隔离）与真实闭环验证（两次真实触发间隔实测通过）均已跑通
- 原单元测试 `test_webapp_keepalive_now.py` 通过
