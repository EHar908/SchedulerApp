from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv

from database import get_db
from models import User, GoogleCalendar
from schemas import GoogleCalendarResponse
from auth import create_access_token, get_current_user

# Load environment variables
load_dotenv()

# Google OAuth2 configuration
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
]
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

router = APIRouter(prefix="/auth/google", tags=["google-calendar"])

@router.get("/auth")
async def google_auth():
    """Start the Google OAuth2 flow."""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent screen to ensure we get refresh token
    )
    
    return {"authorization_url": authorization_url}

@router.get("/callback")
async def oauth2callback(code: str, db: Session = Depends(get_db)):
    """Handle the OAuth2 callback from Google."""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    
    try:
        # Exchange authorization code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info from Google
        service = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        # Get or create user
        user = db.query(User).filter(User.email == user_info['email']).first()
        if not user:
            user = User(
                email=user_info['email'],
                google_id=user_info.get('id')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Store credentials in database
        calendar = GoogleCalendar(
            user_id=user.id,
            email=user_info['email'],
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=credentials.scopes
        )
        
        db.add(calendar)
        db.commit()
        
        # Create JWT token for the user
        token = create_access_token({"sub": str(user.id)})
        # Redirect to frontend with token as query param
        return RedirectResponse(url=f"{FRONTEND_URL}/login?token={token}")
    except Exception as e:
        print(f"Error in oauth2callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendars", response_model=List[GoogleCalendarResponse])
async def list_calendars(db: Session = Depends(get_db)):
    """List all connected Google calendars for the user."""
    calendars = db.query(GoogleCalendar).filter(GoogleCalendar.user_id == 1).all()  # Temporarily hardcoded
    return calendars

async def fetch_calendar_events(user_id: int, start_date: date, end_date: date, db: Session):
    """Utility function to fetch events from all calendars for a user."""
    print(f"Fetching events from {start_date} to {end_date}")
    calendars = db.query(GoogleCalendar).filter(GoogleCalendar.user_id == user_id).all()
    
    all_events = []
    for calendar in calendars:
        try:
            # Get events from Google Calendar
            events = await get_calendar_events(calendar, start_date, end_date)
            all_events.extend(events)
        except Exception as e:
            print(f"Error fetching events for calendar {calendar.email}: {str(e)}")
            continue
    
    return all_events

@router.get("/events")
async def get_events(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Route handler to get events from all connected calendars for the user."""
    return await fetch_calendar_events(current_user.id, start_date, end_date, db)

@router.delete("/calendars/{calendar_id}")
async def disconnect_calendar(calendar_id: int, db: Session = Depends(get_db)):
    """Disconnect a Google Calendar."""
    calendar = db.query(GoogleCalendar).filter(
        GoogleCalendar.id == calendar_id,
        GoogleCalendar.user_id == 1  # Temporarily hardcoded until auth is implemented
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    db.delete(calendar)
    db.commit()
    
    return {"message": "Calendar disconnected"}

async def get_calendar_events(calendar: GoogleCalendar, start_date: date, end_date: date):
    """Get events from a specific Google Calendar for the given date range."""
    try:
        credentials = google.oauth2.credentials.Credentials(
            token=calendar.access_token,
            refresh_token=calendar.refresh_token,
            token_uri=calendar.token_uri,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=calendar.scopes
        )
        
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except Exception as e:
        print(f"Error fetching events for calendar {calendar.email}: {str(e)}")
        return [] 