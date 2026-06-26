from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()