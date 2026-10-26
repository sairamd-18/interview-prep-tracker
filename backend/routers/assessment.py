"""
Assessment Router: Subjects, Topics, Quizzes, and Skill Profile Analysis.
Triggers SkillAssessmentAgent and cascading orchestrator pipeline upon submission.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from backend.database.db import get_db
from backend.dependencies import get_current_user
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/assessment", tags=["Skill Assessment"])

class QuizAnswerItem(BaseModel):
    question_id: int
    selected_option: int # index 0-3

class QuizSubmissionRequest(BaseModel):
    subject_id: int
    topic_id: Optional[int] = None
    answers: List[QuizAnswerItem]
    time_taken_seconds: int = 60

@router.get("/subjects")
def get_subjects(current_user: dict = Depends(get_current_user)):
    """Fetch all subjects with summary statistics and student's average proficiency."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, 
                   COUNT(DISTINCT t.id) as topic_count,
                   COUNT(DISTINCT q.id) as question_count,
                   AVG(sp.proficiency_score) as user_proficiency
            FROM subjects s
            LEFT JOIN topics t ON t.subject_id = s.id
            LEFT JOIN questions q ON q.topic_id = t.id
            LEFT JOIN skill_profiles sp ON sp.topic_id = t.id AND sp.user_id = ?
            GROUP BY s.id
            ORDER BY s.display_order ASC
        """, (current_user["id"],))
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "name": r["name"],
                "code": r["code"],
                "description": r["description"],
                "icon": r["icon"],
                "topic_count": r["topic_count"],
                "question_count": r["question_count"],
                "user_proficiency": round(r["user_proficiency"] or 50.0, 1)
            })
        return result

@router.get("/topics/{subject_id}")
def get_topics_by_subject(subject_id: int, current_user: dict = Depends(get_current_user)):
    """Fetch topics for a subject with student's current proficiency score and status."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, 
                   COUNT(q.id) as question_count,
                   COALESCE(sp.proficiency_score, 50.0) as proficiency_score,
                   COALESCE(sp.status, 'Moderate') as status,
                   COALESCE(sp.quizzes_taken, 0) as quizzes_taken
            FROM topics t
            LEFT JOIN questions q ON q.topic_id = t.id
            LEFT JOIN skill_profiles sp ON sp.topic_id = t.id AND sp.user_id = ?
            WHERE t.subject_id = ?
            GROUP BY t.id
        """, (current_user["id"], subject_id))
        return cursor.fetchall()

@router.get("/quiz")
def get_quiz_questions(
    subject_id: Optional[str] = Query(None),
    topic_id: Optional[str] = Query(None),
    limit: int = 4
):
    """
    Retrieve randomized quiz questions.
    Safely handles string or int parameters, including 'undefined' and 'null'.
    """
    sid = None
    if subject_id and subject_id not in ("undefined", "null", ""):
        try:
            sid = int(subject_id)
        except (ValueError, TypeError):
            sid = None

    tid = None
    if topic_id and topic_id not in ("undefined", "null", ""):
        try:
            tid = int(topic_id)
        except (ValueError, TypeError):
            tid = None

    with get_db() as conn:
        cursor = conn.cursor()
        if tid:
            cursor.execute("""
                SELECT q.id, q.topic_id, t.name as topic_name, q.question_text, q.options_json, q.difficulty
                FROM questions q
                JOIN topics t ON q.topic_id = t.id
                WHERE q.topic_id = ?
                ORDER BY RANDOM() LIMIT ?
            """, (tid, limit))
        elif sid:
            cursor.execute("""
                SELECT q.id, q.topic_id, t.name as topic_name, q.question_text, q.options_json, q.difficulty
                FROM questions q
                JOIN topics t ON q.topic_id = t.id
                WHERE t.subject_id = ?
                ORDER BY RANDOM() LIMIT ?
            """, (sid, limit))
        else:
            cursor.execute("""
                SELECT q.id, q.topic_id, t.name as topic_name, q.question_text, q.options_json, q.difficulty
                FROM questions q
                JOIN topics t ON q.topic_id = t.id
                ORDER BY RANDOM() LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        output = []
        for r in rows:
            output.append({
                "id": r["id"],
                "topic_id": r["topic_id"],
                "topic_name": r["topic_name"],
                "question_text": r["question_text"],
                "options": json.loads(r["options_json"]),
                "difficulty": r["difficulty"]
            })
        return output

@router.post("/submit")
def submit_quiz(submission: QuizSubmissionRequest, current_user: dict = Depends(get_current_user)):
    """
    Submits quiz responses, grades correctness, and initiates the multi-agent cascade
    through the AgentOrchestrator.
    """
    user_id = current_user["id"]
    if not submission.answers:
        raise HTTPException(status_code=400, detail="No answers submitted.")

    detailed_evals = []
    correct_count = 0

    with get_db() as conn:
        cursor = conn.cursor()
        for ans in submission.answers:
            cursor.execute("SELECT * FROM questions WHERE id = ?", (ans.question_id,))
            q_row = cursor.fetchone()
            if not q_row:
                continue

            is_correct = (ans.selected_option == q_row["correct_answer"])
            if is_correct:
                correct_count += 1

            detailed_evals.append({
                "question_id": q_row["id"],
                "topic_id": q_row["topic_id"],
                "question_text": q_row["question_text"],
                "options": json.loads(q_row["options_json"]),
                "selected_option": ans.selected_option,
                "correct_answer": q_row["correct_answer"],
                "is_correct": is_correct,
                "explanation": q_row["explanation"],
                "difficulty": q_row["difficulty"]
            })

        total = len(submission.answers)
        score_pct = round((correct_count / total * 100.0) if total > 0 else 0.0, 1)

        # Record attempt
        cursor.execute("""
            INSERT INTO quiz_attempts (user_id, subject_id, topic_id, total_questions, correct_answers, score_percentage, time_taken_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, submission.subject_id, submission.topic_id, total, correct_count, score_pct, submission.time_taken_seconds))
        attempt_id = cursor.lastrowid

    # Trigger multi-agent orchestrator pipeline!
    orchestrator_result = orchestrator.on_quiz_completed(user_id, detailed_evals)

    return {
        "attempt_id": attempt_id,
        "total_questions": total,
        "correct_answers": correct_count,
        "score_percentage": score_pct,
        "detailed_results": detailed_evals,
        "orchestrator_pipeline": orchestrator_result
    }

@router.get("/skill-profile")
def get_skill_profile(current_user: dict = Depends(get_current_user)):
    """Retrieve student's full skill profile across all topics and subjects."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sp.*, t.name as topic_name, s.name as subject_name, s.code as subject_code
            FROM skill_profiles sp
            JOIN topics t ON sp.topic_id = t.id
            JOIN subjects s ON sp.subject_id = s.id
            WHERE sp.user_id = ?
            ORDER BY s.display_order ASC, sp.proficiency_score ASC
        """, (current_user["id"],))
        rows = cursor.fetchall()
        
        weak = [r for r in rows if r["status"] == "Weak"]
        moderate = [r for r in rows if r["status"] == "Moderate"]
        strong = [r for r in rows if r["status"] == "Strong"]

        return {
            "all_skills": rows,
            "weak_topics": weak,
            "moderate_topics": moderate,
            "strong_topics": strong,
            "total_evaluated_topics": len(rows)
        }
