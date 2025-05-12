from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SchedulingWindowBase(BaseModel):
    day_of_week: int
    start_hour: str
    end_hour: str

class SchedulingWindowCreate(SchedulingWindowBase):
    pass

class SchedulingWindowResponse(SchedulingWindowBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 