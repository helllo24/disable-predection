import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

print("=== AVION MYSQL DATABASE VERIFICATION ===")

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "3306")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "smart_healthcare_db")
db_url = os.getenv("DATABASE_URL")

print(f"DB_HOST: {db_host}")
print(f"DB_PORT: {db_port}")
print(f"DB_USER: {db_user}")
print(f"DB_NAME: {db_name}")
print(f"Password provided: {'YES (Masked)' if db_pass else 'NO'}")

# Import SQLAlchemy engine from connection.py
from app.database.connection import engine, Base
from sqlalchemy import inspect, text

driver = engine.url.drivername
print(f"Active SQLAlchemy Dialect/Driver: {driver}")

if "sqlite" in driver:
    print("[ERROR] Application is still using SQLite!")
    sys.exit(1)
else:
    print(f"[CONFIRMED] Application is NOT using SQLite. Connected to MySQL database via {driver}.")

print("\n--- Running Existing init_db.py ---")
import init_db
init_db.init()

print("\n--- Inspecting Created Tables in smart_healthcare_db ---")
inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"Connected Database Name: {engine.url.database}")
print(f"Number of Tables Found: {len(tables)}")
print("Table Names:")
for t in sorted(tables):
    print(f"  - {t}")

expected_tables = [
    "users", "bmi_records", "diabetes_predictions", "disease_predictions",
    "health_risk_scores", "diet_recommendations", "exercise_recommendations",
    "medicine_reminders", "doctors", "appointments"
]

missing = [t for t in expected_tables if t not in tables]
if missing:
    print(f"\n[WARNING] Missing tables: {missing}")
else:
    print("\n[SUCCESS] All 10 required tables exist in smart_healthcare_db!")
