from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.models import PDFModel


async def get_user_files(user_id: int, db: Session):
    return db.query(PDFModel).filter(and_(PDFModel.user_id == user_id)).all()


async def get_user_file_by_id(file_id: int, user_id: int, db: Session):
    return db.query(PDFModel).filter(and_(PDFModel.user_id == user_id, PDFModel.id == file_id)).first()
