"""
Database connection test script for Smart Healthcare Assistant.
Usage: python test_db.py
"""
import sys
from sqlalchemy import text
from app.database.connection import engine

def test_connection():
    print(f"Testing database connection to: {engine.url.render_as_string(hide_password=True)}")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("SUCCESS: Database connection established successfully!")
                return True
            else:
                print("FAILED: Query returned unexpected result.")
                return False
    except Exception as e:
        print(f"ERROR connecting to database: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
