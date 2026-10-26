"""
Verification test suite for multi-agent pipeline and database integrity.
"""
import sys
from backend.database.db import init_db, get_db
from backend.database.seed_data import seed
from backend.agents.orchestrator import orchestrator

def run_pipeline_test():
    print("=== 1. Testing DB and Seed Initialization ===")
    init_db()
    seed()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()["count"]
        cursor.execute("SELECT COUNT(*) as count FROM subjects")
        subj_count = cursor.fetchone()["count"]
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        q_count = cursor.fetchone()["count"]
        cursor.execute("SELECT COUNT(*) as count FROM coding_problems")
        prob_count = cursor.fetchone()["count"]
        cursor.execute("SELECT id FROM users WHERE email = 'demo@example.com'")
        demo_user = cursor.fetchone()
        user_id = demo_user["id"]
        
    print(f"Verified DB: {user_count} users, {subj_count} subjects, {q_count} questions, {prob_count} problems.")
    assert user_count > 0, "No users found"
    assert q_count > 0, "No questions found"

    print("\n=== 2. Testing Skill Assessment & Multi-Agent Cascade ===")
    # Simulate submitting a quiz where the student misses Dynamic Programming questions
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.id, q.topic_id, q.correct_answer, t.name as topic_name
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            WHERE t.name = 'Dynamic Programming'
            LIMIT 2
        """)
        dp_questions = cursor.fetchall()
        
    quiz_results = []
    for q in dp_questions:
        # Intentionally wrong answer
        wrong_opt = (q["correct_answer"] + 1) % 4
        quiz_results.append({
            "question_id": q["id"],
            "topic_id": q["topic_id"],
            "is_correct": False,
            "difficulty": "Medium"
        })

    cascade_result = orchestrator.on_quiz_completed(user_id, quiz_results)
    print("Orchestrator Cascade Pipeline Execution Time:", cascade_result["pipeline_time_ms"], "ms")
    print("Skill assessment updated topics:", [t["topic_name"] for t in cascade_result["skill_assessment"]["updated_topics"]])
    print("Coding recommendations count:", len(cascade_result["coding_recommendations"]["recommended_problems"]))
    print("Recalculated Readiness Score:", cascade_result["progress_monitoring"]["overall_readiness_score"])

    print("\n=== 3. Testing Mock Interview Agent ===")
    start_interview = orchestrator.interview_agent.execute({
        "action": "start_interview",
        "user_id": user_id,
        "interview_type": "Technical",
        "target_role": "Software Development Engineer (SDE)"
    })
    interview_id = start_interview["interview_id"]
    q1 = start_interview["questions"][0]
    print(f"Mock Interview started (ID: {interview_id}). First question: {q1['question_text'][:60]}...")

    eval_resp = orchestrator.interview_agent.execute({
        "action": "submit_answer",
        "question_id": q1["id"],
        "user_response": "Dynamic programming works by storing intermediate solutions so we avoid redundant exponential re-computation. Recursion with memoization uses top-down stack space, while tabulation builds bottom-up in an array, allowing space optimization."
    })
    print(f"Evaluated candidate response. Overall Score: {eval_resp['overall_score']}, Technical: {eval_resp['technical_score']}")
    assert eval_resp["overall_score"] > 50, "Evaluation failed to grade meaningful answer"

    complete_res = orchestrator.on_interview_completed(user_id, interview_id)
    print("Completed interview rating:", complete_res["interview_summary"]["overall_score"])

    print("\n=== 4. Testing Resume Analysis Agent ===")
    resume_res = orchestrator.on_resume_uploaded(
        user_id=user_id,
        resume_text="Senior CS student with proficiency in Python, Java, SQL, React, FastAPI, Git, Algorithms, and Distributed Systems. Built collaborative applications and automated testing frameworks.",
        target_role="Software Development Engineer (SDE)",
        filename="Test_Resume.txt"
    )
    print(f"Resume Overall Score: {resume_res['resume_analysis']['overall_score']}")
    print(f"Matched Keywords: {len(resume_res['resume_analysis']['matched_keywords'])}, Missing: {len(resume_res['resume_analysis']['missing_keywords'])}")

    print("\n=== 5. Testing Research & Performance Metrics ===")
    metrics_data = orchestrator.get_system_performance_metrics(user_id)
    print(f"Total metrics reported: {len(metrics_data['metrics'])}")
    for m in metrics_data["metrics"]:
        print(f" - {m['name']}: {m['value']} ({m['status']})")

    print("\n>>> ALL MULTI-AGENT ARCHITECTURE AND DATABASE TESTS PASSED! <<<")

if __name__ == "__main__":
    run_pipeline_test()
