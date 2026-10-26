"""
Authentication router: Login, Register, and Current User profile.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.database.db import get_db
from backend.auth_utils import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    target_role: str = "Software Development Engineer (SDE)"

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(req: RegisterRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (req.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        pwd_hash = hash_password(req.password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, 'student')",
            (req.email, pwd_hash, req.full_name)
        )
        user_id = cursor.lastrowid

        # Create initial profile
        cursor.execute(
            "INSERT INTO user_profiles (user_id, target_role) VALUES (?, ?)",
            (user_id, req.target_role)
        )

        token = create_access_token({"sub": user_id, "email": req.email, "name": req.full_name})
        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": req.email,
                "full_name": req.full_name,
                "role": "student",
                "target_role": req.target_role
            }
        }

@router.post("/login")
def login(req: LoginRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password_hash, full_name, role FROM users WHERE email = ?", (req.email,))
        user = cursor.fetchone()
        if not user or not verify_password(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        token = create_access_token({"sub": user["id"], "email": user["email"], "name": user["full_name"]})
        
        cursor.execute("SELECT target_role, daily_study_hours, interview_date FROM user_profiles WHERE user_id = ?", (user["id"],))
        prof = cursor.fetchone() or {}

        return {
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "target_role": prof.get("target_role", "Software Development Engineer"),
                "daily_study_hours": prof.get("daily_study_hours", 3.0),
                "interview_date": prof.get("interview_date")
            }
        }

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (current_user["id"],))
        profile = cursor.fetchone() or {}
        
    return {
        "user": current_user,
        "profile": profile
    }
