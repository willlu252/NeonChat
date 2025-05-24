from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="user")
    daily_metrics = relationship("DailyMetrics", back_populates="user")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    mood_score = Column(Integer)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    sentiment_score = Column(Float)  # -1 to 1
    tags = Column(JSON)  # List of tags
    ai_observations = Column(Text)  # AI therapist notes
    entry_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    word_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="journal_entries")

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today)
    
    # Physical metrics
    sleep_hours = Column(Float)
    water_intake = Column(Integer)  # glasses
    exercise_minutes = Column(Integer)
    steps = Column(Integer)
    
    # Mental/Emotional metrics
    stress_level = Column(Integer)  # 1-10 scale
    anxiety_level = Column(Integer)  # 1-10 scale
    happiness_level = Column(Integer)  # 1-10 scale
    meditation_minutes = Column(Integer)
    
    # Social/Spiritual metrics
    social_interaction_quality = Column(Integer)  # 1-10 scale
    prayer_minutes = Column(Integer)
    gratitude_count = Column(Integer)
    
    # Work/Productivity metrics
    work_satisfaction = Column(Integer)  # 1-10 scale
    productivity_score = Column(Integer)  # 1-10 scale
    
    # Calculated metrics
    wellbeing_score = Column(Float)  # Calculated composite score
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="daily_metrics")

# Pydantic Models for API
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

class JournalEntryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)

class JournalEntryResponse(BaseModel):
    id: str
    title: Optional[str]
    content: str
    mood_score: Optional[int]
    energy_level: Optional[int]
    sentiment_score: Optional[float]
    tags: Optional[List[str]]
    ai_observations: Optional[str]
    entry_date: date
    created_at: datetime
    word_count: int

class DailyMetricsCreate(BaseModel):
    date: Optional[date] = None
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    water_intake: Optional[int] = Field(None, ge=0)
    exercise_minutes: Optional[int] = Field(None, ge=0)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    happiness_level: Optional[int] = Field(None, ge=1, le=10)
    meditation_minutes: Optional[int] = Field(None, ge=0)
    social_interaction_quality: Optional[int] = Field(None, ge=1, le=10)
    prayer_minutes: Optional[int] = Field(None, ge=0)
    work_satisfaction: Optional[int] = Field(None, ge=1, le=10)
    productivity_score: Optional[int] = Field(None, ge=1, le=10)

class DailyMetricsResponse(BaseModel):
    id: str
    date: date
    sleep_hours: Optional[float]
    water_intake: Optional[int]
    exercise_minutes: Optional[int]
    stress_level: Optional[int]
    anxiety_level: Optional[int]
    happiness_level: Optional[int]
    meditation_minutes: Optional[int]
    social_interaction_quality: Optional[int]
    prayer_minutes: Optional[int]
    work_satisfaction: Optional[int]
    productivity_score: Optional[int]
    wellbeing_score: Optional[float]
    created_at: datetime