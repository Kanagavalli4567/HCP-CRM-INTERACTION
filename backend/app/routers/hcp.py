from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/hcp", tags=["hcp"])

@router.post("/", response_model=schemas.HCP)
def create_hcp(hcp: schemas.HCPCreate, db: Session = Depends(get_db)):
    return crud.create_hcp(db=db, hcp=hcp)

@router.get("/", response_model=List[schemas.HCP])
def get_hcps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_hcps(db, skip=skip, limit=limit)

@router.get("/{hcp_id}", response_model=schemas.HCP)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    db_hcp = crud.get_hcp(db, hcp_id)
    if db_hcp is None:
        raise HTTPException(status_code=404, detail="HCP not found")
    return db_hcp