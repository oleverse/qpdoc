from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, constr


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    password: str = Field(min_length=0, max_length=14)


class UserUpdate(UserModel):
    is_active: bool
    role: str


class UserDb(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    username: str
    email: Optional[EmailStr] = None
    created_at: datetime
    avatar: Optional[str] = None


class UserDbStatus(UserDb):
    is_active: bool


class UserDbExtra(UserDb):
    photos_count: Optional[int] = None
    comments_count: Optional[int] = None


class UserProfileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None
    number_pictures: Optional[int]
    number_comments: Optional[int]


class UserResponse(BaseModel):
    user: UserDb
    detail: str = 'User successfully created'


class UserProfileUpdate(BaseModel):
    password: constr(min_length=5, max_length=100) = None
    username: str
    email: EmailStr


class UserStatusChange(BaseModel):
    email: EmailStr


class UserStatusResponse(BaseModel):
    username: str
    email: EmailStr
    is_active: bool
    updated_at: datetime


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr


class PDFFile(BaseModel):
    filename: str
    content: str
    user_id: Optional[int]
    context: Optional[str]


class ChatRequest(BaseModel):
    query: str
    user_id: str
    file_id: int

# class HistoryBase(BaseModel):
#     user_id: int
#     question: str
#     answer: str


class HistoryResponse(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str
    created_at: datetime | None
    updated_at: datetime | None

    # class ConfigDict:
    #     from_attributes = True

