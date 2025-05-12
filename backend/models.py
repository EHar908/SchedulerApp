from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    google_id = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    calendars = relationship("Calendar", back_populates="user")
    scheduling_links = relationship("SchedulingLink", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user")
    google_calendars = relationship("GoogleCalendar", back_populates="user", cascade="all, delete-orphan")
    scheduling_windows = relationship("SchedulingWindow", back_populates="user", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="user", cascade="all, delete-orphan")

class Calendar(Base):
    __tablename__ = "calendars"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    calendar_id = Column(String)
    name = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    user = relationship("User", back_populates="calendars")

class SchedulingWindow(Base):
    __tablename__ = "scheduling_windows"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)  # 0 = Monday, 6 = Sunday
    start_hour = Column(String)  # Format: "HH:MM"
    end_hour = Column(String)  # Format: "HH:MM"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="scheduling_windows")

class SchedulingLink(Base):
    __tablename__ = "scheduling_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    slug = Column(String, unique=True, index=True)
    meeting_length = Column(Integer)  # in minutes
    buffer_before = Column(Integer)  # in minutes
    buffer_after = Column(Integer)  # in minutes
    max_uses = Column(Integer, nullable=True)  # Optional limit on number of times link can be used
    expiration_date = Column(DateTime(timezone=True), nullable=True)  # Optional expiration date
    max_days_ahead = Column(Integer)  # Maximum number of days in advance that can be scheduled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="scheduling_links")
    custom_questions = relationship("CustomQuestion", back_populates="scheduling_link", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="scheduling_link", cascade="all, delete-orphan")

class CustomQuestion(Base):
    __tablename__ = "custom_questions"

    id = Column(Integer, primary_key=True, index=True)
    scheduling_link_id = Column(Integer, ForeignKey("scheduling_links.id"))
    question = Column(String)
    required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))

    scheduling_link = relationship("SchedulingLink", back_populates="custom_questions")

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scheduling_link_id = Column(Integer, ForeignKey("scheduling_links.id"))
    email = Column(String)
    linkedin_url = Column(String)
    meeting_time = Column(DateTime(timezone=True))
    answers = Column(JSON)  # Store custom question answers
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="meetings")
    scheduling_link = relationship("SchedulingLink", back_populates="meetings")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    data = Column(JSON)  # For storing session data
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="sessions")

class Cache(Base):
    __tablename__ = "cache"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class GoogleCalendar(Base):
    __tablename__ = "google_calendars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_uri = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    scopes = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="google_calendars") 