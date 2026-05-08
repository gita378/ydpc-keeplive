import json
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from database import get_db
from auth import login_required
from keepalive_core import soho_login, fetch_vm_list, keepalive_account, boot_vm

_CST = timezone(timedelta(hours=8))


def _now_cst() -> str:
    return datetime.now(_CST).strftime("%Y-%m-%d %H:%M:%S")
from scheduler import add_job, remove_job, reschedule_job

main_bp = Blueprint("main", __name__)

INTERVAL_OPTIONS = [
    (600, "10 分钟"),
    (1200, "20 分钟"),
    (1680, "28 分钟 (推荐)"),
    (3600, "1 小时"),
    (21600, "6 小时"),
    (43200, "12 小时"),
]


@main_bp.route("/")
@login_required
def index():
    db = get_db()
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    allowed_sorts = {
        "username": "a.username",
        "remark": "a.remark",
        "vm_count": "vm_count",
        "keepalive": "a.keepalive_enabled",
        "interval": "a.keepalive_interval",
        "expire": "a.expire_at",
        "last": "a.last_keepalive_at",
        "id": "a.id",
    }
    sort_col = allowed_sorts.get(sort, "a.id")
    order_dir = "DESC" if order == "desc" else "ASC"
    accounts_raw = db.execute(
        f"SELECT a.*, "
        f"(SELECT COUNT(*) FROM cloud_vm WHERE account_id=a.id) as vm_count, "
        f"(SELECT COUNT(*) FROM cloud_vm WHERE account_id=a.id AND keepalive_enabled=1) as vm_keepalive_count, "
        f"(SELECT COUNT(*) FROM cloud_vm WHERE account_id=a.id AND vm_status='运行中') as vm_running, "
        f"(SELECT COUNT(*) FROM cloud_vm WHERE account_id=a.id AND vm_status='已关机') as vm_off "
        f"FROM cloud_account a ORDER BY {sort_col} {order_dir}"
    ).fetchall()
    accounts = [dict(a) for a in accounts_raw]
    return render_template("accounts.html", accounts=accounts, intervals=INTERVAL_OPTIONS,
                           current_sort=sort, current_order=order,
                           now_date=datetime.now(_CST).strftime("%Y-%m-%d"))


@main_bp.route("/accounts/add", methods=["POST"])
@login_required
def add_account():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    remark = request.form.get("remark", "").strip()
    if not username or not password:
        flash("账号和密码不能为空", "danger")
        return redirect(url_for("main.index"))

    db = get_db()
    existing = db.execute("SELECT id FROM cloud_account WHERE username=?", (username,)).fetchone()
    if existing:
        flash(f"账号 {username} 已存在", "warning")
        return redirect(url_for("main.index"))

    # 尝试登录验证
    try:
        client = soho_login(username, password)
        vms = fetch_vm_list(client)
    except Exception as e:
        flash(f"登录失败: {e}", "danger")
        return redirect(url_for("main.index"))

    # 写入数据库
    cur = db.execute(
        "INSERT INTO cloud_account (username, password, remark, last_login_at) VALUES (?, ?, ?, ?)",
        (username, password, remark, _now_cst()),
    )
    account_id = cur.lastrowid

    # 写入云电脑列表
    for vm in vms:
        db.execute(
            "INSERT INTO cloud_vm (account_id, user_service_id, vm_name, spu_code, sku_name, "
            "vm_status, remain_duration_time, cpu, memory, raw_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                account_id,
                vm.get("userServiceId"),
                vm.get("vmName"),
                vm.get("spuCode"),
                vm.get("skuName"),
                vm.get("vmStatusShow"),
                str(vm.get("remainDurationTime") or ""),
                vm.get("cpu"),
                vm.get("memory"),
                json.dumps(vm, ensure_ascii=False),
            ),
        )
    db.commit()
    flash(f"添加成功: {username} ({len(vms)} 台云电脑)", "success")
    return redirect(url_for("main.index"))


