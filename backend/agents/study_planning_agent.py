"""
Agent 2: Study Planning Agent
Generates and adapts personalized study plans based on skill profile, weak topics,
target role, interview date, and available daily hours. Dynamically restructures
tasks whenever the student's performance or weak areas shift.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
from backend.agents.base_agent import BaseAgent
from backend.agents.llm_service import llm_service
from backend.database.db import get_db

TASK_TEMPLATES = {
    "theory": [
        ("Concept Mastery & Patterns: {topic}", "Deep dive into {topic} fundamentals. Review algorithmic invariants, trade-offs, and failure points."),
        ("Algorithmic Blueprint: {topic}", "Analyze key recurring patterns in {topic}. Map out recursive vs iterative approaches and state transitions."),
        ("Edge Case & In-Depth Review: {topic}", "Deconstruct boundary conditions, integer overflow, empty collections, and complexity bottlenecks for {topic}.")
    ],
    "practice": [
        ("Targeted Problem Solving: {topic}", "Solve 3 hand-picked interview problems on {topic} prioritizing optimal time and space complexity."),
        ("Timed LeetCode Drill: {topic}", "Practice solving 2 medium difficulty {topic} problems under a strict 40-minute simulated interview timer."),
        ("Pattern Implementation Sprint: {topic}", "Write clean, bug-free implementations for classic {topic} problems from scratch without looking at solutions.")
    ],
    "review": [
        ("Flash Revision & Self-Quiz: {topic}", "Quick 20-minute conceptual check. Explain core {topic} operations out loud and derive big-O complexities."),
        ("Code Review & Optimization: {topic}", "Review past submissions for {topic}. Refactor solutions to reduce memory overhead and eliminate redundant passes.")
    ]
}

class StudyPlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="StudyPlanningAgent",
            description="Designs and dynamically updates personalized study schedules prioritizing weak areas and target interview milestones."
        )

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
            user_id: int
            force_regenerate: bool (optional)
            focus_topics: List[str] (optional hints)
        Output:
            plan_id: int
            title: str
            tasks_created_or_updated: int
            schedule: List[Dict]
            adaptation_note: str
        """
        user_id = input_data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id is required."}

        force_regenerate = bool(input_data.get("force_regenerate", False))

        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Fetch user profile
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            profile = cursor.fetchone()
            target_role = profile["target_role"] if profile else "Software Development Engineer"
            daily_hours = profile["daily_study_hours"] if profile and profile.get("daily_study_hours") else 3.0
            interview_date_str = profile["interview_date"] if profile and profile.get("interview_date") else None
            
            # 2. Fetch weak and moderate topics from skill_profiles
            cursor.execute("""
                SELECT sp.topic_id, sp.proficiency_score, sp.status, t.name as topic_name, s.name as subject_name
                FROM skill_profiles sp
                JOIN topics t ON sp.topic_id = t.id
                JOIN subjects s ON sp.subject_id = s.id
                WHERE sp.user_id = ?
                ORDER BY sp.proficiency_score ASC
            """, (user_id,))
            all_skills = cursor.fetchall()

            weak_topics = [s for s in all_skills if s["status"] == "Weak"]
            moderate_topics = [s for s in all_skills if s["status"] == "Moderate"]
            strong_topics = [s for s in all_skills if s["status"] == "Strong"]

            # Fallback if no skills recorded yet
            if not all_skills:
                cursor.execute("""
                    SELECT t.id as topic_id, 45.0 as proficiency_score, 'Weak' as status, t.name as topic_name, s.name as subject_name
                    FROM topics t
                    JOIN subjects s ON t.subject_id = s.id
                    LIMIT 6
                """)
                weak_topics = cursor.fetchall()

            # 3. Compute timeline
            today = datetime.now()
            if interview_date_str:
                try:
                    target_date = datetime.strptime(interview_date_str, "%Y-%m-%d")
                    days_remaining = max(7, (target_date - today).days)
                except Exception:
                    days_remaining = 28
                    target_date = today + timedelta(days=28)
            else:
                days_remaining = 28
                target_date = today + timedelta(days=28)

            total_weeks = max(1, days_remaining // 7)

            # 4. Handle plan creation / archive
            cursor.execute("SELECT COUNT(*) as count FROM study_plans WHERE user_id = ?", (user_id,))
            total_plans_generated = cursor.fetchone()["count"]

            if force_regenerate:
                # Archive any existing active plans to give a completely clean fresh plan
                cursor.execute("""
                    UPDATE study_plans
                    SET current_status = 'Archived'
                    WHERE user_id = ? AND current_status = 'Active'
                """, (user_id,))

            cursor.execute("""
                SELECT id FROM study_plans
                WHERE user_id = ? AND current_status = 'Active'
                ORDER BY id DESC LIMIT 1
            """, (user_id,))
            existing_plan = cursor.fetchone()

            sprint_iteration = total_plans_generated + 1

            if existing_plan and not force_regenerate:
                plan_id = existing_plan["id"]
                plan_title = f"{total_weeks}-Week Adaptive Prep: {target_role}"
            else:
                plan_title = f"Adaptive Sprint #{sprint_iteration}: {target_role}"
                weak_names = [w["topic_name"] for w in weak_topics[:3]]
                notes = f"Sprint generated {today.strftime('%b %d, %Y')}. Prioritizing weak areas: {', '.join(weak_names) if weak_names else 'General Polish'}."
                cursor.execute("""
                    INSERT INTO study_plans (user_id, title, target_date, total_weeks, current_status, notes)
                    VALUES (?, ?, ?, ?, 'Active', ?)
                """, (user_id, plan_title, target_date.strftime("%Y-%m-%d"), total_weeks, notes))
                plan_id = cursor.lastrowid

            # 5. Generate structured task items (prioritizing weak topics first)
            tasks_to_insert = []
            day_counter = 1

            # High priority tasks for weak topics (Top 3-4 weak topics)
            topics_to_target = weak_topics[:4] if weak_topics else moderate_topics[:4]

            for wt in topics_to_target:
                topic_id = wt["topic_id"]
                topic_name = wt["topic_name"]
                score = wt["proficiency_score"]

                # Pick randomized template for freshness
                t_tmpl = random.choice(TASK_TEMPLATES["theory"])
                p_tmpl = random.choice(TASK_TEMPLATES["practice"])

                # Theory task
                deadline_1 = (today + timedelta(days=day_counter)).strftime("%Y-%m-%d")
                tasks_to_insert.append({
                    "plan_id": plan_id,
                    "user_id": user_id,
                    "topic_id": topic_id,
                    "title": t_tmpl[0].format(topic=topic_name),
                    "description": f"Score: {score}%. " + t_tmpl[1].format(topic=topic_name),
                    "priority": "High",
                    "estimated_minutes": int(daily_hours * 30),
                    "day_number": day_counter,
                    "deadline": deadline_1
                })
                day_counter += 1

                # Practical drill task
                deadline_2 = (today + timedelta(days=day_counter)).strftime("%Y-%m-%d")
                tasks_to_insert.append({
                    "plan_id": plan_id,
                    "user_id": user_id,
                    "topic_id": topic_id,
                    "title": p_tmpl[0].format(topic=topic_name),
                    "description": f"Intensive problem set targeting your weak area in {topic_name}. " + p_tmpl[1].format(topic=topic_name),
                    "priority": "High",
                    "estimated_minutes": int(daily_hours * 45),
                    "day_number": day_counter,
                    "deadline": deadline_2
                })
                day_counter += 1

            # Moderate priority tasks (2 items)
            for mt in moderate_topics[:2]:
                topic_id = mt["topic_id"]
                topic_name = mt["topic_name"]
                r_tmpl = random.choice(TASK_TEMPLATES["review"])
                deadline = (today + timedelta(days=day_counter)).strftime("%Y-%m-%d")
                tasks_to_insert.append({
                    "plan_id": plan_id,
                    "user_id": user_id,
                    "topic_id": topic_id,
                    "title": r_tmpl[0].format(topic=topic_name),
                    "description": f"Reinforce moderate proficiency ({mt['proficiency_score']}%). " + r_tmpl[1].format(topic=topic_name),
                    "priority": "Medium",
                    "estimated_minutes": int(daily_hours * 30),
                    "day_number": day_counter,
                    "deadline": deadline
                })
                day_counter += 1

            # Mock Interview Milestone
            mock_day = min(days_remaining - 1, day_counter)
            tasks_to_insert.append({
                "plan_id": plan_id,
                "user_id": user_id,
                "topic_id": None,
                "title": f"Full Technical & Behavioral Mock Simulation",
                "description": f"End-to-end interview simulation under pressure testing technical accuracy and STAR communication.",
                "priority": "High",
                "estimated_minutes": 60,
                "day_number": mock_day,
                "deadline": (today + timedelta(days=mock_day)).strftime("%Y-%m-%d")
            })

            # If force_regenerate, clear any existing uncompleted tasks in this plan
            if force_regenerate:
                cursor.execute("DELETE FROM study_tasks WHERE study_plan_id = ?", (plan_id,))

            inserted_count = 0
            for t in tasks_to_insert:
                cursor.execute("""
                    INSERT INTO study_tasks (study_plan_id, user_id, topic_id, title, description, priority, estimated_minutes, day_number, deadline, is_completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (t["plan_id"], t["user_id"], t["topic_id"], t["title"], t["description"], t["priority"], t["estimated_minutes"], t["day_number"], t["deadline"]))
                inserted_count += 1

            # 6. Fetch current tasks for output
            cursor.execute("""
                SELECT st.*, t.name as topic_name, s.name as subject_name
                FROM study_tasks st
                LEFT JOIN topics t ON st.topic_id = t.id
                LEFT JOIN subjects s ON t.subject_id = s.id
                WHERE st.study_plan_id = ?
                ORDER BY st.is_completed ASC, st.day_number ASC, st.id ASC
            """, (plan_id,))
            schedule = cursor.fetchall()

        weak_topic_names = [w["topic_name"] for w in weak_topics[:3]]
        adaptation_message = (
            f"AI Study Plan successfully adapted for {target_role}! "
            f"Prioritized {len(weak_topics)} weak topics ({', '.join(weak_topic_names) if weak_topic_names else 'General Mastery'}) "
            f"with {inserted_count} customized high-impact tasks."
        )

        return {
            "plan_id": plan_id,
            "title": plan_title,
            "target_role": target_role,
            "total_weeks": total_weeks,
            "days_to_interview": days_remaining,
            "tasks_updated_or_added": inserted_count,
            "schedule": schedule,
            "adaptation_note": adaptation_message
        }
