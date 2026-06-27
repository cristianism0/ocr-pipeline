import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_ = load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ocrdb")

psql_engine = create_engine(DB_URL)

DBSession = sessionmaker(bind=psql_engine)


class Base(DeclarativeBase):
    pass


# need to be called when a job is created
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
