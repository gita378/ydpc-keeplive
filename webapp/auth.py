from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash
from database import get_db
from captcha_util import generate_captcha, verify_captcha

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    fail_count = session.get("_login_fails", 0)
    need_captcha = fail_count >= current_app.config.get("LOGIN_MAX_ATTEMPTS", 5)

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # 验证码校验
        if need_captcha:
            captcha_input = request.form.get("captcha", "")
            if not verify_captcha(captcha_input):
                flash("验证码错误", "danger")
                captcha = generate_captcha()
                return render_template("login.html", need_captcha=True, captcha=captcha)

        db = get_db()
        user = db.execute("SELECT * FROM admin_user WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            session.pop("_login_fails", None)
            return redirect(url_for("main.index"))

        session["_login_fails"] = fail_count + 1
        remaining = current_app.config.get("LOGIN_MAX_ATTEMPTS", 5) - (fail_count + 1)
        if remaining > 0:
            flash(f"用户名或密码错误（还剩 {remaining} 次后需验证码）", "danger")
        else:
            flash("用户名或密码错误", "danger")
        need_captcha = (fail_count + 1) >= current_app.config.get("LOGIN_MAX_ATTEMPTS", 5)

    captcha = generate_captcha() if need_captcha else None
    return render_template("login.html", need_captcha=need_captcha, captcha=captcha)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_username = request.form.get("new_username", "").strip()
        old_pwd = request.form.get("old_password", "")
        new_pwd = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not old_pwd:
            flash("当前密码不能为空", "danger")
            return render_template("change_password.html", admin_username=session["admin_username"])

        db = get_db()
        user = db.execute("SELECT * FROM admin_user WHERE username=?", (session["admin_username"],)).fetchone()
        if not user or not check_password_hash(user["password_hash"], old_pwd):
            flash("当前密码错误", "danger")
            return render_template("change_password.html", admin_username=session["admin_username"])

        if new_pwd and new_pwd != confirm:
            flash("两次新密码不一致", "danger")
            return render_template("change_password.html", admin_username=session["admin_username"])

        from werkzeug.security import generate_password_hash
        # 修改用户名
        if new_username and new_username != session["admin_username"]:
            db.execute("UPDATE admin_user SET username=? WHERE id=?", (new_username, user["id"]))
            session["admin_username"] = new_username
        # 修改密码（有填才改）
        if new_pwd:
            db.execute("UPDATE admin_user SET password_hash=? WHERE id=?",
                       (generate_password_hash(new_pwd), user["id"]))
        db.commit()
        flash("管理员信息修改成功", "success")
        return redirect(url_for("main.index"))
    return render_template("change_password.html", admin_username=session.get("admin_username", "admin"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
