from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class InteractionType(str, Enum):
    MEETING = "Meeting"
    CALL = "Call"
    EMAIL = "Email"
    VISIT = "Visit"

class Sentiment(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    hospital: Optional[str] = None

class HCPCreate(HCPBase):
    pass

class HCP(HCPBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: InteractionType
    date: datetime
    topics: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    outcomes: Optional[str] = None
    follow_up: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(BaseModel):
    interaction_type: Optional[InteractionType] = None
    date: Optional[datetime] = None
    topics: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    outcomes: Optional[str] = None
    follow_up: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None

class Interaction(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    hcp: Optional[HCP] = None
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str
    hcp_id: Optional[int] = None

class AgentResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[dict] = None