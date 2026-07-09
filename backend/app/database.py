# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get URL from environment with fallback
DATABASE_URL = os.getenv("DATABASE_URL")

# If still None, use hardcoded value
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://hcp_user:Admin123@localhost:3306/hcp_crm"
    print("⚠️ Using hardcoded database URL (no .env found)")

# Remove any whitespace or quotes
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")

print(f"📊 Using database URL")  # Don't print the actual URL

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    print("✅ Database engine created successfully!")
except Exception as e:
    print(f"❌ Failed to create engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()