import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Support individual Avion MySQL environment variables or direct DATABASE_URL
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "smart_healthcare_db")

DATABASE_URL = None

if db_user and db_password and db_host:
    mysql_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    try:
        # Test Cloud MySQL connection with a short timeout to prevent server hang
        test_engine = create_engine(
            mysql_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        DATABASE_URL = mysql_url
        print("[DB Info] Connected successfully to Cloud MySQL Database.")
    except Exception as err:
        print(f"[DB Warning] Could not connect to Cloud MySQL database ({err}). Falling back to local SQLite database.")
        DATABASE_URL = "sqlite:///./smart_healthcare.db"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./smart_healthcare.db"
    )

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
