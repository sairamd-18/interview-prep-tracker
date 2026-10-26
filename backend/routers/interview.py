"""
Mock Interview Router: Technical and Behavioral Conversational Simulation and Evaluation.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.database.db import get_db
from backend.dependencies import get_current_user
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/interview", tags=["Mock Interview"])

class StartInterviewRequest(BaseModel):
    interview_type: str = "Technical" # Technical, Behavioral, Mixed
    target_role: Optional[str] = "Software Development Engineer (SDE)"

class SubmitAnswerRequest(BaseModel):
    interview_id: int
    question_id: int
    user_response: str

class CompleteInterviewRequest(BaseModel):
    interview_id: int

@router.post("/start")
def start_interview(req: StartInterviewRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    return orchestrator.interview_agent.execute({
        "action": "start_interview",
        "user_id": user_id,
        "interview_type": req.interview_type,
        "target_role": req.target_role
    })

@router.post("/respond")
def submit_answer(req: SubmitAnswerRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    eval_res = orchestrator.interview_agent.execute({
        "action": "submit_answer",
        "question_id": req.question_id,
        "user_response": req.user_response
    })
    return eval_res

@router.post("/complete")
def complete_interview(req: CompleteInterviewRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    summary = orchestrator.on_interview_completed(user_id, req.interview_id)
    return summary

@router.get("/history")
def get_interview_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mi.*, 
                   COUNT(iq.id) as question_count,
                   COUNT(ir.id) as response_count
            FROM mock_interviews mi
            LEFT JOIN interview_questions iq ON mi.id = iq.mock_interview_id
            LEFT JOIN interview_responses ir ON iq.id = ir.interview_question_id
            WHERE mi.user_id = ?
            GROUP BY mi.id
            ORDER BY mi.id DESC
        """, (user_id,))
        return cursor.fetchall()

@router.get("/{interview_id}")
def get_interview_details(interview_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mock_interviews WHERE id = ? AND user_id = ?", (interview_id, user_id))
        interview = cursor.fetchone()
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        cursor.execute("""
            SELECT iq.*, ir.user_response, ir.technical_score, ir.clarity_score,
                   ir.confidence_score, ir.communication_score, ir.relevance_score,
                   ir.feedback, ir.key_strengths, ir.improvement_areas
            FROM interview_questions iq
            LEFT JOIN interview_responses ir ON iq.id = ir.interview_question_id
            WHERE iq.mock_interview_id = ?
            ORDER BY iq.order_idx ASC
        """, (interview_id,))
        questions = cursor.fetchall()

        interview["questions"] = questions
        return interview
