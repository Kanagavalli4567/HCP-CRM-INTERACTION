# backend/test_groq.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key[:20]}...")

# Available Groq models
models = [
    "llama-3.3-70b-versatile",  # ✅ Latest Llama
    "llama-3.1-70b-versatile",  # ✅ Llama 3.1
    "mixtral-8x7b-32768",      # ✅ Mixtral
    "gemma2-9b-it"             # ❌ Decommissioned
]

try:
    client = Groq(api_key=api_key)
    
    # Test with Llama 3.3 (recommended)
    print("\n🔄 Testing with llama-3.3-70b-versatile...")
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # ✅ Working model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is HCP in healthcare?"}
        ],
        temperature=0.7,
    )
    
    print("✅ Groq API is working!")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Groq API error: {e}")