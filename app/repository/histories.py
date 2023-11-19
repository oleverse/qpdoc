from datetime import datetime
from typing import Type, List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import and_


from app.database.models import User, History
from app.schemas.essential import HistoryResponse


async def create_record(user_id: int, file_id: int, query, answer, db: Session):
    record = History(user_id=user_id, file_id=file_id, question=query, answer=answer)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


async def get_last_history_file_id(user_id: int, db: Session):
    last_file_used = db.query(History).filter(and_(History.user_id == user_id))\
        .order_by(History.id.desc()).limit(1).first()
    return last_file_used.file_id


async def get_history_for_user(user_id: int, db: Session):
    return db.query(History).filter(and_(History.user_id == user_id)).all()


async def get_history_for_user_by_file(user_id: int, file_id, db: Session):
    return db.query(History).filter(and_(History.user_id == user_id, History.file_id == file_id)).all()


async def remove_history(id: int, db: Session):
    # history = await db.execute(
    #     select(History).join(User, User.id == History)
    # )
    #
    history = db.query(History).filter(and_(History.user_id == id)).all()
    if history:
        for i in history:
            db.delete(i)
            db.commit()

    if history is None:
        raise HTTPException(status_code=404, detail="History not found")


