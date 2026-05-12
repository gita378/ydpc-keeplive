import os
import sqlite3
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from flask import Flask


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(ROOT_DIR, "webapp")
if WEBAPP_DIR not in sys.path:
    sys.path.insert(0, WEBAPP_DIR)

from database import init_db  # noqa: E402
from routes import main_bp  # noqa: E402


class KeepaliveNowRouteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "cloudpc.db")

        app = Flask(__name__, template_folder=os.path.join(WEBAPP_DIR, "templates"))
        app.config.update(
            SECRET_KEY="test",
            DATABASE=self.db_path,
            DEFAULT_ADMIN_USER="admin",
            DEFAULT_ADMIN_PASS="admin123",
            LOGIN_MAX_ATTEMPTS=5,
            HOLD_SECONDS=10,
            MANUAL_KEEPALIVE_WORKERS=2,
        )
        init_db(app)
        app.register_blueprint(main_bp)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO cloud_account (id, username, password, keepalive_enabled) VALUES (1, 'user', 'pass', 1)"
        )
        conn.commit()
        conn.close()

        self.app = app
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["admin_logged_in"] = True

    def tearDown(self):
        self.tmp.cleanup()

    def test_keepalive_now_uses_background_low_concurrency_job(self):
        called = []
        done = threading.Event()

        def fake_run_keepalive(account_id, username, password, db_path, hold=10, max_workers=8):
            called.append(
                {
                    "account_id": account_id,
                    "username": username,
                    "password": password,
                    "db_path": db_path,
                    "hold": hold,
                    "max_workers": max_workers,
                }
            )
            done.set()

        with patch("scheduler._run_keepalive", side_effect=fake_run_keepalive):
            resp = self.client.post(
                "/accounts/1/keepalive-now",
                headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["success"], True)
        self.assertTrue(done.wait(1.0))
        self.assertEqual(called[0]["account_id"], 1)
        self.assertEqual(called[0]["username"], "user")
        self.assertEqual(called[0]["db_path"], self.db_path)
        self.assertEqual(called[0]["max_workers"], 2)


if __name__ == "__main__":
    unittest.main()
