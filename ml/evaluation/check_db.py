import sqlite3
import os

for path in ['smart_healthcare.db', 'backend/smart_healthcare.db']:
    abs_p = os.path.abspath(path)
    if os.path.exists(abs_p):
        print(f"=== DB File: {abs_p} ===")
        conn = sqlite3.connect(abs_p)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        print("  Tables:", tables)
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"    Table '{t}': {cnt} rows")
            if 'user' in t:
                cur.execute(f"SELECT id, email, full_name, role FROM {t}")
                print(f"    User List in '{t}':", cur.fetchall())
        conn.close()
