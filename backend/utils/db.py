# utils/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------
# ✅ DATABASE URL (MySQL)
# -----------------------------------------
DATABASE_URL = "mysql+pymysql://attendance_user:attendance123@localhost:3306/smart_attendance"

# -----------------------------------------
# ✅ ENGINE + SESSION
# -----------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------------------
# ✅ Base Model
# -----------------------------------------
Base = declarative_base()

# -----------------------------------------
# ⬇️ VERY IMPORTANT: IMPORT MODELS HERE
# -----------------------------------------
from models.user_model import User
from models.attendance_model import Attendance
from models.active_session import ActiveSession

# -----------------------------------------
# ⬇️ CREATE ALL TABLES (YOU WERE MISSING THIS)
# -----------------------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------------------
# ✅ GLOBAL get_db() (used by ALL routes)
# -----------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
