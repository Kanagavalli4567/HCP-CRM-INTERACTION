from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class HCP(Base):
    __tablename__ = "hcps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    hospital = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    interactions = relationship("Interaction", back_populates="hcp")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    interaction_type = Column(Enum("Meeting", "Call", "Email", "Visit", name="interaction_types"))
    date = Column(DateTime, nullable=False)
    topics = Column(Text)
    summary = Column(Text)
    sentiment = Column(Enum("Positive", "Neutral", "Negative", name="sentiment_types"))
    outcomes = Column(Text)
    follow_up = Column(Text)
    materials_shared = Column(Text)
    samples_distributed = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    hcp = relationship("HCP", back_populates="interactions")