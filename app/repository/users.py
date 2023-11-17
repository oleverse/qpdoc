from datetime import datetime
from typing import Type, List
import uuid

from fastapi import HTTPException, status
from libgravatar import Gravatar
from slugify import slugify
from sqlalchemy.orm import Session

from app.database.models import User, BlacklistToken, RoleNames, Role
from app.database.models import User, RoleNames, Role
from app.schemas.essential import UserModel, UserProfileModel, UserUpdate


async def get_users_count(db: Session):
    return len(db.query(User).limit(1).all())


async def get_user_by_email(email: str, db: Session) -> Type[User]:
    return db.query(User).filter(User.email == email).first()


async def user_exists(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    return bool(user)


async def create_user(body: UserModel, db: Session):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    # first registered user is always admin
    default_role = RoleNames.user.name if await get_users_count(db) else RoleNames.admin.name
    role = db.query(Role).filter(Role.name == default_role).first()
    new_user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        avatar=avatar,
        role_id=role.id
    )
    # new_user = User(**body.model_dump(), avatar=avatar)
    new_user.slug = str(uuid.uuid4().hex)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    new_user.slug = slugify(f"{body.username}-{new_user.id}")
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, db: Session):
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    user.is_active = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> Type[User] | None:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def ban_user(email: str, current_user_id: int, db: Session, is_active=False) -> type[User]:
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
    if user.id == current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change your own status!")

    user.is_active = is_active
    user.updated_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user


async def add_to_blacklist(token: str, db: Session) -> None:
    blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.now())
    db.add(blacklist_token)
    db.commit()


async def find_blacklisted_token(token: str, db: Session) -> None:
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    return blacklist_token


async def remove_from_blacklist(token: str, db: Session) -> None:
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    db.delete(blacklist_token)


async def get_user_profile(slug: str, db: Session) -> User | None:
    user = db.query(User).filter(User.slug == slug).first()  # slug or username  ??
    user_profile = None
    if user:
        user_profile = UserProfileModel(id=user.id, username=user.username, email=user.email,
                                        created_at=user.created_at, is_active=user.is_active)
    return user_profile


async def get_all_users(limit: int, offset: int, user: User, db: Session) -> List[Type[User]]:
    if not user.role != RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This action only for admin person. You don't have a permission!")

    all_users = db.query(User).order_by(User.id).all()

    if all_users:
        return all_users


async def update_user_self(body: UserModel, user: User, db: Session) -> User | None:

    user = db.query(User).filter(User.id == user.id).first()
    if user:
        user.username = body.username
        user.email = body.email
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
    return user


async def update_user_as_admin(body: UserUpdate, user: User, db: Session) -> Type[User] | None:
    pass
#
#     user_to_update = db.query(User).filter(User.username == body.username).first()
#     if user_to_update:
#         if user.role == RoleNames.admin:
#             user_to_update.username = body.username
#             user_to_update.email = body.email
#             user_to_update.is_active = body.is_active
#             user_to_update.user_role = body.role
#             user_to_update.updated_at = datetime.now()
#             db.commit()
#         return user_to_update
#     return None

