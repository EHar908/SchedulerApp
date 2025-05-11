from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class CustomQuestion(BaseModel):
    question: str
    required: bool = False
    type: str = "text"  # text, email, phone, etc.

class SchedulingLinkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    meeting_length: int = Field(..., ge=15, le=480)  # 15 minutes to 8 hours
    max_uses: Optional[int] = Field(None, ge=1)
    expiration_date: Optional[datetime] = None
    max_days_ahead: int = Field(..., ge=1, le=365)
    custom_questions: Optional[List[CustomQuestion]] = []

class SchedulingLinkResponse(BaseModel):
    id: int
    slug: str
    title: str
    meeting_length: int
    max_uses: Optional[int]
    expiration_date: Optional[datetime]
    max_days_ahead: int
    custom_questions: List[CustomQuestion]
    created_at: datetime

    class Config:
        from_attributes = True 