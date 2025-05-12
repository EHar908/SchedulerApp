from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GoogleCalendarEvent(BaseModel):
    id: str
    summary: str
    start: dict
    end: dict
    description: Optional[str] = None
    location: Optional[str] = None

class GoogleCalendarResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True 