"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Autonomous Multi-Agent E-Commerce Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENV: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./ecommerce_intelligence.db"
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_intelligence"
    USE_SQLITE: bool = True
    
    # Security
    SECRET_KEY: str = "insecure-development-secret-key-replace-in-production-1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
    
    # Default Ranking Weights
    DEFAULT_WEIGHT_REQUIREMENT_FIT: float = 0.30
    DEFAULT_WEIGHT_REVIEW_QUALITY: float = 0.20
    DEFAULT_WEIGHT_PRICE_VALUE: float = 0.15
    DEFAULT_WEIGHT_SPEC_STRENGTH: float = 0.15
    DEFAULT_WEIGHT_RELIABILITY: float = 0.10
    DEFAULT_WEIGHT_PREFERENCE_MATCH: float = 0.10
    
    # LLM Settings
    LLM_PROVIDER: str = "groq"  # "mock", "gemini", "openai", "groq"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""


settings = Settings()
