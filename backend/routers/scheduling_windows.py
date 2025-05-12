from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import SchedulingWindow
from schemas.scheduling_window import SchedulingWindowCreate, SchedulingWindowResponse

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
    
    try:
        # Parse the time strings
        start_hour = int(window.start_hour.split(':')[0])
        end_hour = int(window.end_hour.split(':')[0])
        
        # Validate hours
        if start_hour < 0 or start_hour > 23:
            raise HTTPException(status_code=400, detail="Start hour must be between 0 and 23")
        if end_hour < 0 or end_hour > 23:
            raise HTTPException(status_code=400, detail="End hour must be between 0 and 23")
        if start_hour >= end_hour:
            raise HTTPException(status_code=400, detail="Start hour must be before end hour")
        
        # Check for overlapping windows
        existing_window = db.query(SchedulingWindow).filter(
            SchedulingWindow.user_id == 1,
            SchedulingWindow.day_of_week == window.day_of_week,
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
            day_of_week=window.day_of_week,
            start_hour=window.start_hour,
            end_hour=window.end_hour
        )
        
        db.add(db_window)
        db.commit()
        db.refresh(db_window)
        # Ensure updated_at is set
        if db_window.updated_at is None:
            db_window.updated_at = db_window.created_at
            db.commit()
            db.refresh(db_window)
        print(f"Created scheduling window: {db_window}")
        return db_window
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Expected HH:MM")
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