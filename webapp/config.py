import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 首次启动自动生成 SECRET_KEY 并持久化
_key_file = os.path.join(BASE_DIR, ".secret_key")
if os.environ.get("SECRET_KEY"):
    _secret = os.environ["SECRET_KEY"]
elif os.path.exists(_key_file):
    with open(_key_file) as f:
        _secret = f.read().strip()
else:
    _secret = os.urandom(32).hex()
    with open(_key_file, "w") as f:
        f.write(_secret)


class Config:
    SECRET_KEY = _secret
    DATABASE = os.path.join(BASE_DIR, "cloudpc.db")
    HOLD_SECONDS = 10
    TIMEOUT = 10
    DEFAULT_ADMIN_USER = "admin"
    DEFAULT_ADMIN_PASS = "admin123"
    LOGIN_MAX_ATTEMPTS = 5  # 超过此次数需要验证码
