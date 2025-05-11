from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets
import string
import logging
import uuid
from datetime import datetime

from database import get_db
from models import SchedulingLink, User
from schemas import SchedulingLinkCreate, SchedulingLinkResponse, CustomQuestion
from auth import get_current_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scheduling-links", tags=["scheduling-links"])

def generate_slug(length: int = 8) -> str:
    """Generate a random slug for the scheduling link."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/", response_model=SchedulingLinkResponse)
def create_scheduling_link(
    link: SchedulingLinkCreate,
    db: Session = Depends(get_db)
):
    try:
        # Generate a unique slug
        slug = str(uuid.uuid4())[:8]
        
        # Convert CustomQuestion objects to dictionaries
        custom_questions = [q.dict() for q in (link.custom_questions or [])]
        
        # Create new scheduling link
        db_link = SchedulingLink(
            # Temporarily set user_id to None until auth is implemented
            user_id=None,  # Changed from 1 to None
            slug=slug,
            title=link.title,
            max_uses=link.max_uses,
            expiration_date=link.expiration_date,
            custom_questions=custom_questions,  # Now using the converted list
            meeting_length=link.meeting_length,
            max_days_ahead=link.max_days_ahead,
            created_at=datetime.utcnow()
        )
        
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        
        return db_link
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create scheduling link: {str(e)}"
        )

@router.get("/", response_model=List[SchedulingLinkResponse])
def list_scheduling_links(
    db: Session = Depends(get_db)
):
    links = db.query(SchedulingLink).all()
    return links

@router.get("/{slug}", response_model=SchedulingLinkResponse)
async def get_scheduling_link(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a scheduling link by its slug."""
    link = db.query(SchedulingLink).filter(SchedulingLink.slug == slug).first()
    if not link:
        raise HTTPException(status_code=404, detail="Scheduling link not found")
    return link 