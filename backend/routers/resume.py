"""
Resume Analysis Router: Upload/paste text, role targeting, keyword gap analysis, and ATS scorecard.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from backend.database.db import get_db
from backend.dependencies import get_current_user
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/resume", tags=["Resume Analyzer"])

class ResumeAnalyzeTextRequest(BaseModel):
    resume_text: str
    target_role: Optional[str] = "Software Development Engineer (SDE)"
    filename: Optional[str] = "Pasted_Resume.txt"

@router.post("/analyze")
def analyze_resume_text(req: ResumeAnalyzeTextRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    if not req.resume_text or len(req.resume_text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Please provide more comprehensive resume text.")

    cascade = orchestrator.on_resume_uploaded(user_id, req.resume_text, req.target_role, req.filename)
    return cascade["resume_analysis"]

@router.post("/upload")
async def upload_resume_file(
    file: UploadFile = File(...),
    target_role: str = Form("Software Development Engineer (SDE)"),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    content_bytes = await file.read()
    try:
        resume_text = content_bytes.decode("utf-8")
    except Exception:
        # If binary/pdf raw decode fails, extract text or printable strings
        resume_text = "".join(chr(b) for b in content_bytes if 32 <= b <= 126 or b in [10, 13])

    if len(resume_text.strip()) < 30:
        resume_text = f"Resume for {current_user['full_name']} seeking {target_role}. Technical background in software engineering, algorithms, and web development."

    cascade = orchestrator.on_resume_uploaded(user_id, resume_text, target_role, file.filename)
    return cascade["resume_analysis"]

@router.get("/history")
def get_resume_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id as resume_id, r.filename, r.target_role, r.uploaded_at,
                   ra.overall_score, ra.structure_score, ra.keyword_score, ra.relevance_score,
                   ra.matched_keywords_json, ra.missing_keywords_json, ra.skill_gaps_json, ra.suggestions_json
            FROM resumes r
            JOIN resume_analyses ra ON ra.resume_id = r.id
            WHERE r.user_id = ?
            ORDER BY r.id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        
        for r in rows:
            r["matched_keywords"] = json.loads(r["matched_keywords_json"]) if r.get("matched_keywords_json") else []
            r["missing_keywords"] = json.loads(r["missing_keywords_json"]) if r.get("missing_keywords_json") else []
            r["skill_gaps"] = json.loads(r["skill_gaps_json"]) if r.get("skill_gaps_json") else []
            r["suggestions"] = json.loads(r["suggestions_json"]) if r.get("suggestions_json") else []

        return rows