@main_bp.route("/accounts/<int:aid>/delete", methods=["POST"])
@login_required
def delete_account(aid):
    db = get_db()
    remove_job(aid)
    db.execute("DELETE FROM cloud_vm WHERE account_id=?", (aid,))
    db.execute("DELETE FROM keepalive_log WHERE account_id=?", (aid,))
    db.execute("DELETE FROM cloud_account WHERE id=?", (aid,))
    db.commit()
    flash("已删除", "success")
    return redirect(url_for("main.index"))


@main_bp.route("/accounts/<int:aid>")
@login_required
def account_detail(aid):
    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    if not account:
        flash("账号不存在", "danger")
        return redirect(url_for("main.index"))
    vms_raw = db.execute("SELECT * FROM cloud_vm WHERE account_id=? ORDER BY id", (aid,)).fetchall()
    # 解析 raw_json 提取 skuSpecStr
    vms = []
    for vm in vms_raw:
        vm_dict = dict(vm)
        try:
            raw = json.loads(vm["raw_json"]) if vm["raw_json"] else {}
            vm_dict["sku_spec_str"] = raw.get("skuSpecStr", "")
            vm_dict["spu_name"] = raw.get("spuName", "")
        except Exception:
            vm_dict["sku_spec_str"] = ""
            vm_dict["spu_name"] = ""
        vms.append(vm_dict)
    logs = db.execute(
        "SELECT * FROM keepalive_log WHERE account_id=? ORDER BY executed_at DESC LIMIT 20", (aid,)
    ).fetchall()
    return render_template("account_detail.html", account=account, vms=vms, logs=logs,
                           intervals=INTERVAL_OPTIONS, now_date=datetime.now().strftime("%Y-%m-%d"))


@main_bp.route("/accounts/<int:aid>/edit", methods=["POST"])
@login_required
def edit_account(aid):
    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    if not account:
        flash("账号不存在", "danger")
        return redirect(url_for("main.index"))
    new_username = request.form.get("username", "").strip()
    new_password = request.form.get("password", "").strip()
    if not new_username or not new_password:
        flash("账号和密码不能为空", "danger")
        return redirect(url_for("main.index"))
    # 验证新密码能登录
    try:
        client = soho_login(new_username, new_password)
    except Exception as e:
        flash(f"验证失败（请确认账号密码正确）: {e}", "danger")
        return redirect(url_for("main.index"))
    db.execute("UPDATE cloud_account SET username=?, password=? WHERE id=?", (new_username, new_password, aid))
    db.commit()
    # 如果保活任务在跑，更新它
    if account["keepalive_enabled"]:
        remove_job(aid)
        add_job(aid, new_username, new_password, account["keepalive_interval"],
                current_app.config["DATABASE"], current_app.config.get("HOLD_SECONDS", 10))
    flash("账号密码修改成功", "success")
    return redirect(url_for("main.index"))


@main_bp.route("/accounts/<int:aid>/refresh", methods=["POST"])
@login_required
def refresh_vms(aid):
    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    if not account:
        flash("账号不存在", "danger")
        return redirect(url_for("main.index"))
    try:
        client = soho_login(account["username"], account["password"])
        vms = fetch_vm_list(client)
    except Exception as e:
        flash(f"刷新失败: {e}", "danger")
        return redirect(url_for("main.account_detail", aid=aid))

    # 保留 VM 保活开关状态
    old_ka = {r["user_service_id"]: r["keepalive_enabled"] for r in
              db.execute("SELECT user_service_id, keepalive_enabled FROM cloud_vm WHERE account_id=?", (aid,)).fetchall()}
    db.execute("DELETE FROM cloud_vm WHERE account_id=?", (aid,))
    for vm in vms:
        db.execute(
            "INSERT INTO cloud_vm (account_id, user_service_id, vm_name, spu_code, sku_name, "
            "vm_status, remain_duration_time, cpu, memory, raw_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (aid, vm.get("userServiceId"), vm.get("vmName"), vm.get("spuCode"),
             vm.get("skuName"), vm.get("vmStatusShow"),
             str(vm.get("remainDurationTime") or ""), vm.get("cpu"), vm.get("memory"),
             json.dumps(vm, ensure_ascii=False)),
        )
    # 恢复保活开关
    for usid, ka in old_ka.items():
        db.execute("UPDATE cloud_vm SET keepalive_enabled=? WHERE account_id=? AND user_service_id=?", (ka, aid, usid))
    db.execute("UPDATE cloud_account SET last_login_at=? WHERE id=?", (_now_cst(), aid))
    db.commit()
    flash(f"刷新成功 ({len(vms)} 台)", "success")
    return redirect(url_for("main.account_detail", aid=aid))


