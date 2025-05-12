from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import SchedulingWindow
from schemas import SchedulingWindowCreate, SchedulingWindowResponse

router = APIRouter(prefix="/api/scheduling-windows", tags=["scheduling-windows"])

@router.get("/", response_model=List[SchedulingWindowResponse])
async def list_scheduling_windows(db: Session = Depends(get_db)):
    """List all scheduling windows for the current user."""
    # Temporarily hardcoded user_id until auth is implemented
    windows = db.query(SchedulingWindow).filter(SchedulingWindow.user_id == 1).all()
    return windows

@router.post("/", response_model=SchedulingWindowResponse)
async def create_scheduling_window(
    window: SchedulingWindowCreate,
    db: Session = Depends(get_db)
):
    """Create a new scheduling window."""
    print(f"Creating scheduling window: {window}")
    
    # Validate hours
    if window.start_hour < 0 or window.start_hour > 23:
        raise HTTPException(status_code=400, detail="Start hour must be between 0 and 23")
    if window.end_hour < 0 or window.end_hour > 23:
        raise HTTPException(status_code=400, detail="End hour must be between 0 and 23")
    if window.start_hour >= window.end_hour:
        raise HTTPException(status_code=400, detail="Start hour must be before end hour")
    
    # Check for overlapping windows
    existing_window = db.query(SchedulingWindow).filter(
        SchedulingWindow.user_id == 1,
        SchedulingWindow.weekday == window.weekday,
        (
            (SchedulingWindow.start_hour <= window.start_hour) & 
            (SchedulingWindow.end_hour > window.start_hour)
        ) | (
            (SchedulingWindow.start_hour < window.end_hour) & 
            (SchedulingWindow.end_hour >= window.end_hour)
        )
    ).first()
    
    if existing_window:
        print(f"Found overlapping window: {existing_window}")
        raise HTTPException(
            status_code=400,
            detail="This time window overlaps with an existing window"
        )
    
    # Create new window
    db_window = SchedulingWindow(
        user_id=1,  # Temporarily hardcoded until auth is implemented
        weekday=window.weekday,
        start_hour=window.start_hour,
        end_hour=window.end_hour
    )
    
    try:
        db.add(db_window)
        db.commit()
        db.refresh(db_window)
        print(f"Created scheduling window: {db_window}")
        return db_window
    except Exception as e:
        print(f"Error creating scheduling window: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{window_id}")
async def delete_scheduling_window(window_id: int, db: Session = Depends(get_db)):
    """Delete a scheduling window."""
    window = db.query(SchedulingWindow).filter(
        SchedulingWindow.id == window_id,
        SchedulingWindow.user_id == 1  # Temporarily hardcoded until auth is implemented
    ).first()
    
    if not window:
        raise HTTPException(status_code=404, detail="Scheduling window not found")
    
    db.delete(window)
    db.commit()
    
    return {"message": "Scheduling window deleted"} 