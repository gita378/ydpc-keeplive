import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cloudpc-keepalive-secret-change-me")
    DATABASE = os.path.join(BASE_DIR, "cloudpc.db")
    HOLD_SECONDS = 10
    TIMEOUT = 10
    # 默认管理员（首次启动自动创建）
    DEFAULT_ADMIN_USER = "admin"
    DEFAULT_ADMIN_PASS = "admin123"
