#!/usr/bin/env python3
"""重置管理员密码: python3 reset_password.py [新密码]"""
import sqlite3, sys, os
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudpc.db")
new_pass = sys.argv[1] if len(sys.argv) > 1 else "admin123"

conn = sqlite3.connect(db_path)
conn.execute("UPDATE admin_user SET password_hash=?", (generate_password_hash(new_pass),))
conn.commit()
row = conn.execute("SELECT username FROM admin_user LIMIT 1").fetchone()
conn.close()
print(f"已重置: 用户={row[0]} 密码={new_pass}")
