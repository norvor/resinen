from sqlmodel import SQLModel, create_engine, Session

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
# Replace with your actual Postgres connection string.
# Format: postgresql://<user>:<password>@<host>:<port>/<db_name>
# Example for local default:
DATABASE_URL = "postgresql://localhost/resinen_platform"

# Create the engine
engine = create_engine(DATABASE_URL)

def init_db():
    """
    Creates the tables in the database if they don't exist.
    Run this once on startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency to provide a database session to API endpoints.
    """
    with Session(engine) as session:
        yield session