# backend/test_agent.py
from app.database import SessionLocal
from app.agents.hcp_agent import HCPAgent

def test_agent():
    db = SessionLocal()
    agent = HCPAgent(db)
    
    test_messages = [
        "Hello!",
        "What is an HCP?",
        "How are you doing today?",
        "Can you help me log a meeting with Dr. Smith?",
        "What can you help me with?"
    ]
    
    print("="*60)
    print("🧪 Testing HCP CRM AI Agent")
    print("="*60)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = agent.process_message(msg)
        print(f"🤖 Assistant: {response['response']}")
        print(f"📊 Intent: {response.get('intent', 'unknown')}")
        print("-"*50)

if __name__ == "__main__":
    test_agent()