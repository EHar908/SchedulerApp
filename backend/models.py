from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    google_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    calendars = relationship("Calendar", back_populates="user")
    scheduling_links = relationship("SchedulingLink", back_populates="user")

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
    weekday = Column(Integer)  # 0-6 for Monday-Sunday
    start_hour = Column(Integer)  # 0-23
    end_hour = Column(Integer)  # 0-23
    created_at = Column(DateTime, default=datetime.utcnow)

class SchedulingLink(Base):
    __tablename__ = "scheduling_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    slug = Column(String, unique=True, index=True)
    max_uses = Column(Integer, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    custom_questions = Column(JSON)  # List of question objects
    meeting_length = Column(Integer)  # in minutes
    max_days_ahead = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="scheduling_links")
    bookings = relationship("Booking", back_populates="scheduling_link")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    scheduling_link_id = Column(Integer, ForeignKey("scheduling_links.id"))
    email = Column(String)
    linkedin_url = Column(String)
    answers = Column(JSON)  # Map of question IDs to answers
    meeting_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduling_link = relationship("SchedulingLink", back_populates="bookings") 