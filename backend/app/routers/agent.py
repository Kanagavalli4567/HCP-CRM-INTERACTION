# backend/app/routers/agent.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import ChatMessage, AgentResponse
from ..database import get_db
from ..agents.hcp_agent import HCPAgent

router = APIRouter(prefix="/api/agent", tags=["agent"])

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(message: ChatMessage, db: Session = Depends(get_db)):
    try:
        agent = HCPAgent(db)
        response = agent.process_message(message.message, message.hcp_id)
        
        return AgentResponse(
            response=response["response"],
            action=response.get("intent"),
            data=response.get("tool_result")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))