@main_bp.route("/accounts/<int:aid>/toggle", methods=["POST"])
@login_required
def toggle_keepalive(aid):
    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    if not account:
        return redirect(url_for("main.index"))

    new_state = 0 if account["keepalive_enabled"] else 1
    db.execute("UPDATE cloud_account SET keepalive_enabled=? WHERE id=?", (new_state, aid))
    db.commit()

    db_path = current_app.config["DATABASE"]
    hold = current_app.config.get("HOLD_SECONDS", 10)
    if new_state:
        add_job(aid, account["username"], account["password"], account["keepalive_interval"], db_path, hold)
        flash("保活已开启", "success")
    else:
        remove_job(aid)
        flash("保活已关闭", "info")
    return redirect(url_for("main.account_detail", aid=aid))


@main_bp.route("/accounts/<int:aid>/interval", methods=["POST"])
@login_required
def set_interval(aid):
    try:
        interval = int(request.form.get("interval", 600))
    except (ValueError, TypeError):
        interval = 600
    if interval not in [v for v, _ in INTERVAL_OPTIONS]:
        interval = 600
    db = get_db()
    db.execute("UPDATE cloud_account SET keepalive_interval=? WHERE id=?", (interval, aid))
    db.commit()
    reschedule_job(aid, interval)
    flash(f"间隔已设为 {interval // 60} 分钟", "success")
    return redirect(url_for("main.account_detail", aid=aid))


@main_bp.route("/accounts/<int:aid>/expire", methods=["POST"])
@login_required
def set_expire(aid):

    from datetime import timedelta
    db = get_db()
    expire_type = request.form.get("expire_type", "")
    custom_date = request.form.get("custom_date", "").strip()

    if expire_type == "never":
        expire_at = None
    elif expire_type == "custom" and custom_date:
        expire_at = custom_date + "T23:59:59"
    elif expire_type:
        days_map = {"1d": 1, "1w": 7, "1m": 30, "1y": 365}
        days = days_map.get(expire_type, 0)
        expire_at = (datetime.now(_CST) + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S") if days else None
    else:
        expire_at = None

    db.execute("UPDATE cloud_account SET expire_at=? WHERE id=?", (expire_at, aid))
    db.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "expire_at": expire_at[:10] if expire_at else None,
                        "msg": f"到期: {expire_at[:10]}" if expire_at else "永不过期"})

    flash(f"到期时间设为 {expire_at[:10]}" if expire_at else "已设为永不过期", "success")
    referrer = request.referrer or url_for("main.index")
    return redirect(referrer)


@main_bp.route("/accounts/<int:aid>/vm/<int:vmid>/toggle-keepalive", methods=["POST"])
@login_required
def toggle_vm_keepalive(aid, vmid):

    db = get_db()
    vm = db.execute("SELECT * FROM cloud_vm WHERE id=? AND account_id=?", (vmid, aid)).fetchone()
    if not vm:
        return jsonify({"success": False, "msg": "云电脑不存在"}), 404
    new_state = 0 if vm["keepalive_enabled"] else 1
    db.execute("UPDATE cloud_vm SET keepalive_enabled=? WHERE id=?", (new_state, vmid))
    db.commit()
    return jsonify({"success": True, "enabled": bool(new_state),
                    "msg": f"{vm['vm_name']}: {'开启' if new_state else '关闭'}保活"})


