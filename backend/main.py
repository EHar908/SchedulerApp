from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict
import os
from dotenv import load_dotenv

from routers import scheduling_links, google_calendar, scheduling_windows

# Load environment variables
load_dotenv()

app = FastAPI(title="Scheduler API")

# Get frontend URL from environment variable
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Configure CORS with explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Use environment variable for frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(scheduling_links.router)
app.include_router(google_calendar.router)
app.include_router(scheduling_windows.router)

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Scheduler API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 