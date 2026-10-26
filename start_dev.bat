@echo off
echo ======================================================================
echo  Starting Agentic AI Interview Preparation Tracker
echo ======================================================================

echo Initializing Database and Seed Data...
python -m backend.database.seed_data

echo Starting FastAPI Backend Server on http://127.0.0.1:8000 ...
start "PrepAgent AI Backend" cmd /k "python run_app.py"

echo Starting Vite Frontend on http://127.0.0.1:5173 ...
cd frontend
start "PrepAgent AI Frontend" cmd /k "npm run dev"

echo.
echo System started successfully!
echo Backend:  http://127.0.0.1:8000
echo Swagger:  http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:5173
echo ======================================================================
pause
