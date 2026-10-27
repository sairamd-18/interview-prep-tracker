"""
Profile router: View and update student goals and study settings.
hii
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from backend.database.db import get_db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["User Profile"])

class ProfileUpdateRequest(BaseModel):
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    interview_date: Optional[str] = None
    daily_study_hours: Optional[float] = None
    experience_level: Optional[str] = None
    bio: Optional[str] = None

@router.get("")
def get_profile(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (current_user["id"],))
        profile = cursor.fetchone()
        return {"user": current_user, "profile": profile}

@router.put("/update")
def update_profile(req: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_profiles
            SET target_role = COALESCE(?, target_role),
                target_company = COALESCE(?, target_company),
                interview_date = COALESCE(?, interview_date),
                daily_study_hours = COALESCE(?, daily_study_hours),
                experience_level = COALESCE(?, experience_level),
                bio = COALESCE(?, bio),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (req.target_role, req.target_company, req.interview_date, req.daily_study_hours, req.experience_level, req.bio, current_user["id"]))
        
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (current_user["id"],))
        updated = cursor.fetchone()
        return {"status": "success", "profile": updated}