@main_bp.route("/accounts/<int:aid>/vm/<int:vmid>/boot", methods=["POST"])
@login_required
def boot_vm_route(aid, vmid):
    """单台云电脑开机"""

    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    vm_row = db.execute("SELECT * FROM cloud_vm WHERE id=? AND account_id=?", (vmid, aid)).fetchone()
    if not account or not vm_row:
        return jsonify({"success": False, "msg": "账号或云电脑不存在"}), 404

    try:
        client = soho_login(account["username"], account["password"])
        vm_dict = json.loads(vm_row["raw_json"]) if vm_row["raw_json"] else {
            "userServiceId": vm_row["user_service_id"], "vmName": vm_row["vm_name"], "vmStatus": 23
        }
        ok, msg = boot_vm(client, vm_dict)
        if ok:
            db.execute("UPDATE cloud_vm SET vm_status='运行中' WHERE id=?", (vmid,))
            db.commit()
        return jsonify({"success": ok, "msg": msg})
    except Exception as e:
        return jsonify({"success": False, "msg": f"开机出错: {e}"}), 500


@main_bp.route("/accounts/<int:aid>/boot-all", methods=["POST"])
@login_required
def boot_all_vms(aid):
    """账号下所有关机 VM 全部开机"""

    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    if not account:
        return jsonify({"success": False, "msg": "账号不存在"}), 404

    try:
        client = soho_login(account["username"], account["password"])
        vms = fetch_vm_list(client)
        results = []
        for vm in vms:
            vm_status = vm.get("vmStatus")
            if vm_status in (23, "23"):
                ok, msg = boot_vm(client, vm)
                results.append(msg)
                if ok:
                    db.execute(
                        "UPDATE cloud_vm SET vm_status='运行中' WHERE account_id=? AND user_service_id=?",
                        (aid, int(vm["userServiceId"]))
                    )
        db.commit()
        if not results:
            return jsonify({"success": True, "msg": "所有 VM 已在运行中"})
        return jsonify({"success": True, "msg": " | ".join(results)})
    except Exception as e:
        return jsonify({"success": False, "msg": f"开机出错: {e}"}), 500


@main_bp.route("/accounts/<int:aid>/vm/<int:vmid>/keepalive", methods=["POST"])
@login_required
def keepalive_vm(aid, vmid):
    """单台云电脑保活（支持 AJAX）"""

    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    vm_row = db.execute("SELECT * FROM cloud_vm WHERE id=? AND account_id=?", (vmid, aid)).fetchone()
    if not account or not vm_row:
        return jsonify({"success": False, "msg": "账号或云电脑不存��"}), 404

    from keepalive_core import soho_login, keepalive_single_vm
    try:
        client = soho_login(account["username"], account["password"])
        vm_dict = json.loads(vm_row["raw_json"]) if vm_row["raw_json"] else {"userServiceId": vm_row["user_service_id"], "vmName": vm_row["vm_name"]}
        result = keepalive_single_vm(client, vm_dict, hold=current_app.config.get("HOLD_SECONDS", 10))
        now = _now_cst()
        db.execute(
            "INSERT INTO keepalive_log (account_id, vm_name, user_service_id, status, cag_reply_code, "
            "error_message, vm_status_before, booted, executed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (aid, result.vm_name, result.user_service_id,
             "success" if result.success else "failed", result.cag_code, result.error or None,
             result.vm_status_before, int(result.booted), now),
        )
        db.execute("UPDATE cloud_account SET last_keepalive_at=?, last_keepalive_status=? WHERE id=?",
                   (now, "success" if result.success else "failed", aid))
        db.commit()
        boot_tag = " (已自动开机🖥)" if result.booted else ""
        status_tag = f"[{result.vm_status_before}]" if result.vm_status_before else ""
        if result.success:
            msg = f"{result.vm_name}{status_tag}: 保活成功{boot_tag}"
        else:
            msg = f"{result.vm_name}{status_tag}: 保活失败{boot_tag} {result.error}"
        return jsonify({"success": result.success, "msg": msg, "cag_code": result.cag_code, "booted": result.booted})
    except Exception as e:
        return jsonify({"success": False, "msg": f"保活出错: {e}"}), 500


