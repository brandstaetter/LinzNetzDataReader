from core.config import settings
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
insp = inspect(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
