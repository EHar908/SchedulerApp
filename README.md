# Scheduler App

A Calendly-like scheduling tool for advisors to meet with their clients.

## Features

- Google Calendar integration
- Multiple calendar support
- HubSpot CRM integration
- Custom scheduling windows
- Customizable scheduling links
- LinkedIn profile scraping
- AI-enhanced meeting notes

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- Redis
- Google Calendar API
- HubSpot API

### Frontend
- React with TypeScript
- Tailwind CSS
- React Query
- React Router
- React Hook Form

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Fill in the required environment variables

4. Set up the database:
```bash
# Create a PostgreSQL database named 'scheduler'
# Update DATABASE_URL in .env with your database credentials
```

5. Run the backend:
```bash
cd backend
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Development

The backend API will be available at `http://localhost:8000`
The frontend development server will be available at `http://localhost:3000`

## Deployment

This application is designed to be deployed on Render.com. Follow these steps:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the required environment variables in Render's dashboard

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive API documentation. 