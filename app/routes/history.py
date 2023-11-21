from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database.models import User, History
from app.schemas.essential import HistoryResponse
from app.database.db import get_db, SessionLocal
import app.repository.histories as repository_history

from app.services.auth import auth_service

router = APIRouter(prefix='/history', tags=['history'])


@router.get("/for-file/{file_id}", response_model=List[HistoryResponse])
async def get_history_by_file(file_id: int, user: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):
    history = await repository_history.get_history_for_user_by_file(user.id, file_id, db)

    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No history for this file")

    return history


@router.delete("/qa-pair/{history_pair_id}")
async def remove_history_pair(history_pair_id: int, user: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):
    return await repository_history.remove_qa_pair(history_pair_id, user.id, db)


@router.get("/{user_id}", response_model=List[HistoryResponse])
async def get_history_for_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    history = await repository_history.get_history_for_user(user_id, db)
    if history is None:
        raise HTTPException(status_code=404, detail="History not found")
    return history


@router.delete("/{user_id}")
async def remove_history(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # history = await repository_history.remove_history(user_id, db)
    # if history is None:
    #     raise HTTPException(status_code=404, detail="History not found")
    return await repository_history.remove_history(user_id, db)
