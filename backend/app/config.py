"""
FermaGen AI - Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    app_name: str = "FermaGen AI"
    version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database (default to PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:password@127.0.0.1:5432/fermagen"
    
    # External APIs
    perplexity_api_key: str = ""
    uniprot_base_url: str = "https://rest.uniprot.org"
    kegg_base_url: str = "https://rest.kegg.jp"
    pubchem_base_url: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
