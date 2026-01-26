import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get DB URL from .env, default to sqlite if not found (fallback)
database_url = os.getenv("DATABASE_URL")

# Postgres connection engine
engine = create_engine(database_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session