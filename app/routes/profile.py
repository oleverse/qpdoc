from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import User, RoleNames
from app.repository import users as repository_users
from app.schemas.essential import UserUpdate, UserDb, UserProfileUpdate, UserDbExtra, UserStatusResponse
from app.schemas.essential import UserStatusChange, UserDbStatus
from app.services.auth import auth_service

router = APIRouter(prefix="/profile", tags=['profile'])
security = HTTPBearer()


async def get_user_by_slug(db: Session, slug: str) -> UserDbExtra | None:
    return db.query(User).filter(User.slug == slug).first()


async def update_user(db: Session, user_update: UserProfileUpdate, current_user: User) -> UserDbExtra:
    user = await get_user_by_slug(db, current_user.slug)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    user.password = auth_service.get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)

    return user
    # return {""}


@router.get("/who_am_i", response_model=UserDbExtra)
async def view_own_profile(db: Session = Depends(get_db),
                           user: User = Depends(auth_service.get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You should be authorized.")

    user_data = user.__dict__

    return user_data


@router.get("/{slug}", response_model=UserDbExtra)
async def view_user_profile(slug: str, db: Session = Depends(get_db)):
    user = await get_user_by_slug(db, slug)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_data = user.__dict__

    return user_data


@router.get('/admin/all_users', response_model=list[UserDbStatus])
async def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    if not current_user.role.name == RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Only administrators can get full list of users.")

    all_users = await repository_users.get_all_users(skip, limit, current_user, db)
    if all_users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users not found.")
    UserDb.model_validate(all_users[0])
    return all_users


@router.get("/admin/{slug}", response_model=UserDbExtra)
async def admin_view_user_profile(slug: str, db: Session = Depends(get_db),
                                  current_user: User = Depends(auth_service.get_current_user)):
    if not current_user.role.name == RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Only administrators can see sensitive information.")
    user = await get_user_by_slug(db, slug)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_data = user.__dict__

    return user_data


@router.put("/update", response_model=UserDb)
async def edit_own_profile(user_update: UserProfileUpdate, db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    user = await update_user(db, user_update, current_user)
    return user


@router.put("/deactivate", response_model=UserStatusResponse)
async def user_deactivate(user_data: UserStatusChange, current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    if current_user.role.name != RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can deactivate users!")

    user = await repository_users.ban_user(user_data.email, current_user.id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    return user


@router.put("/activate", response_model=UserStatusResponse)
async def user_activate(user_data: UserStatusChange, current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    if current_user.role.name != RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can activate users!")
    user = await repository_users.ban_user(user_data.email, current_user.id, db, is_active=True)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    return user
