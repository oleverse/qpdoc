from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.models import User, History
from app.schemas.essential import HistoryResponse
from app.database.db import get_db, SessionLocal
import app.repository.histories as repository_history

from app.services.auth import auth_service

router = APIRouter(prefix='/history', tags=['history'])


@router.get("/{user_id}", response_model=List[HistoryResponse])
async def get_history_for_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    print(db_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    history = await repository_history.get_history_for_user(user_id, db)
    if history is None:
        raise HTTPException(status_code=404, detail="History not found")
    return history

