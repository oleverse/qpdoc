from datetime import datetime
from typing import Type, List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session


from app.database.models import User, History
from app.schemas.essential import HistoryResponse


async def create_record(user_id: int, query, answer, db: Session):
    record = History(user_id=user_id, question=query, answer=answer)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
