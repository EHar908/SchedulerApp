from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
import pytz
import re

from database import get_db
from models import SchedulingLink, CustomQuestion, SchedulingWindow, Meeting
from schemas.scheduling_link import SchedulingLinkCreate, SchedulingLinkResponse, BookingCreate, AvailableSlots
from routers.google_calendar import get_events
from auth import get_current_user

router = APIRouter(
    prefix="/api/scheduling-links",
    tags=["scheduling-links"]
)

def generate_slug(title: str) -> str:
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().replace(" ", "-")
    # Remove any non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    return slug

@router.post("/", response_model=SchedulingLinkResponse)
def create_scheduling_link(
    scheduling_link: SchedulingLinkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Generate slug if not provided
    if not scheduling_link.slug:
        scheduling_link.slug = generate_slug(scheduling_link.title)
    
    # Check if slug already exists
    existing_link = db.query(SchedulingLink).filter(SchedulingLink.slug == scheduling_link.slug).first()
    if existing_link:
        # Append a number to make it unique
        counter = 1
        while existing_link:
            new_slug = f"{scheduling_link.slug}-{counter}"
            existing_link = db.query(SchedulingLink).filter(SchedulingLink.slug == new_slug).first()
            counter += 1
        scheduling_link.slug = new_slug

    db_scheduling_link = SchedulingLink(
        user_id=current_user.id,
        title=scheduling_link.title,
        slug=scheduling_link.slug,
        meeting_length=scheduling_link.meeting_length,
        buffer_before=scheduling_link.buffer_before,
        buffer_after=scheduling_link.buffer_after
    )
    db.add(db_scheduling_link)
    db.flush()  # Flush to get the ID

    # Create custom questions
    for question in scheduling_link.custom_questions:
        db_question = CustomQuestion(
            scheduling_link_id=db_scheduling_link.id,
            question=question.question,
            required=question.required
        )
        db.add(db_question)

    db.commit()
    db.refresh(db_scheduling_link)
    return db_scheduling_link

@router.get("/", response_model=List[SchedulingLinkResponse])
def list_scheduling_links(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(SchedulingLink).filter(SchedulingLink.user_id == current_user.id).all()

@router.get("/{scheduling_link_id}", response_model=SchedulingLinkResponse)
def get_scheduling_link(
    scheduling_link_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    scheduling_link = db.query(SchedulingLink).filter(
        SchedulingLink.id == scheduling_link_id,
        SchedulingLink.user_id == current_user.id
    ).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")
    return scheduling_link

@router.delete("/{scheduling_link_id}")
def delete_scheduling_link(
    scheduling_link_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    scheduling_link = db.query(SchedulingLink).filter(
        SchedulingLink.id == scheduling_link_id,
        SchedulingLink.user_id == current_user.id
    ).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")
    db.delete(scheduling_link)
    db.commit()
    return {"message": "Scheduling link deleted"}

@router.get("/{slug}", response_model=SchedulingLinkResponse)
def get_scheduling_link_by_slug(slug: str, db: Session = Depends(get_db)):
    scheduling_link = db.query(SchedulingLink).filter(SchedulingLink.slug == slug).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")
    return scheduling_link

@router.get("/{link_id}/available-slots", response_model=Dict[str, List[str]])
def get_available_slots(link_id: int, db: Session = Depends(get_db)):
    # Get the scheduling link
    scheduling_link = db.query(SchedulingLink).filter(SchedulingLink.id == link_id).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")

    # Get scheduling windows for the next 7 days
    start_date = datetime.now(pytz.UTC).date()
    end_date = start_date + timedelta(days=7)
    
    windows = db.query(SchedulingWindow).filter(
        SchedulingWindow.user_id == scheduling_link.user_id,
        SchedulingWindow.day_of_week >= start_date.weekday(),
        SchedulingWindow.day_of_week < end_date.weekday() + 7
    ).all()

    # Get Google Calendar events
    events = get_events(scheduling_link.user_id, start_date, end_date)

    # Generate available slots
    available_slots = {}
    current_date = start_date
    while current_date <= end_date:
        day_windows = [w for w in windows if w.day_of_week == current_date.weekday()]
        if day_windows:
            slots = []
            for window in day_windows:
                start_time = datetime.strptime(window.start_hour, "%H:%M").time()
                end_time = datetime.strptime(window.end_hour, "%H:%M").time()
                
                current_time = start_time
                while current_time < end_time:
                    slot_start = datetime.combine(current_date, current_time)
                    slot_end = slot_start + timedelta(minutes=scheduling_link.meeting_length)
                    
                    # Check if slot overlaps with any events
                    slot_available = True
                    for event in events:
                        event_start = event['start'].get('dateTime', event['start'].get('date'))
                        event_end = event['end'].get('dateTime', event['end'].get('date'))
                        
                        if isinstance(event_start, str):
                            event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                        if isinstance(event_end, str):
                            event_end = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                        
                        if (slot_start < event_end and slot_end > event_start):
                            slot_available = False
                            break
                    
                    if slot_available:
                        slots.append(current_time.strftime("%H:%M"))
                    
                    # Move to next slot
                    current_time = (datetime.combine(current_date, current_time) + 
                                  timedelta(minutes=scheduling_link.meeting_length)).time()
            
            if slots:
                available_slots[current_date.isoformat()] = slots
        
        current_date += timedelta(days=1)

    return available_slots

@router.post("/{slug}/book", status_code=status.HTTP_201_CREATED)
def book_meeting(
    slug: str,
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    # Get the scheduling link
    scheduling_link = db.query(SchedulingLink).filter(SchedulingLink.slug == slug).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")

    # Create the meeting
    meeting = Meeting(
        user_id=scheduling_link.user_id,
        scheduling_link_id=scheduling_link.id,
        email=booking.email,
        linkedin_url=booking.linkedin_url,
        meeting_time=booking.meeting_time,
        answers=booking.answers
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # TODO: Create Google Calendar event
    # TODO: Send confirmation emails
    # TODO: Create HubSpot contact

    return {"message": "Meeting booked successfully"} 