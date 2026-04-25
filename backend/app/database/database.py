"""
FermaGen AI - Database Configuration and Models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
import enum

from app.config import get_settings

settings = get_settings()

# Async Engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Session Factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    STUDENT = "student"
    RESEARCHER = "researcher"
    SCIENTIST = "scientist"
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default=UserRole.RESEARCHER.value)
    organization = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiments = relationship("Experiment", back_populates="user")


class Experiment(Base):
    """Fermentation experiment model"""
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Fermentation Parameters
    microbe_type = Column(String(100), nullable=False)
    substrate = Column(String(100), nullable=False)
    temperature = Column(Float, nullable=False)  # Celsius
    ph = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)  # Hours
    
    # Additional Parameters
    oxygen_level = Column(Float, default=21.0)  # Percentage
    agitation_speed = Column(Float, default=200.0)  # RPM
    bioreactor_volume = Column(Float, default=1000.0)  # Liters
    
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")
    
    # Relationships
    user = relationship("User", back_populates="experiments")
    result = relationship("Result", back_populates="experiment", uselist=False)


class Result(Base):
    """Experiment results model"""
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    
    # Predicted Outcomes
    predicted_yield = Column(Float)  # g/L
    energy_usage = Column(Float)  # kWh
    co2_footprint = Column(Float)  # kg CO2
    protein_score = Column(Float)  # 0-100
    
    # Quality Metrics
    purity = Column(Float)  # Percentage
    efficiency = Column(Float)  # Percentage
    
    # Sustainability Score
    sustainability_score = Column(Float)  # 0-100
    
    # AI Explanation
    explanation = Column(Text)
    recommendations = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="result")


class AuditLog(Base):
    """Audit logging for security"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(Integer)
    details = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for getting database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
