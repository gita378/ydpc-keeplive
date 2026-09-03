"""APScheduler 后台保活调度"""
import sqlite3
import logging
import random  # [改造] 新增:用于 ±1 分钟随机浮动
from datetime import datetime, timezone, timedelta

_CST = timezone(timedelta(hours=8))


def _now_cst() -> str:
    """返回北京时间 ISO 格式字符串"""
    return datetime.now(_CST).strftime("%Y-%m-%d %H:%M:%S")
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger  # [改造] interval 固定周期 → date 单次触发自循环
from keepalive_core import keepalive_account

LOG = logging.getLogger("scheduler")
scheduler = BackgroundScheduler(daemon=True, job_defaults={"coalesce": True, "max_instances": 1})


def _run_keepalive(account_id: int, username: str, password: str, db_path: str,
                   hold: int = 10, max_workers: int = 8, base_interval: float = None):
    """后台任务：执行保活并写日志 + 刷新 VM 状态到数据库"""
    # [改造] 本次保活运行完毕后,在函数尾部调度下一次(date 单次自循环)
    def schedule_next():
        if base_interval is None:
            return
        # [改造] 硬性约束①:浮动基于「本次实际完成时刻」,而非原计划时间推算
        # [改造] 偏移幅度 ∈ ±[0.1, 1] 分钟(即至少 6 秒,最大 60 秒),避免接近 0 的伪随机;
        #        下限强制 3 分钟,防请求过频
        offset = random.uniform(0.1, 1.0) * random.choice([-1, 1])
        next_minutes = max(3, base_interval + offset)
        next_run = datetime.now(_CST) + timedelta(minutes=next_minutes)
        # [改造] 移除本次已完成的旧 date 任务 → 新建下一次 date 单次任务(传递账号与基准间隔,闭环)
        remove_job(account_id)
        _add_date_job(account_id, username, password, db_path, hold, base_interval, next_run)

    LOG.info("[%s] 执行保活", username)
    # 检查是否到期
    conn_check = sqlite3.connect(db_path)
    row = conn_check.execute("SELECT expire_at FROM cloud_account WHERE id=?", (account_id,)).fetchone()
    conn_check.close()
    if row and row[0]:
        from datetime import datetime as _dt
        try:
            expire = _dt.fromisoformat(row[0])
            if _dt.now(_CST).replace(tzinfo=None) > expire:
                LOG.info("[%s] 账号已到期(%s)，跳过保活", username, row[0][:10])
                schedule_next()
                return
        except Exception:
            pass
    # 查询哪些 VM 需要保活
    conn_vm = sqlite3.connect(db_path)
    disabled_usids = set()
    for row in conn_vm.execute("SELECT user_service_id FROM cloud_vm WHERE account_id=? AND keepalive_enabled=0", (account_id,)).fetchall():
        disabled_usids.add(int(row[0]))
    conn_vm.close()

    try:
        results, fresh_vms = keepalive_account(
            username, password, hold=hold, skip_usids=disabled_usids, max_workers=max_workers
        )
    except Exception as e:
        LOG.error("[%s] 保活异常: %s", username, e)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute(
            "INSERT INTO keepalive_log (account_id, vm_name, user_service_id, status, error_message, executed_at) VALUES (?, ?, 0, 'failed', ?, ?)",
            (account_id, "SYSTEM", str(e), _now_cst()))
        conn.execute("UPDATE cloud_account SET last_keepalive_at=?, last_keepalive_status='failed' WHERE id=?",
                     (_now_cst(), account_id))
        conn.commit()
        conn.close()
        schedule_next()
        return
    now = _now_cst()
    status_summary = "success" if all(r.success for r in results) else "failed"

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        # 建 usid → VM 状态映射
        vm_map = {}
        if fresh_vms:
            for vm in fresh_vms:
                vm_map[int(vm.get("userServiceId", 0))] = vm
                # 同步更新 VM 的 keepalive_enabled 不影响（保持原值）
        for r in results:
            vm_info = vm_map.get(r.user_service_id, {})
            remain = vm_info.get("remainDurationTime")
            conn.execute(
                "INSERT INTO keepalive_log (account_id, vm_name, user_service_id, status, cag_reply_code, "
                "vm_status, remain_duration_time, error_message, vm_status_before, booted, executed_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (account_id, r.vm_name, r.user_service_id,
                 "success" if r.success else "failed", r.cag_code,
                 vm_info.get("vmStatusShow", ""),
                 str(remain) if remain is not None else None,
                 r.error or None, r.vm_status_before, int(r.booted), now),
            )
        conn.execute(
            "UPDATE cloud_account SET last_keepalive_at=?, last_keepalive_status=? WHERE id=?",
            (now, status_summary, account_id),
        )
        # 刷新 VM 状态和剩余时长
        if fresh_vms:
            import json
            for vm in fresh_vms:
                usid = int(vm.get("userServiceId", 0))
                conn.execute(
                    "UPDATE cloud_vm SET vm_status=?, remain_duration_time=?, raw_json=? "
                    "WHERE account_id=? AND user_service_id=?",
                    (vm.get("vmStatusShow", ""),
                     str(vm.get("remainDurationTime", "")) if vm.get("remainDurationTime") is not None else None,
                     json.dumps(vm, ensure_ascii=False),
                     account_id, usid),
                )
        conn.commit()
    finally:
        conn.close()

    for r in results:
        LOG.info("[%s] %s - %s", username, r.vm_name, "保活成功" if r.success else f"保活失败({r.error})")
    schedule_next()


def _add_date_job(account_id: int, username: str, password: str, db_path: str,
                  hold: int, base_interval: float, run_date: datetime):
    # [改造] 新增:以 date 单次触发器登记任务,基准间隔经 kwargs 传入执行函数
    job_id = f"keepalive_{account_id}"
    scheduler.add_job(
        func=_run_keepalive,
        trigger=DateTrigger(run_date=run_date),
        id=job_id,
        replace_existing=True,
        args=[account_id, username, password, db_path, hold],
        kwargs={"base_interval": base_interval},
    )


def add_job(account_id: int, username: str, password: str, interval: int, db_path: str, hold: int = 10):
    # [改造] 前端/数据库的 interval 以「秒」存储;浮动按「分钟」计算,故 ÷60 得基准分钟数
    # [改造] 开启保活 → 立即以 date 任务执行第一次保活(rule 2)
    base_interval = interval / 60
    _add_date_job(account_id, username, password, db_path, hold, base_interval, datetime.now(_CST))
    LOG.info("添加任务: %s interval=%ds", username, interval)


def remove_job(account_id: int):
    job_id = f"keepalive_{account_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


def reschedule_job(account_id: int, interval: int):
    # [改造] 用户改间隔时:换算基准分钟 → 重排为 date 单次任务,并同步执行函数里的 base_interval
    job_id = f"keepalive_{account_id}"
    job = scheduler.get_job(job_id)
    if job:
        base_interval = interval / 60
        next_run = datetime.now(_CST) + timedelta(minutes=max(3, base_interval))
        scheduler.reschedule_job(job_id, trigger=DateTrigger(run_date=next_run))
        job.modify(kwargs={"base_interval": base_interval})


def init_scheduler(app):
    """启动时加载所有已启用的保活任务"""
    db_path = app.config["DATABASE"]
    hold = app.config.get("HOLD_SECONDS", 10)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM cloud_account WHERE keepalive_enabled = 1").fetchall()
    conn.close()
    for row in rows:
        add_job(row["id"], row["username"], row["password"], row["keepalive_interval"], db_path, hold)
    scheduler.start()
    LOG.info("调度器启动, %d 个活跃任务", len(rows))
