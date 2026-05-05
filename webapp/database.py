import sqlite3
from flask import g, current_app

SCHEMA = """
CREATE TABLE IF NOT EXISTS admin_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cloud_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    keepalive_enabled INTEGER DEFAULT 0,
    keepalive_interval INTEGER DEFAULT 600,
    last_login_at TIMESTAMP,
    last_keepalive_at TIMESTAMP,
    last_keepalive_status TEXT,
    expire_at TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cloud_vm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES cloud_account(id) ON DELETE CASCADE,
    user_service_id INTEGER NOT NULL,
    vm_name TEXT,
    spu_code TEXT,
    sku_name TEXT,
    vm_status TEXT,
    remain_duration_time TEXT,
    cpu TEXT,
    memory TEXT,
    raw_json TEXT,
    keepalive_enabled INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keepalive_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES cloud_account(id) ON DELETE CASCADE,
    vm_name TEXT,
    user_service_id INTEGER,
    status TEXT NOT NULL,
    cag_reply_code INTEGER,
    vm_status TEXT,
    remain_duration_time TEXT,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT (datetime('now','localtime'))
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
        g.db.execute("PRAGMA busy_timeout=5000")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _migrate(db):
    """自动添加缺失的列，不用删库"""
    migrations = [
        ("keepalive_log", "vm_status", "TEXT"),
        ("keepalive_log", "remain_duration_time", "TEXT"),
        ("cloud_account", "expire_at", "TEXT"),
        ("cloud_vm", "keepalive_enabled", "INTEGER DEFAULT 1"),
    ]
    for table, col, col_type in migrations:
        existing = [r[1] for r in db.execute(f"PRAGMA table_info({table})").fetchall()]
        if col not in existing:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")


def init_db(app):
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        db.executescript(SCHEMA)
        _migrate(db)
        # 创建默认管理员
        from werkzeug.security import generate_password_hash

        cur = db.execute("SELECT COUNT(*) FROM admin_user")
        if cur.fetchone()[0] == 0:
            db.execute(
                "INSERT INTO admin_user (username, password_hash) VALUES (?, ?)",
                (
                    app.config["DEFAULT_ADMIN_USER"],
                    generate_password_hash(app.config["DEFAULT_ADMIN_PASS"]),
                ),
            )
            db.commit()
        db.close()
    app.teardown_appcontext(close_db)
