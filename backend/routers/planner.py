"""
Study Planner router: View adaptive schedules, toggle task status, and trigger AI replanning.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.database.db import get_db
from backend.dependencies import get_current_user
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/planner", tags=["Study Planner"])

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "Medium"
    estimated_minutes: int = 60
    deadline: Optional[str] = None
    topic_id: Optional[int] = None

class PlanGenerateRequest(BaseModel):
    force_regenerate: bool = True

@router.get("/current")
def get_current_plan(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check active plan
        cursor.execute("""
            SELECT * FROM study_plans
            WHERE user_id = ? AND current_status = 'Active'
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        plan = cursor.fetchone()

        if not plan:
            # Trigger StudyPlanningAgent to generate one automatically
            agent_res = orchestrator.study_agent.execute({"user_id": user_id})
            cursor.execute("SELECT * FROM study_plans WHERE id = ?", (agent_res["plan_id"],))
            plan = cursor.fetchone()

        cursor.execute("""
            SELECT st.*, t.name as topic_name, s.name as subject_name
            FROM study_tasks st
            LEFT JOIN topics t ON st.topic_id = t.id
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE st.study_plan_id = ?
            ORDER BY st.is_completed ASC, st.day_number ASC, st.id ASC
        """, (plan["id"],))
        tasks = cursor.fetchall()

        total = len(tasks)
        completed = sum(1 for t in tasks if t["is_completed"] == 1)
        adherence = round((completed / total * 100.0) if total > 0 else 0.0, 1)

        return {
            "plan": plan,
            "tasks": tasks,
            "total_tasks": total,
            "completed_tasks": completed,
            "adherence_rate": adherence
        }

@router.post("/generate")
def generate_study_plan(req: PlanGenerateRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    result = orchestrator.study_agent.execute({
        "user_id": user_id,
        "force_regenerate": req.force_regenerate
    })
    # Update progress record
    orchestrator.progress_agent.execute({"user_id": user_id, "save_snapshot": True})
    return result

@router.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        task = cursor.fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        new_status = 0 if task["is_completed"] == 1 else 1
        cursor.execute("""
            UPDATE study_tasks
            SET is_completed = ?, completed_at = CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE id = ?
        """, (new_status, new_status, task_id))

        cursor.execute("SELECT * FROM study_tasks WHERE id = ?", (task_id,))
        updated_task = cursor.fetchone()

    # Trigger progress recalculation
    orchestrator.progress_agent.execute({"user_id": user_id, "save_snapshot": True})

    return {
        "status": "success",
        "task": updated_task
    }

@router.post("/tasks")
def add_custom_task(req: TaskCreateRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM study_plans WHERE user_id = ? AND current_status = 'Active' ORDER BY id DESC LIMIT 1", (user_id,))
        plan = cursor.fetchone()
        if not plan:
            raise HTTPException(status_code=400, detail="No active study plan. Generate one first.")
            
        cursor.execute("""
            INSERT INTO study_tasks (study_plan_id, user_id, topic_id, title, description, priority, estimated_minutes, deadline, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (plan["id"], user_id, req.topic_id, req.title, req.description, req.priority, req.estimated_minutes, req.deadline))
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM study_tasks WHERE id = ?", (new_id,))
        return cursor.fetchone()
