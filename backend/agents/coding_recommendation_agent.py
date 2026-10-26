"""
Agent 3: Coding Recommendation Agent
Recommends coding problems matching student proficiency, prioritizing identified weak areas,
adapting difficulty based on submission history, avoiding already solved problems, and
supplying explainable reasoning with curated learning resources.
"""
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.llm_service import llm_service
from backend.database.db import get_db

class CodingRecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CodingRecommendationAgent",
            description="Recommends coding challenges tailored to weak areas, adapting difficulty and offering contextual learning resources."
        )

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
            user_id: int
            limit: int (default: 5)
        Output:
            recommended_problems: List[Dict]
            learning_resources: List[Dict]
            explanation: str
        """
        user_id = input_data.get("user_id")
        limit = input_data.get("limit", 5)
        if not user_id:
            return {"status": "error", "message": "user_id is required"}

        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Fetch already accepted problem IDs to avoid recommending completed problems
            cursor.execute("""
                SELECT DISTINCT problem_id
                FROM coding_submissions
                WHERE user_id = ? AND status = 'Accepted'
            """, (user_id,))
            solved_ids = {row["problem_id"] for row in cursor.fetchall()}

            # 2. Fetch skill profiles to find weak and moderate topics
            cursor.execute("""
                SELECT sp.topic_id, sp.proficiency_score, sp.status, t.name as topic_name
                FROM skill_profiles sp
                JOIN topics t ON sp.topic_id = t.id
                WHERE sp.user_id = ?
                ORDER BY sp.proficiency_score ASC
            """, (user_id,))
            skills = cursor.fetchall()

            # If student has weak topics, prioritize those
            weak_topic_ids = [s["topic_id"] for s in skills if s["status"] == "Weak"]
            moderate_topic_ids = [s["topic_id"] for s in skills if s["status"] == "Moderate"]
            
            # Map topic_id to topic_name and proficiency score
            topic_lookup = {s["topic_id"]: s for s in skills}

            # 3. Retrieve eligible coding problems
            cursor.execute("""
                SELECT cp.*, t.name as topic_name, s.name as subject_name
                FROM coding_problems cp
                JOIN topics t ON cp.topic_id = t.id
                JOIN subjects s ON t.subject_id = s.id
            """)
            all_problems = cursor.fetchall()

            # Filter out solved problems
            unsolved = [p for p in all_problems if p["id"] not in solved_ids]

            # 4. Score and rank problems based on student's weaknesses & difficulty progression
            def score_problem(p):
                tid = p["topic_id"]
                t_info = topic_lookup.get(tid)
                topic_score = t_info["proficiency_score"] if t_info else 50.0

                rank = 0
                # Weak topic priority
                if tid in weak_topic_ids:
                    rank += 100
                    # For weak topics, prefer Easy or Medium to build confidence
                    if p["difficulty"] == "Easy":
                        rank += 30
                    elif p["difficulty"] == "Medium":
                        rank += 20
                    else:
                        rank += 5
                elif tid in moderate_topic_ids:
                    rank += 50
                    if p["difficulty"] == "Medium":
                        rank += 30
                    elif p["difficulty"] == "Hard":
                        rank += 20
                    else:
                        rank += 10
                else:
                    # Strong topics: challenge with Hard/Medium
                    rank += 10
                    if p["difficulty"] == "Hard":
                        rank += 30
                    elif p["difficulty"] == "Medium":
                        rank += 20
                    else:
                        rank += 5

                # Inverse of acceptance rate can favor well-rounded problems
                rank += (100 - (topic_score if topic_score is not None else 50)) * 0.5
                return rank

            ranked = sorted(unsolved, key=score_problem, reverse=True)
            top_recommendations = ranked[:limit]

            # Build explainable reasoning for each recommendation
            annotated_recs = []
            for p in top_recommendations:
                tid = p["topic_id"]
                t_info = topic_lookup.get(tid)
                if t_info and t_info["status"] == "Weak":
                    reason = f"Recommended because your proficiency in {p['topic_name']} is {t_info['proficiency_score']}%. Starting with {p['difficulty']} difficulty helps build foundational intuition."
                elif t_info and t_info["status"] == "Moderate":
                    reason = f"Recommended to advance your {p['topic_name']} mastery from moderate ({t_info['proficiency_score']}%) to interview-ready."
                else:
                    reason = f"Curated high-frequency interview question in {p['topic_name']} with {p['acceptance_rate']}% platform acceptance rate."

                annotated_recs.append({
                    "id": p["id"],
                    "title": p["title"],
                    "slug": p["slug"],
                    "difficulty": p["difficulty"],
                    "topic_name": p["topic_name"],
                    "subject_name": p["subject_name"],
                    "acceptance_rate": p["acceptance_rate"],
                    "description": p["description"],
                    "starter_code": p["starter_code"],
                    "solution_notes": p["solution_notes"],
                    "recommendation_reason": reason
                })

            # Save top recommendation to agent_recommendations table
            if annotated_recs:
                import json
                cursor.execute("""
                    INSERT INTO agent_recommendations (user_id, agent_name, recommendation_type, content_json, reasoning)
                    VALUES (?, 'CodingRecommendationAgent', 'ProblemSet', ?, ?)
                """, (user_id, json.dumps([r["id"] for r in annotated_recs]), annotated_recs[0]["recommendation_reason"]))

            # 5. Provide relevant learning resources
            learning_resources = [
                {
                    "title": "NeetCode Dynamic Programming Roadmap",
                    "type": "Video / Visual Roadmap",
                    "url": "https://neetcode.io/roadmap",
                    "relevant_topic": "Dynamic Programming",
                    "description": "Step-by-step breakdown from 1D DP to 2D Knapsack and LIS patterns."
                },
                {
                    "title": "Visualizing Algorithms: Two Pointers & Sliding Window",
                    "type": "Interactive Guide",
                    "url": "https://visualgo.net",
                    "relevant_topic": "Arrays & Strings",
                    "description": "Visual intuition for window shrinkage and pointer movements."
                },
                {
                    "title": "Database Normalization & Indexing Cheat Sheet",
                    "type": "Article & Reference",
                    "url": "https://use-the-index-luke.com",
                    "relevant_topic": "SQL Queries & Joins",
                    "description": "Deep dive into B-Tree indexing, table scans, and execution plans."
                }
            ]

        return {
            "recommended_problems": annotated_recs,
            "solved_count": len(solved_ids),
            "unsolved_pool_size": len(unsolved),
            "learning_resources": learning_resources,
            "strategy": "Weak-area prioritized difficulty scaling"
        }
