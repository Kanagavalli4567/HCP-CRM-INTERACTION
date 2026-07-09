# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcp_crm.db")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # ✅ Use a supported model
    GROQ_MODEL = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"