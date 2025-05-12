from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict

from routers import scheduling_links, google_calendar, scheduling_windows

app = FastAPI(title="Scheduler API")

# Configure CORS with explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=False,  # Set to False when using wildcard origins
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