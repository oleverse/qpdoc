import enum
from sqlalchemy import Column, Integer, String, func, ForeignKey, Boolean, Table, Numeric, Text
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship, declarative_base



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

    id = Column(Integer, primary_key=True)
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

class PDFModel(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(String)
