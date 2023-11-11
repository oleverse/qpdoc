from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.conf.config import settings


engine = create_engine(settings.sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class NotUniqueException(Exception):
    pass
