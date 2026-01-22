from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Resinen: Rest In Engines"
    
    # Database
    POSTGRES_USER: str = "resinen_admin"
    POSTGRES_PASSWORD: str = "securepassword"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_DB: str = "resinen_platform"
    
    # Auth
    SECRET_KEY: str = "change_this_to_a_very_long_random_string_xyz123"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 Days (Personal app, long session)
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"]

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()