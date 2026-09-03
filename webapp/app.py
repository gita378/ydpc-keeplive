#!/usr/bin/env python3
"""移动云电脑保活管理 Web 应用"""
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from database import init_db
from scheduler import init_scheduler

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    csrf.init_app(app)
    init_db(app)

    from auth import auth_bp
    from routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    from database import get_setting, HOLD_EXTEND_KEY

    @app.context_processor
    def inject_hold_extend():
        db_path = app.config.get("DATABASE", "")
        enabled = db_path and get_setting(db_path, HOLD_EXTEND_KEY, "0") == "1"
        return {"hold_extend_enabled": enabled}

    init_scheduler(app)

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    app = create_app()
    print("\n  移动云电脑保活管理")
    print("  http://127.0.0.1:5110")
    print("  默认登录: admin / admin123\n")
    app.run(host="0.0.0.0", port=5110, debug=False)
