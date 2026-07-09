# backend/test_db.py
from sqlalchemy import create_engine, text

# Hardcode the URL for testing
DATABASE_URL = "mysql+pymysql://hcp_user:Admin123@localhost:3306/hcp_crm"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        # Use text() wrapper for raw SQL
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        print(f"📊 Test query result: {result.fetchone()}")
except Exception as e:
    print(f"❌ Error: {e}")