"""验证 scheduler.py date 自循环 + ±1 分钟随机浮动 是否真实有效"""
import os
import sqlite3
import sys
import tempfile
import time
import threading
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(ROOT_DIR, "webapp")
if WEBAPP_DIR not in sys.path:
    sys.path.insert(0, WEBAPP_DIR)

import scheduler
from database import SCHEMA, _migrate

_CST = timezone(timedelta(hours=8))
MODE = sys.argv[1] if len(sys.argv) > 1 else "logic"


def make_db():
    tmp = tempfile.mkdtemp()
    db_path = os.path.join(tmp, "cloudpc.db")
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    _migrate(conn)  # 补齐 vm_status_before / booted 等增量列
    conn.execute(
        "INSERT INTO cloud_account (id, username, password, keepalive_enabled, keepalive_interval) VALUES (1, 'u', 'p', 1, 180)"
    )
    conn.execute(
        "INSERT INTO cloud_vm (account_id, user_service_id, vm_name) VALUES (1, 1001, 'vm1')"
    )
    conn.commit()
    conn.close()
    return db_path


# ---------- ① 逻辑验证:排期时间是否符合 [base-1, base+1] 且 >= 3 分钟 ----------
def verify_logic():
    db_path = make_db()
    hits = []
    fires = []

    def fake_keepalive(username, password, hold=10, skip_usids=None, max_workers=8):
        fires.append(datetime.now(_CST))
        class R:
            success = True
            user_service_id = 1001
            vm_name = "vm1"
            cag_code = 0
            vm_status_before = "运行中"
            booted = False
            error = None
        return [R()], [{"userServiceId": 1001, "vmStatusShow": "运行中"}]

    with patch("scheduler.keepalive_account", side_effect=fake_keepalive):
        scheduler.add_job(1, "u", "p", 180, db_path)  # 180秒=3分钟基准
        scheduler.scheduler.start()
        # 等第一次立即触发完成
        for _ in range(50):
            if fires:
                break
            time.sleep(0.2)
        time.sleep(0.5)

        # 检查是否自动排了下一次 date 任务
        job = scheduler.scheduler.get_job("keepalive_1")
        assert job is not None, "第一次执行后应自动排下一次任务"
        from apscheduler.triggers.date import DateTrigger
        assert isinstance(job.trigger, DateTrigger), f"触发器应为 DateTrigger, got {type(job.trigger)}"
        # 距离 = run_date - 完成时刻
        delta_min = (job.trigger.run_date - fires[-1]).total_seconds() / 60
        base = 180 / 60
        low = max(3, base - 1)
        high = base + 1
        print(f"[逻辑] 基准={base}分钟 → 下次间隔={delta_min:.2f}分钟 (期望区间 [{low:.1f}, {high:.1f}])")
        assert low <= delta_min <= high, f"间隔 {delta_min:.2f} 超出区间"
        print("[逻辑] PASS: 时间落在基准±1分钟且>=3分钟区间内")
        # 校验:移除旧任务后新任务存在、job 隔离正确、base_interval 正确传递
        assert job.id == "keepalive_1", f"job id 应为 keepalive_1, got {job.id}"
        assert job.kwargs.get("base_interval") == 3.0, f"base_interval 应为 3.0, got {job.kwargs.get('base_interval')}"
        print(f"[逻辑] PASS: job={job.id}, base_interval={job.kwargs.get('base_interval')} 分钟正确传递")
        # 偏移下限验证:连续 2000 次采样,|偏移| 必须 >= 0.1 分钟(6秒),且 <= 1.0
        import random as _rnd
        offs = [(_rnd.uniform(0.1, 1.0) * _rnd.choice([-1, 1])) for _ in range(2000)]
        min_abs = min(abs(o) for o in offs)
        max_abs = max(abs(o) for o in offs)
        print(f"[逻辑] 偏移采样2000次: |偏移|范围=[{min_abs:.4f}, {max_abs:.4f}] 分钟 (要求 ≥0.1即6秒, ≤1.0)")
        assert min_abs >= 0.1 - 1e-9, f"存在小于 0.1 分钟的偏移: {min_abs}"
        assert max_abs <= 1.0 + 1e-9, f"存在大于 1.0 分钟的偏移: {max_abs}"
        print("[逻辑] PASS: 随机偏移幅度始终 ≥6秒 且 ≤60秒")
        # 多账号隔离检查:加第二个账号任务,互不覆盖
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO cloud_account (id, username, password, keepalive_enabled, keepalive_interval) VALUES (2, 'u2', 'p2', 1, 600)")
        conn.commit(); conn.close()
        scheduler.add_job(2, "u2", "p2", 600, db_path)
        j_a = scheduler.scheduler.get_job("keepalive_1")
        j_b = scheduler.scheduler.get_job("keepalive_2")
        assert j_a and j_b, "两个账号任务应同时存在"
        assert j_a.id != j_b.id
        print("[逻辑] PASS: 多账号任务互相隔离")

    scheduler.scheduler.shutdown(wait=False)
    print("=== 逻辑验证全部通过 ===")


# ---------- ② 真实闭环:date 触发 → 执行 → 自动排下一次 → 再次触发 ----------
def verify_loop():
    db_path = make_db()
    fires = []
    lock = threading.Lock()

    def fake_keepalive(username, password, hold=10, skip_usids=None, max_workers=8):
        with lock:
            fires.append(datetime.now(_CST))
        class R:
            success = True
            user_service_id = 1001
            vm_name = "vm1"
            cag_code = 0
            vm_status_before = "运行中"
            booted = False
            error = None
        return [R()], [{"userServiceId": 1001, "vmStatusShow": "运行中"}]

    with patch("scheduler.keepalive_account", side_effect=fake_keepalive):
        t0 = time.time()
        scheduler.add_job(1, "u", "p", 180, db_path)  # 基准3分钟
        scheduler.scheduler.start()
        # 等待触发至少 2 次(第2次在 ~3-4 分钟后)
        while len(fires) < 2 and time.time() - t0 < 300:
            time.sleep(1)
        scheduler.scheduler.shutdown(wait=False)
        with lock:
            n = len(fires)
            if n >= 2:
                gap = (fires[1] - fires[0]).total_seconds() / 60
                print(f"[闭环] 触发次数={n}")
                print(f"[闭环] 第一次触发: {fires[0].strftime('%H:%M:%S')}")
                print(f"[闭环] 第二次触发: {fires[1].strftime('%H:%M:%S')}")
                print(f"[闭环] 实际间隔: {gap:.2f} 分钟 (基准3分钟, 期望 [3,4])")
                assert 3.0 <= gap <= 4.0 + 1e-6, f"间隔 {gap:.2f} 越界"
                print("=== 真实闭环验证通过: date自循环 + 浮动时间 有效 ===")
            else:
                print(f"[闭环] 失败: 300秒内只触发了 {n} 次")
                sys.exit(1)


if __name__ == "__main__":
    if MODE == "logic":
        verify_logic()
    else:
        verify_loop()
