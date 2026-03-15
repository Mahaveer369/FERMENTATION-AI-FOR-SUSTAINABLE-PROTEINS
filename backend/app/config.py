"""
FermaGen AI - Application Configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    app_name: str = "FermaGen AI"
    version: str = "1.0.0"
    debug: bool = False
    
    # Security - These MUST be set in production
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database (default to PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/fermagen"
    
    # External APIs
    perplexity_api_key: str = ""
    nvidia_api_key: str = ""
    groq_api_key: str = ""
    firebase_api_key: str = ""
    firebase_project_id: str = ""
    uniprot_base_url: str = "https://rest.uniprot.org"
    kegg_base_url: str = "https://rest.kegg.jp"
    pubchem_base_url: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Redis (optional - for caching)
    redis_url: str = "redis://redis:6379/0"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate required production settings
        if not self.debug and not self.secret_key:
            raise ValueError("SECRET_KEY must be set in production (set DEBUG=False)")
    
    @property
    def is_production(self) -> bool:
        return not self.debug and self.secret_key != ""


def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
