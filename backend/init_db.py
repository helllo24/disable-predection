import os
import sys
import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import engine, Base
import app.models  # noqa: F401
from app.models.user import User
from app.models.doctor import Doctor

db_file = os.path.join(os.path.dirname(__file__), "smart_healthcare.db")

def hash_pw(pwd: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')

def init():
    # Only remove local SQLite file if backend is explicitly configured for SQLite
    if engine.url.drivername.startswith("sqlite") and os.path.exists(db_file):
        try:
            os.remove(db_file)
            print("Removed old SQLite database file to apply schema updates.")
        except Exception as e:
            print(f"Could not remove old db file: {e}")

    print(f"Initializing database using engine: {engine.url.render_as_string(hide_password=True)}")
    Base.metadata.create_all(bind=engine)

    print("Successfully created/updated all database tables!")

    with Session(bind=engine) as session:
        # Seed Default Admin Account if missing
        admin_count = session.query(User).filter(User.role == "ADMIN").count()
        if admin_count == 0:
            admin_user = User(
                full_name="System Administrator",
                email="admin@example.com",
                phone="+1-555-0000",
                password_hash=hash_pw("AdminPass123"),
                age=40,
                gender="Other",
                role="ADMIN",
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            print("Successfully seeded Default Admin Account (admin@example.com / AdminPass123)!")

        # Seed Demo Doctor Data if missing
        count = session.query(Doctor).count()
        if count == 0:
            demo_doctors = [
                Doctor(
                    name="Dr. Sarah Jenkins (Demo)",
                    specialization="Cardiology",
                    qualification="MD, FACC",
                    clinic_hospital="City Heart Care Center",
                    phone="+1-555-0192",
                    email="dr.jenkins.demo@example.com",
                    available_days="Monday, Wednesday, Friday",
                    available_times="09:00 AM - 01:00 PM, 04:00 PM - 07:00 PM",
                    active=True
                ),
                Doctor(
                    name="Dr. Rajesh Kumar (Demo)",
                    specialization="Endocrinology",
                    qualification="MD, DM (Endocrinology)",
                    clinic_hospital="Diabetes & Metabolic Health Clinic",
                    phone="+1-555-0144",
                    email="dr.kumar.demo@example.com",
                    available_days="Tuesday, Thursday, Saturday",
                    available_times="10:00 AM - 02:00 PM",
                    active=True
                ),
                Doctor(
                    name="Dr. Emily Chen (Demo)",
                    specialization="General Medicine",
                    qualification="MBBS, MD (Internal Medicine)",
                    clinic_hospital="Community Wellness Hospital",
                    phone="+1-555-0188",
                    email="dr.chen.demo@example.com",
                    available_days="Monday, Tuesday, Wednesday, Thursday, Friday",
                    available_times="08:30 AM - 04:30 PM",
                    active=True
                ),
                Doctor(
                    name="Dr. Michael Ross (Demo)",
                    specialization="Neurology",
                    qualification="MD, Ph.D.",
                    clinic_hospital="Neuro & Brain Care Institute",
                    phone="+1-555-0123",
                    email="dr.ross.demo@example.com",
                    available_days="Monday, Thursday",
                    available_times="11:00 AM - 03:00 PM",
                    active=True
                ),
                Doctor(
                    name="Dr. Anita Sharma (Demo)",
                    specialization="Pediatrics",
                    qualification="MD (Pediatrics), DCH",
                    clinic_hospital="Sunshine Children Clinic",
                    phone="+1-555-0177",
                    email="dr.sharma.demo@example.com",
                    available_days="Wednesday, Friday, Saturday",
                    available_times="09:30 AM - 01:30 PM",
                    active=True
                )
            ]
            session.add_all(demo_doctors)
            session.commit()
            print("Successfully seeded 5 sample demo doctors!")

if __name__ == "__main__":
    init()
