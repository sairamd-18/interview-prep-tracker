"""
Convenience launcher for the Agentic AI Interview Preparation Tracker.
Starts FastAPI backend server on http://127.0.0.1:8000.
"""
import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 60)
    print(" PrepAgent AI: Agentic AI Interview Preparation Tracker")
    print("=" * 60)
    print("Starting FastAPI backend on http://127.0.0.1:8000 ...")
    print("Interactive API Docs available at http://127.0.0.1:8000/docs")
    print("Frontend application available at http://127.0.0.1:5173 (or bundled at /)")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
