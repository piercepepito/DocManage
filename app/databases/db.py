from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment")

engine = create_engine(DATABASE_URL)
LocalSession = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

def get_db():
    with LocalSession() as session:
        yield session
