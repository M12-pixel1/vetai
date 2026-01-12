"""
Database models for the Veterinary AI application.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, 
    ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    VETERINARIAN = "veterinarian"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


class DiagnosisStatus(enum.Enum):
    """Diagnosis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class MediaType(enum.Enum):
    """Media type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"


class Animal(Base):
    """Animal/patient model."""
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100))
    age = Column(Float)  # Age in years
    weight = Column(Float)  # Weight in kg
    sex = Column(String(10))
    owner_name = Column(String(255))
    owner_contact = Column(String(100))
    medical_history = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="animal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Animal(id={self.id}, name='{self.name}', species='{self.species}')>"


class Diagnosis(Base):
    """Diagnosis model for AI-powered veterinary diagnostics."""
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    status = Column(Enum(DiagnosisStatus), default=DiagnosisStatus.PENDING, nullable=False)
    symptoms = Column(Text)
    ai_diagnosis = Column(JSON)  # Store AI results as JSON
    confidence_score = Column(Float)
    veterinarian_notes = Column(Text)
    treatment_plan = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="diagnoses")
    animal = relationship("Animal", back_populates="diagnoses")
    media_files = relationship("MediaFile", back_populates="diagnosis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Diagnosis(id={self.id}, animal_id={self.animal_id}, status='{self.status.value}')>"


class MediaFile(Base):
    """Media file model for images, videos, and audio."""
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=False)
    media_type = Column(Enum(MediaType), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    analysis_result = Column(JSON)  # Store AI analysis results
    thumbnail_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    diagnosis = relationship("Diagnosis", back_populates="media_files")

    def __repr__(self):
        return f"<MediaFile(id={self.id}, type='{self.media_type.value}', diagnosis_id={self.diagnosis_id})>"


class Subscription(Base):
    """Subscription model for payment tracking."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # active, cancelled, expired
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_name}')>"


class AuditLog(Base):
    """Audit log for tracking important actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
