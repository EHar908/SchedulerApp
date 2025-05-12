from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
import pytz
import re

from database import get_db
from models import SchedulingLink, CustomQuestion, SchedulingWindow, Meeting
from schemas.scheduling_link import SchedulingLinkCreate, SchedulingLinkResponse, BookingCreate, AvailableSlots, MeetingResponse
from routers.google_calendar import fetch_calendar_events
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
        buffer_after=scheduling_link.buffer_after,
        max_uses=scheduling_link.max_uses,
        expiration_date=scheduling_link.expiration_date,
        max_days_ahead=scheduling_link.max_days_ahead
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

@router.get("/slug/{slug}", response_model=SchedulingLinkResponse)
def get_scheduling_link_by_slug(slug: str, db: Session = Depends(get_db)):
    scheduling_link = db.query(SchedulingLink).filter(SchedulingLink.slug == slug).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")
    return scheduling_link

@router.get("/{link_id}/available-slots", response_model=Dict[str, List[str]])
async def get_available_slots(link_id: int, db: Session = Depends(get_db)):
    # Get the scheduling link
    scheduling_link = db.query(SchedulingLink).filter(SchedulingLink.id == link_id).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")

    # Check if link has expired
    if scheduling_link.expiration_date and scheduling_link.expiration_date < datetime.now(pytz.UTC):
        raise HTTPException(status_code=400, detail="This scheduling link has expired")

    # Check if link has reached its usage limit
    if scheduling_link.max_uses:
        current_uses = db.query(Meeting).filter(Meeting.scheduling_link_id == link_id).count()
        if current_uses >= scheduling_link.max_uses:
            raise HTTPException(status_code=400, detail="This scheduling link has reached its usage limit")

    # Get scheduling windows for the next max_days_ahead days
    start_date = datetime.now(pytz.UTC).date()
    end_date = start_date + timedelta(days=scheduling_link.max_days_ahead)
    
    windows = db.query(SchedulingWindow).filter(
        SchedulingWindow.user_id == scheduling_link.user_id,
        SchedulingWindow.day_of_week >= start_date.weekday(),
        SchedulingWindow.day_of_week < end_date.weekday() + 7
    ).all()

    # Get Google Calendar events
    events = await fetch_calendar_events(scheduling_link.user_id, start_date, end_date, db)

    # Generate available slots
    available_slots = {}
    current_date = start_date
    while current_date <= end_date:
        day_slots = []
        day_windows = [w for w in windows if w.day_of_week == current_date.weekday()]
        
        for window in day_windows:
            # Parse start and end hours
            start_hour, start_minute = map(int, window.start_hour.split(':'))
            end_hour, end_minute = map(int, window.end_hour.split(':'))
            
            # Create start and end times for this window
            start_time = datetime.combine(current_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
            end_time = datetime.combine(current_date, datetime.min.time().replace(hour=end_hour, minute=end_minute))
            
            # Generate slots within this window
            current_slot = start_time
            while current_slot + timedelta(minutes=scheduling_link.meeting_length) <= end_time:
                # Check if this slot overlaps with any existing events
                slot_end = current_slot + timedelta(minutes=scheduling_link.meeting_length)
                is_available = True
                
                for event in events:
                    event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                    event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                    
                    if (current_slot < event_end and slot_end > event_start):
                        is_available = False
                        break
                
                if is_available:
                    day_slots.append(current_slot.strftime('%H:%M'))
                
                current_slot += timedelta(minutes=scheduling_link.meeting_length)
        
        if day_slots:
            available_slots[current_date.strftime('%Y-%m-%d')] = day_slots
        
        current_date += timedelta(days=1)
    
    return available_slots

@router.post("/{link_id}/book", response_model=MeetingResponse)
async def book_meeting(
    link_id: int,
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    print(f"Attempting to book meeting for link {link_id}")
    print(f"Meeting time: {booking.meeting_time}")
    
    # Get the scheduling link
    scheduling_link = db.query(SchedulingLink).filter(SchedulingLink.id == link_id).first()
    if not scheduling_link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")
    
    print(f"Found scheduling link: {scheduling_link.title}")
    print(f"Meeting length: {scheduling_link.meeting_length} minutes")

    # Check if link has expired
    if scheduling_link.expiration_date and scheduling_link.expiration_date < datetime.now(pytz.UTC):
        print(f"Link expired on {scheduling_link.expiration_date}")
        raise HTTPException(status_code=400, detail="This scheduling link has expired")

    # Check if link has reached its usage limit
    if scheduling_link.max_uses:
        current_uses = db.query(Meeting).filter(Meeting.scheduling_link_id == link_id).count()
        print(f"Current uses: {current_uses}, Max uses: {scheduling_link.max_uses}")
        if current_uses >= scheduling_link.max_uses:
            raise HTTPException(status_code=400, detail="This scheduling link has reached its usage limit")

    # Validate meeting time is within scheduling windows
    meeting_time = booking.meeting_time
    if meeting_time.tzinfo is None:
        meeting_time = pytz.UTC.localize(meeting_time)
    
    print(f"Meeting time (UTC): {meeting_time}")
    print(f"Meeting day of week (UTC): {meeting_time.weekday()}")

    # Get all scheduling windows for the user to debug
    all_windows = db.query(SchedulingWindow).filter(
        SchedulingWindow.user_id == scheduling_link.user_id
    ).all()
    print("All scheduling windows for user:")
    for window in all_windows:
        print(f"Day {window.day_of_week}: {window.start_hour} - {window.end_hour}")

    # Get scheduling windows for the meeting day using UTC time
    windows = db.query(SchedulingWindow).filter(
        SchedulingWindow.user_id == scheduling_link.user_id,
        SchedulingWindow.day_of_week == meeting_time.weekday()
    ).all()

    print(f"Found {len(windows)} scheduling windows for day {meeting_time.weekday()}")
    for window in windows:
        print(f"Window: {window.start_hour} - {window.end_hour}")

    if not windows:
        raise HTTPException(status_code=400, detail="No scheduling windows available for this day")

    # Check if meeting time is within any window
    meeting_end = meeting_time + timedelta(minutes=scheduling_link.meeting_length)
    time_in_window = False
    for window in windows:
        # Parse start and end hours
        start_hour, start_minute = map(int, window.start_hour.split(':'))
        end_hour, end_minute = map(int, window.end_hour.split(':'))
        
        # Create timezone-aware datetime objects in UTC
        window_start = datetime.combine(meeting_time.date(), datetime.min.time().replace(hour=start_hour, minute=start_minute))
        window_start = pytz.UTC.localize(window_start)
        window_end = datetime.combine(meeting_time.date(), datetime.min.time().replace(hour=end_hour, minute=end_minute))
        window_end = pytz.UTC.localize(window_end)
        
        print(f"Checking window (UTC): {window_start} - {window_end}")
        print(f"Meeting (UTC): {meeting_time} - {meeting_end}")
        
        # Compare times in UTC
        if window_start <= meeting_time and meeting_end <= window_end:
            time_in_window = True
            print("Meeting time is within this window")
            break

    if not time_in_window:
        print("Meeting time is not within any available window")
        raise HTTPException(status_code=400, detail="Meeting time is not within available scheduling windows")

    # Check if time slot is available (not in events)
    events = await fetch_calendar_events(scheduling_link.user_id, meeting_time.date(), meeting_time.date(), db)
    print(f"Found {len(events)} existing events for this day")
    
    for event in events:
        event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
        
        # Ensure event times are timezone-aware
        if event_start.tzinfo is None:
            event_start = pytz.UTC.localize(event_start)
        if event_end.tzinfo is None:
            event_end = pytz.UTC.localize(event_end)
        
        print(f"Checking event: {event_start} - {event_end}")
        
        if (meeting_time < event_end and meeting_end > event_start):
            print("Meeting time conflicts with existing event")
            raise HTTPException(status_code=400, detail="This time slot is not available")

    # Create the meeting
    meeting = Meeting(
        user_id=scheduling_link.user_id,
        scheduling_link_id=link_id,
        email=booking.email,
        linkedin_url=booking.linkedin_url,
        meeting_time=meeting_time,  # Store in UTC
        answers=booking.answers
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    print("Successfully created meeting")
    return meeting 