@main_bp.route("/accounts/<int:aid>/keepalive-now", methods=["POST"])
@login_required
def keepalive_now(aid):

    db = get_db()
    account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
    if not account:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "msg": "账号不存在"}), 404
        return redirect(url_for("main.index"))

    # 跳过关闭保活的 VM
    disabled = {r["user_service_id"] for r in
                db.execute("SELECT user_service_id FROM cloud_vm WHERE account_id=? AND keepalive_enabled=0", (aid,)).fetchall()}
    results, fresh_vms = keepalive_account(account["username"], account["password"],
                                           hold=current_app.config.get("HOLD_SECONDS", 10),
                                           skip_usids=disabled)
    now = _now_cst()
    status = "success" if all(r.success for r in results) else "failed"
    # 刷新 VM 状态
    if fresh_vms:
        for vm in fresh_vms:
            usid = int(vm.get("userServiceId", 0))
            db.execute(
                "UPDATE cloud_vm SET vm_status=?, remain_duration_time=?, raw_json=? "
                "WHERE account_id=? AND user_service_id=?",
                (vm.get("vmStatusShow", ""),
                 str(vm.get("remainDurationTime", "")) if vm.get("remainDurationTime") is not None else None,
                 json.dumps(vm, ensure_ascii=False),
                 aid, usid),
            )
    vm_map = {int(vm.get("userServiceId", 0)): vm for vm in fresh_vms} if fresh_vms else {}
    for r in results:
        vm_info = vm_map.get(r.user_service_id, {})
        remain = vm_info.get("remainDurationTime")
        db.execute(
            "INSERT INTO keepalive_log (account_id, vm_name, user_service_id, status, cag_reply_code, "
            "vm_status, remain_duration_time, error_message, vm_status_before, booted, executed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (aid, r.vm_name, r.user_service_id, "success" if r.success else "failed", r.cag_code,
             vm_info.get("vmStatusShow", ""),
             str(remain) if remain is not None else None,
             r.error or None, r.vm_status_before, int(r.booted), now),
        )
    db.execute("UPDATE cloud_account SET last_keepalive_at=?, last_keepalive_status=? WHERE id=?", (now, status, aid))
    db.commit()

    def _fmt(r):
        boot = "🖥" if r.booted else ""
        status = f"[{r.vm_status_before}]" if r.vm_status_before else ""
        ok = "✅" if r.success else "❌"
        return f"{r.vm_name}{status}: {ok}{boot}"
    msg = " | ".join(_fmt(r) for r in results)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": status == "success", "msg": msg})
    flash(f"保活完成: {msg}", "success" if status == "success" else "warning")
    return redirect(url_for("main.account_detail", aid=aid))


@main_bp.route("/accounts/<int:aid>/remark", methods=["POST"])
@login_required
def set_remark(aid):

    remark = request.form.get("remark", "").strip()
    db = get_db()
    db.execute("UPDATE cloud_account SET remark=? WHERE id=?", (remark, aid))
    db.commit()
    return jsonify({"success": True, "remark": remark})


