"""
Agent 6: Progress Monitoring Agent
Central intelligence aggregator. Dynamically computes the composite Placement Readiness Score,
aggregates subject proficiency, coding submission metrics, interview scores, and study plan adherence,
tracks historical trends, and formulates prioritized next actions.
"""
from typing import Dict, Any, List
from datetime import datetime
from backend.agents.base_agent import BaseAgent
from backend.database.db import get_db

class ProgressMonitoringAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ProgressMonitoringAgent",
            description="Aggregates preparation activities across all 5 agents, computes the composite Placement Readiness Score, and pinpoints next actions."
        )

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
            user_id: int
            save_snapshot: bool (default True)
        Output:
            overall_readiness_score: float
            subject_proficiency: Dict[str, float]
            coding_progress: Dict[str, Any]
            mock_interview_performance: Dict[str, Any]
            resume_score: float
            study_plan_adherence: float
            weak_topics: List[Dict]
            progress_trends: List[Dict]
            recommended_next_actions: List[Dict]
        """
        user_id = input_data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id is required"}

        save_snapshot = input_data.get("save_snapshot", True)

        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Subject-wise proficiency and weak topics from skill_profiles
            cursor.execute("""
                SELECT s.code, s.name as subject_name, AVG(sp.proficiency_score) as avg_score
                FROM subjects s
                LEFT JOIN topics t ON t.subject_id = s.id
                LEFT JOIN skill_profiles sp ON sp.topic_id = t.id AND sp.user_id = ?
                GROUP BY s.id, s.code, s.name
                ORDER BY s.display_order ASC
            """, (user_id,))
            subject_rows = cursor.fetchall()
            
            subject_scores = {}
            for r in subject_rows:
                code = r["code"].lower()
                subject_scores[code] = round(r["avg_score"] or 50.0, 1)

            # Weak topics
            cursor.execute("""
                SELECT sp.proficiency_score, sp.status, t.name as topic_name, s.name as subject_name
                FROM skill_profiles sp
                JOIN topics t ON sp.topic_id = t.id
                JOIN subjects s ON sp.subject_id = s.id
                WHERE sp.user_id = ? AND sp.status = 'Weak'
                ORDER BY sp.proficiency_score ASC
                LIMIT 5
            """, (user_id,))
            weak_topics = cursor.fetchall()

            # Average skill score
            all_skill_avg = sum(subject_scores.values()) / len(subject_scores) if subject_scores else 50.0

            # 2. Coding Progress
            cursor.execute("""
                SELECT COUNT(DISTINCT problem_id) as solved_count
                FROM coding_submissions
                WHERE user_id = ? AND status = 'Accepted'
            """, (user_id,))
            solved = cursor.fetchone()["solved_count"]

            cursor.execute("SELECT COUNT(*) as total_problems FROM coding_problems")
            total_prob = cursor.fetchone()["total_problems"]
            coding_pct = round((solved / total_prob * 100.0) if total_prob > 0 else 0.0, 1)

            coding_data = {
                "solved_count": solved,
                "total_problems": total_prob,
                "completion_percentage": coding_pct
            }

            # 3. Mock Interview Performance
            cursor.execute("""
                SELECT AVG(overall_score) as avg_score, COUNT(*) as interview_count
                FROM mock_interviews
                WHERE user_id = ? AND status = 'Completed'
            """, (user_id,))
            mock_row = cursor.fetchone()
            interview_avg = round(mock_row["avg_score"] or 65.0, 1)
            interview_count = mock_row["interview_count"]

            interview_data = {
                "average_score": interview_avg,
                "completed_sessions": interview_count
            }

            # 4. Resume Score
            cursor.execute("""
                SELECT ra.overall_score
                FROM resume_analyses ra
                JOIN resumes r ON ra.resume_id = r.id
                WHERE r.user_id = ?
                ORDER BY ra.id DESC LIMIT 1
            """, (user_id,))
            res_row = cursor.fetchone()
            resume_score = round(res_row["overall_score"] if res_row else 70.0, 1)

            # 5. Study Plan Adherence
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_tasks
                FROM study_tasks
                WHERE user_id = ?
            """, (user_id,))
            task_row = cursor.fetchone()
            total_tasks = task_row["total_tasks"]
            completed_tasks = task_row["completed_tasks"] or 0
            plan_adherence = round((completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0, 1)

            # 6. Composite Placement Readiness Formula:
            # 35% Skills + 25% Coding + 20% Mock Interviews + 10% Resume + 10% Study Plan Adherence
            composite_readiness = (
                0.35 * all_skill_avg +
                0.25 * coding_pct +
                0.20 * interview_avg +
                0.10 * resume_score +
                0.10 * plan_adherence
            )
            composite_readiness = round(min(100.0, max(0.0, composite_readiness)), 1)

            # 7. Record historical progress record snapshot
            if save_snapshot:
                cursor.execute("""
                    INSERT INTO progress_records (
                        user_id, readiness_score, dsa_score, dbms_score, os_score,
                        cn_score, oop_score, aptitude_score, behavioral_score,
                        coding_completion_pct, resume_score, interview_avg_score,
                        study_plan_adherence, recorded_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    user_id, composite_readiness,
                    subject_scores.get("dsa", 50.0),
                    subject_scores.get("dbms", 50.0),
                    subject_scores.get("os", 50.0),
                    subject_scores.get("cn", 50.0),
                    subject_scores.get("oop", 50.0),
                    subject_scores.get("apt", 50.0),
                    subject_scores.get("beh", 50.0),
                    coding_pct, resume_score, interview_avg, plan_adherence
                ))

            # 8. Historical Trends
            cursor.execute("""
                SELECT readiness_score, dsa_score, coding_completion_pct, recorded_at
                FROM progress_records
                WHERE user_id = ?
                ORDER BY id ASC
                LIMIT 14
            """, (user_id,))
            trends = cursor.fetchall()

            # 9. Formulate recommended next actions
            recommended_actions = []
            if weak_topics:
                wt_name = weak_topics[0]["topic_name"]
                recommended_actions.append({
                    "priority": "High",
                    "title": f"Revise {wt_name}",
                    "reason": f"Topic proficiency is currently at {weak_topics[0]['proficiency_score']}%. Targeted practice will provide the highest readiness gain.",
                    "action_type": "coding_or_quiz",
                    "target": wt_name
                })
            
            if plan_adherence < 70.0:
                recommended_actions.append({
                    "priority": "Medium",
                    "title": "Complete Pending Study Tasks",
                    "reason": f"Study plan adherence is {plan_adherence}%. Staying on schedule ensures full syllabus coverage before the target interview date.",
                    "action_type": "study_plan",
                    "target": "study_planner"
                })

            if interview_count < 2:
                recommended_actions.append({
                    "priority": "High",
                    "title": "Simulate a Technical Mock Interview",
                    "reason": "Mock interview practice increases communication fluency and prepares you for live question pressure.",
                    "action_type": "mock_interview",
                    "target": "Technical"
                })

            if resume_score < 80.0:
                recommended_actions.append({
                    "priority": "Medium",
                    "title": "Enhance Resume Keywords",
                    "reason": f"Current resume ATS score is {resume_score}%. Incorporating missing role keywords will improve recruiter screening.",
                    "action_type": "resume",
                    "target": "resume_analyzer"
                })

        return {
            "overall_readiness_score": composite_readiness,
            "subject_proficiency": subject_scores,
            "coding_progress": coding_data,
            "mock_interview_performance": interview_data,
            "resume_score": resume_score,
            "study_plan_adherence": plan_adherence,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "weak_topics": weak_topics,
            "progress_trends": trends,
            "recommended_next_actions": recommended_actions
        }
