"""
Progress Analytics Router: Readiness Dashboard, Multi-Agent Performance Metrics, and Trends.
"""
from fastapi import APIRouter, Depends
from backend.database.db import get_db
from backend.dependencies import get_current_user
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/analytics", tags=["Progress Analytics"])

@router.get("/dashboard")
def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Fetches high-level readiness dashboard from ProgressMonitoringAgent."""
    user_id = current_user["id"]
    return orchestrator.progress_agent.execute({"user_id": user_id, "save_snapshot": False})

@router.get("/metrics")
def get_performance_metrics(current_user: dict = Depends(get_current_user)):
    """Fetches 8 research & system performance metrics calculated by the orchestrator."""
    user_id = current_user["id"]
    return orchestrator.get_system_performance_metrics(user_id)

@router.get("/trends")
def get_trends(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM progress_records
            WHERE user_id = ?
            ORDER BY id ASC
            LIMIT 30
        """, (user_id,))
        records = cursor.fetchall()
        return records

@router.get("/recent-activity")
def get_recent_activity(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    activity = []
    with get_db() as conn:
        cursor = conn.cursor()

        # Quizzes
        cursor.execute("""
            SELECT 'quiz' as type, s.name as subject_name, qa.score_percentage as score, qa.created_at
            FROM quiz_attempts qa
            JOIN subjects s ON qa.subject_id = s.id
            WHERE qa.user_id = ?
            ORDER BY qa.id DESC LIMIT 5
        """, (user_id,))
        for q in cursor.fetchall():
            activity.append({
                "type": "quiz",
                "title": f"Quiz in {q['subject_name']}",
                "detail": f"Scored {q['score']}%",
                "timestamp": q["created_at"]
            })

        # Coding submissions
        cursor.execute("""
            SELECT 'coding' as type, cp.title, cs.status, cs.created_at
            FROM coding_submissions cs
            JOIN coding_problems cp ON cs.problem_id = cp.id
            WHERE cs.user_id = ?
            ORDER BY cs.id DESC LIMIT 5
        """, (user_id,))
        for c in cursor.fetchall():
            activity.append({
                "type": "coding",
                "title": f"Coded '{c['title']}'",
                "detail": f"Status: {c['status']}",
                "timestamp": c["created_at"]
            })

        # Mock interviews
        cursor.execute("""
            SELECT 'interview' as type, interview_type, overall_score, completed_at
            FROM mock_interviews
            WHERE user_id = ? AND status = 'Completed'
            ORDER BY id DESC LIMIT 3
        """, (user_id,))
        for mi in cursor.fetchall():
            activity.append({
                "type": "interview",
                "title": f"{mi['interview_type']} Mock Interview",
                "detail": f"Rated {mi['overall_score']}/100",
                "timestamp": mi["completed_at"]
            })

        # Sort combined activity chronologically
        activity.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
        return activity[:10]
