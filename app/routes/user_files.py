from app.database.models import User
from app.services.auth import auth_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
import app.repository.user_files as repo_user_files

router = APIRouter(prefix='/user-files', tags=["user_files"])


@router.get("/{file_id}")
async def get_file_content_by_id(file_id: int,
                                 current_user: User = Depends(auth_service.get_current_user),
                                 db: Session = Depends(get_db)):
    user_file = await repo_user_files.get_user_file_by_id(file_id=file_id, user_id=current_user.id, db=db)
    if user_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The file not found')

    return user_file.content[:3000] if len(user_file.content) > 3000 else user_file.content
