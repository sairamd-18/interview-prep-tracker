"""
Main application entry point for the Agentic AI Interview Preparation Tracker backend.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database.db import init_db
from backend.database.seed_data import seed
from backend.routers import auth, profile, assessment, planner, coding, interview, resume, analytics, system

app = FastAPI(
    title="Agentic AI Interview Preparation Tracker API",
    description="Multi-agent AI architecture continuously analyzing, planning, and preparing students for software engineering placements.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(assessment.router)
app.include_router(planner.router)
app.include_router(coding.router)
app.include_router(interview.router)
app.include_router(resume.router)
app.include_router(analytics.router)
app.include_router(system.router)

# Ensure database is initialized on startup
@app.on_event("startup")
def on_startup():
    init_db()
    seed()

# Serve static frontend dist if it exists
dist_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
