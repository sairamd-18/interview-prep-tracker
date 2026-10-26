"""
Agent 1: Skill Assessment Agent
Analyzes student quiz & test performances across subjects (DSA, DBMS, OS, CN, OOP, Aptitude, Behavioral),
calculates topic-wise proficiency, detects weak/strong areas, and continuously updates the student's skill profile.
"""
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.llm_service import llm_service
from backend.database.db import get_db

class SkillAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SkillAssessmentAgent",
            description="Evaluates student quiz performances, assesses subject/topic mastery, and detects weak/strong competencies."
        )

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
            user_id: int
            quiz_results: List[Dict] with keys (question_id, topic_id, is_correct, difficulty)
            subject_id: int (optional)
        Output:
            updated_topics: List[Dict] (topic_id, name, new_score, status, change)
            weak_topics: List[Dict]
            strong_topics: List[Dict]
            assessment_summary: str
        """
        user_id = input_data.get("user_id")
        quiz_results = input_data.get("quiz_results", [])
        
        if not user_id or not quiz_results:
            return {"status": "no_data", "message": "No quiz results or user_id provided."}

        # 1. Group quiz results by topic
        topic_stats = {}
        with get_db() as conn:
            cursor = conn.cursor()
            for item in quiz_results:
                q_id = item.get("question_id")
                is_correct = bool(item.get("is_correct"))
                
                # Fetch topic details from DB
                cursor.execute("""
                    SELECT q.topic_id, t.name as topic_name, t.subject_id, s.name as subject_name, q.difficulty
                    FROM questions q
                    JOIN topics t ON q.topic_id = t.id
                    JOIN subjects s ON t.subject_id = s.id
                    WHERE q.id = ?
                """, (q_id,))
                row = cursor.fetchone()
                if not row:
                    continue
                
                tid = row["topic_id"]
                if tid not in topic_stats:
                    topic_stats[tid] = {
                        "topic_id": tid,
                        "topic_name": row["topic_name"],
                        "subject_id": row["subject_id"],
                        "subject_name": row["subject_name"],
                        "total": 0,
                        "correct": 0,
                        "weighted_score": 0.0
                    }
                
                weight = 1.0 if row["difficulty"] == "Easy" else (1.5 if row["difficulty"] == "Medium" else 2.0)
                topic_stats[tid]["total"] += 1
                if is_correct:
                    topic_stats[tid]["correct"] += 1
                    topic_stats[tid]["weighted_score"] += weight

            # 2. Re-calculate and update skill profile for each affected topic
            updated_profiles = []
            weak_topics = []
            strong_topics = []

            for tid, stats in topic_stats.items():
                # Fetch existing skill profile
                cursor.execute("""
                    SELECT proficiency_score, quizzes_taken, confidence_level
                    FROM skill_profiles
                    WHERE user_id = ? AND topic_id = ?
                """, (user_id, tid))
                existing = cursor.fetchone()

                current_quiz_pct = (stats["correct"] / stats["total"]) * 100.0 if stats["total"] > 0 else 0.0
                
                if existing:
                    old_score = existing["proficiency_score"]
                    quizzes_count = existing["quizzes_taken"] + 1
                    # Exponential moving average / Bayesian updating
                    learning_rate = max(0.2, 1.0 / (quizzes_count + 1))
                    new_score = round(old_score * (1 - learning_rate) + current_quiz_pct * learning_rate, 1)
                    new_conf = min(0.95, existing["confidence_level"] + 0.1)
                else:
                    old_score = 50.0
                    quizzes_count = 1
                    new_score = round(current_quiz_pct, 1)
                    new_conf = 0.6

                # Classification
                if new_score < 50.0:
                    status = "Weak"
                elif new_score >= 75.0:
                    status = "Strong"
                else:
                    status = "Moderate"

                # Update or Insert
                cursor.execute("""
                    INSERT INTO skill_profiles (user_id, subject_id, topic_id, proficiency_score, status, confidence_level, quizzes_taken, last_evaluated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id, topic_id) DO UPDATE SET
                        proficiency_score = excluded.proficiency_score,
                        status = excluded.status,
                        confidence_level = excluded.confidence_level,
                        quizzes_taken = excluded.quizzes_taken,
                        last_evaluated_at = CURRENT_TIMESTAMP
                """, (user_id, stats["subject_id"], tid, new_score, status, new_conf, quizzes_count))

                topic_info = {
                    "topic_id": tid,
                    "topic_name": stats["topic_name"],
                    "subject_name": stats["subject_name"],
                    "old_score": old_score,
                    "new_score": new_score,
                    "status": status,
                    "accuracy": f"{stats['correct']}/{stats['total']}"
                }
                updated_profiles.append(topic_info)

                if status == "Weak":
                    weak_topics.append(topic_info)
                elif status == "Strong":
                    strong_topics.append(topic_info)

        # 3. Generate summary using LLM or intelligent synthesis
        weak_names = [w["topic_name"] for w in weak_topics]
        strong_names = [s["topic_name"] for s in strong_topics]

        system_prompt = "You are an expert AI Assessment Agent evaluating student technical test results."
        prompt = f"""
        User ID: {user_id}
        Updated Topics: {updated_profiles}
        Weak Topics: {weak_names}
        Strong Topics: {strong_names}
        Generate an assessment diagnostic summary and learning recommendations.
        """
        fallback_summary = {
            "assessment_summary": f"Assessment completed: Identified {len(weak_topics)} weak topics ({', '.join(weak_names) if weak_names else 'None'}) and {len(strong_topics)} strong topics ({', '.join(strong_names) if strong_names else 'None'}). Recommended targeted revision.",
            "action_priority": "High" if len(weak_topics) > 0 else "Normal",
            "recommended_focus": weak_names[0] if weak_names else "Maintain consistency across moderate topics"
        }

        ai_analysis = llm_service.generate_json(prompt, system_prompt, fallback_summary)

        return {
            "user_id": user_id,
            "updated_topics": updated_profiles,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "analysis": ai_analysis
        }