@main_bp.route("/batch", methods=["POST"])
@login_required
def batch_action():
    """批量操作: action=keepalive|boot|delete|remark|expire, ids=[1,2,3]"""

    data = request.get_json(silent=True) or {}
    action = data.get("action", "")
    try:
        ids = [int(i) for i in data.get("ids", [])]
    except (TypeError, ValueError):
        return jsonify({"success": False, "msg": "ids 参数格式错误"}), 400
    if not ids or not action:
        return jsonify({"success": False, "msg": "参数缺失"}), 400

    db = get_db()
    results = []

    if action == "delete":
        for aid in ids:
            remove_job(aid)
            db.execute("DELETE FROM cloud_vm WHERE account_id=?", (aid,))
            db.execute("DELETE FROM keepalive_log WHERE account_id=?", (aid,))
            db.execute("DELETE FROM cloud_account WHERE id=?", (aid,))
        db.commit()
        return jsonify({"success": True, "msg": f"已删除 {len(ids)} 个账号"})

    if action == "remark":
        remark = data.get("remark", "")
        for aid in ids:
            db.execute("UPDATE cloud_account SET remark=? WHERE id=?", (remark, aid))
        db.commit()
        return jsonify({"success": True, "msg": f"已更新 {len(ids)} 个备注"})

    if action == "expire":
        expire_type = data.get("expire_type", "never")
        custom_date = data.get("custom_date", "")
        if expire_type == "never":
            expire_at = None
        elif expire_type == "custom" and custom_date:
            expire_at = custom_date + "T23:59:59"
        else:
            from datetime import timedelta as _td
            days_map = {"1d": 1, "1w": 7, "1m": 30, "1y": 365}
            days = days_map.get(expire_type, 0)
            expire_at = (datetime.now(_CST) + _td(days=days)).strftime("%Y-%m-%dT%H:%M:%S") if days else None
        for aid in ids:
            db.execute("UPDATE cloud_account SET expire_at=? WHERE id=?", (expire_at, aid))
        db.commit()
        label = expire_at[:10] if expire_at else "永不过期"
        return jsonify({"success": True, "msg": f"{len(ids)} 个账号到期设为 {label}"})

    if action == "keepalive":
        for aid in ids:
            account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
            if not account:
                continue
            disabled = {r["user_service_id"] for r in
                        db.execute("SELECT user_service_id FROM cloud_vm WHERE account_id=? AND keepalive_enabled=0", (aid,)).fetchall()}
            try:
                res, fresh = keepalive_account(account["username"], account["password"],
                                               hold=current_app.config.get("HOLD_SECONDS", 10), skip_usids=disabled)
                now = _now_cst()
                status = "success" if all(r.success for r in res) else "failed"
                db.execute("UPDATE cloud_account SET last_keepalive_at=?, last_keepalive_status=? WHERE id=?", (now, status, aid))
                booted_count = sum(1 for r in res if r.booted)
                boot_tag = f" 🖥×{booted_count}" if booted_count else ""
                results.append(f"{account['username']}: {'✅' if status == 'success' else '❌'}{boot_tag}")
            except Exception as e:
                results.append(f"{account['username']}: ❌ {e}")
        db.commit()
        return jsonify({"success": True, "msg": " | ".join(results) or "完成"})

    if action == "boot":
        for aid in ids:
            account = db.execute("SELECT * FROM cloud_account WHERE id=?", (aid,)).fetchone()
            if not account:
                continue
            try:
                client = soho_login(account["username"], account["password"])
                vms = fetch_vm_list(client)
                booted = 0
                for vm in vms:
                    if vm.get("vmStatus") in (23, "23"):
                        ok, msg = boot_vm(client, vm)
                        if ok:
                            booted += 1
                            db.execute("UPDATE cloud_vm SET vm_status='运行中' WHERE account_id=? AND user_service_id=?",
                                       (aid, int(vm["userServiceId"])))
                results.append(f"{account['username']}: {booted} 台已开机")
            except Exception as e:
                results.append(f"{account['username']}: ❌ {e}")
        db.commit()
        return jsonify({"success": True, "msg": " | ".join(results) or "完成"})

    return jsonify({"success": False, "msg": f"未知操作: {action}"}), 400


@main_bp.route("/logs")
@login_required
def logs():
    db = get_db()
    rows = db.execute(
        "SELECT l.*, a.username FROM keepalive_log l "
        "JOIN cloud_account a ON l.account_id=a.id "
        "ORDER BY l.executed_at DESC LIMIT 100"
    ).fetchall()
    return render_template("logs.html", logs=rows)
