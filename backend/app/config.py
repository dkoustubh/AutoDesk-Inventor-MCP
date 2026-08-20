import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ATS Engineering AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8005
    
    # AI / LLM (vLLM)
    VLLM_API_BASE: str = os.getenv("VLLM_API_BASE", "http://192.168.11.86:8000/v1")
    VLLM_MODEL: str = os.getenv("VLLM_MODEL", "google/gemma-4-31B-it")
    
    # Database (PostgreSQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@192.168.11.86:5432/ats_engineering"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://192.168.11.86:6380/0")
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:8085",
        "http://192.168.11.86:8085",
        "http://192.168.11.94:5173",
        "*"
    ]
    
    # Workstation Defaults
    DEFAULT_WORKSTATION_IP: str = "192.168.11.150"
    DEFAULT_USER_NAME: str = "Koustubh Deodhar"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
