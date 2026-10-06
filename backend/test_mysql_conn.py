import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=== BACKEND DATABASE CONFIGURATION INSPECTION ===")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "3306")
db_user = os.getenv("DB_USER")
db_name = os.getenv("DB_NAME", "smart_healthcare_db")
db_url = os.getenv("DATABASE_URL")

print(f"DB_HOST: {db_host}")
print(f"DB_PORT: {db_port}")
print(f"DB_USER: {db_user}")
print(f"DB_NAME: {db_name}")
print(f"DATABASE_URL: {db_url}")

if db_host and db_user:
    print(f"Configured Engine Target: MySQL ({db_host}:{db_port}/{db_name})")
elif db_url and db_url.startswith("mysql"):
    print(f"Configured Engine Target: MySQL via DATABASE_URL")
else:
    print(f"Configured Engine Target: SQLite Fallback ({db_url})")
