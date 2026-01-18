
from typing import List
from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resinen Platform"
    API_V1_STR: str = "/api/v1"
    
    # DB
    DATABASE_URL: str = "postgresql+asyncpg://resinen_admin:securepassword@localhost/resinen_platform"
    
    # SECURITY
    SECRET_KEY: str = "change_this_to_a_secure_random_key_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://resinen.com"]

    # --- 🆕 MINIO (THE VAULT) ---
    MINIO_ENDPOINT: str = "http://localhost:9000" # Where MinIO lives
    MINIO_ACCESS_KEY: str = "resinen_minio_admin"
    MINIO_SECRET_KEY: str = "minio_secure_password_123"
    MINIO_BUCKET_NAME: str = "resinen-media" # The folder we store files in

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()