from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

class CustomQuestionBase(BaseModel):
    question: str
    required: bool = False
    type: str = "text"

class CustomQuestionCreate(CustomQuestionBase):
    pass

class CustomQuestionResponse(CustomQuestionBase):
    id: int
    scheduling_link_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SchedulingLinkBase(BaseModel):
    title: str
    slug: Optional[str] = None
    meeting_length: int
    buffer_before: int = 0
    buffer_after: int = 0
    max_uses: Optional[int] = None
    expiration_date: Optional[datetime] = None
    max_days_ahead: int
    custom_questions: List[CustomQuestionCreate] = []

class SchedulingLinkCreate(SchedulingLinkBase):
    pass

class SchedulingLinkResponse(SchedulingLinkBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    custom_questions: List[CustomQuestionResponse] = []

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    email: EmailStr
    linkedin_url: HttpUrl
    answers: Dict[int, str]
    meeting_time: datetime

class AvailableSlots(BaseModel):
    date: str
    slots: List[str]

    class Config:
        from_attributes = True

class MeetingResponse(BaseModel):
    id: int
    user_id: int
    scheduling_link_id: int
    email: str
    linkedin_url: str
    meeting_time: datetime
    answers: Dict[int, str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 