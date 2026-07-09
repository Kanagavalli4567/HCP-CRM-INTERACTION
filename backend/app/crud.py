from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

def get_hcp(db: Session, hcp_id: int):
    return db.query(models.HCP).filter(models.HCP.id == hcp_id).first()

def get_hcps(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HCP).offset(skip).limit(limit).all()

def create_hcp(db: Session, hcp: schemas.HCPCreate):
    db_hcp = models.HCP(**hcp.dict())
    db.add(db_hcp)
    db.commit()
    db.refresh(db_hcp)
    return db_hcp

def get_interaction(db: Session, interaction_id: int):
    return db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()

def get_hcp_interactions(db: Session, hcp_id: int, limit: int = 10):
    return db.query(models.Interaction).filter(
        models.Interaction.hcp_id == hcp_id
    ).order_by(models.Interaction.date.desc()).limit(limit).all()

def create_interaction(db: Session, interaction: schemas.InteractionCreate):
    db_interaction = models.Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

def update_interaction(db: Session, interaction_id: int, interaction_update: schemas.InteractionUpdate):
    db_interaction = get_interaction(db, interaction_id)
    if db_interaction:
        update_data = interaction_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_interaction, key, value)
        db.commit()
        db.refresh(db_interaction)
    return db_interaction

def delete_interaction(db: Session, interaction_id: int):
    db_interaction = get_interaction(db, interaction_id)
    if db_interaction:
        db.delete(db_interaction)
        db.commit()
        return True
    return False

def get_hcps(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HCP).offset(skip).limit(limit).all()