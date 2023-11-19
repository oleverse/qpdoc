import enum


from sqlalchemy.orm import relationship, column_property, configure_mappers
from sqlalchemy.sql import select

from sqlalchemy import Column, Integer, String, func, ForeignKey, Boolean, Table, Numeric, Text, select, text
from sqlalchemy.future import engine
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship, declarative_base, column_property

Base = declarative_base()


class RoleNames(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'

    @staticmethod
    def get_max_role_len():
        return len(max(list(RoleNames.__members__), key=lambda item: len(item)))


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(RoleNames.get_max_role_len()), default=RoleNames.user)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    role_id = Column(Integer, ForeignKey(Role.id))
    confirmed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    slug = Column(String(255), unique=True, nullable=False)
    avatar = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    role = relationship("Role", backref="users")
    uploaded_files = relationship('PDFModel', back_populates='user')
    history = relationship('History', backref='user')


class PDFModel(Base):
    __tablename__ = 'pdfs'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates="uploaded_files")
    history = relationship('History', backref='files')


class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    blacklisted_on = Column(DateTime, default=func.now())


class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    file_id = Column(Integer, ForeignKey('pdfs.id', ondelete='CASCADE'), nullable=True)
    question = Column(String)
    answer = Column(String)
    created_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())