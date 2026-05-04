"""APScheduler 后台保活调度"""
import sqlite3
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from keepalive_core import keepalive_account

LOG = logging.getLogger("scheduler")
scheduler = BackgroundScheduler(daemon=True, job_defaults={"coalesce": True, "max_instances": 1})


def _run_keepalive(account_id: int, username: str, password: str, db_path: str, hold: int = 10):
    """后台任务：执行保活并写日志到数据库"""
    LOG.info("[%s] 执行保活", username)
    results = keepalive_account(username, password, hold=hold)
    now = datetime.now().isoformat()
    status_summary = "success" if all(r.success for r in results) else "failed"

    conn = sqlite3.connect(db_path)
    try:
        for r in results:
            conn.execute(
                "INSERT INTO keepalive_log (account_id, vm_name, user_service_id, status, cag_reply_code, error_message) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (account_id, r.vm_name, r.user_service_id,
                 "success" if r.success else "failed", r.cag_code, r.error or None),
            )
        conn.execute(
            "UPDATE cloud_account SET last_keepalive_at=?, last_keepalive_status=? WHERE id=?",
            (now, status_summary, account_id),
        )
        conn.commit()
    finally:
        conn.close()

    for r in results:
        LOG.info("[%s] %s - %s", username, r.vm_name, "保活成功" if r.success else f"保活失败({r.error})")


def add_job(account_id: int, username: str, password: str, interval: int, db_path: str, hold: int = 10):
    job_id = f"keepalive_{account_id}"
    scheduler.add_job(
        func=_run_keepalive,
        trigger=IntervalTrigger(seconds=interval),
        id=job_id,
        replace_existing=True,
        args=[account_id, username, password, db_path, hold],
    )
    LOG.info("添加任务: %s interval=%ds", username, interval)


def remove_job(account_id: int):
    job_id = f"keepalive_{account_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


def reschedule_job(account_id: int, interval: int):
    job_id = f"keepalive_{account_id}"
    job = scheduler.get_job(job_id)
    if job:
        scheduler.reschedule_job(job_id, trigger=IntervalTrigger(seconds=interval))


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
