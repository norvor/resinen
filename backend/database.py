import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# 1. Force load the .env file
load_dotenv()

# 2. Get the URL from the file
DATABASE_URL = os.getenv("DATABASE_URL")

# Safety Check: If no URL found, print error
if not DATABASE_URL:
    raise ValueError("FATAL: DATABASE_URL not found in .env file.")

# 3. Create Engine
# pool_pre_ping=True fixes "server closed the connection unexpectedly" errors
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session