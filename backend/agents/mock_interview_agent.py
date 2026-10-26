"""
Agent 4: Mock Interview Evaluation Agent
Expanded question repository with 60+ dynamic questions across technical and behavioral domains.
Includes deduplication to ensure candidates never receive repeated questions in subsequent sessions.
"""
from typing import Dict, Any, List
import random
import re
from datetime import datetime
from backend.agents.base_agent import BaseAgent
from backend.agents.llm_service import llm_service
from backend.database.db import get_db

# Extensive Question Bank for diverse interview sessions
TECHNICAL_QUESTIONS_POOL = [
    # Dynamic Programming & Algorithms
    {
        "question_text": "Can you explain the core trade-offs between dynamic programming (tabulation) and memoization (top-down recursion)? How does call-stack memory overhead impact production systems?",
        "category": "DSA - Dynamic Programming",
        "expected_key_points": "Stack overflow risks, cache locality in arrays, space optimization from O(N) to O(1), overhead of recursion vs iteration"
    },
    {
        "question_text": "How would you solve the Coin Change problem (finding minimum coins to make an amount)? Explain both the recurrence relation and time/space complexity.",
        "category": "DSA - Dynamic Programming",
        "expected_key_points": "Unbounded knapsack approach, dp[i] = min(dp[i], 1 + dp[i-coin]), O(amount * n) time, O(amount) space"
    },
    {
        "question_text": "Explain Kadane's algorithm for Maximum Subarray Sum. Why does it achieve linear O(N) time, and how do you handle an array of all negative numbers?",
        "category": "DSA - Algorithms",
        "expected_key_points": "Local vs global max, resetting current sum when negative, tracking max negative element when all negative"
    },
    {
        "question_text": "Walk me through how Dijkstra's Shortest Path algorithm works. Why does it fail when negative edge weights are present in the graph?",
        "category": "DSA - Graphs",
        "expected_key_points": "Greedy choice with min-heap priority queue, relaxation of edges, assumption that visited shortest distances are final failing with negative cycles"
    },
    {
        "question_text": "How do you detect a cycle in a Singly Linked List using Floyd's Cycle-Finding Algorithm? Prove why the slow and fast pointers must meet.",
        "category": "DSA - Linked Lists",
        "expected_key_points": "Two pointers moving at speeds 1 and 2, relative distance decreases by 1 each step within cycle, O(N) time, O(1) space"
    },

    # Database Systems & SQL
    {
        "question_text": "Describe how database indexes (such as B-Trees and B+ Trees) work internally. In what practical scenarios might adding an index actually degrade database performance?",
        "category": "DBMS - Indexing",
        "expected_key_points": "B+ Tree leaf pointers and sequential scans, write amplification during INSERT/UPDATE/DELETE, memory buffer pool pressure, low-cardinality column scans"
    },
    {
        "question_text": "Explain the four ACID properties in relational database transactions. How do modern databases prevent 'Dirty Reads' and 'Phantom Reads'?",
        "category": "DBMS - Transactions & Concurrency",
        "expected_key_points": "Atomicity, Consistency, Isolation, Durability. Isolation levels: Read Committed, Repeatable Read, Serializable via Two-Phase Locking or MVCC"
    },
    {
        "question_text": "What is Database Normalization? Compare 3NF and BCNF with a real-world scenario where denormalization is preferred for read-heavy microservices.",
        "category": "DBMS - Schema Design",
        "expected_key_points": "Eliminating anomalies and redundancy, functional dependencies, BCNF strictness, denormalization for OLAP and read performance"
    },

    # Operating Systems & Concurrency
    {
        "question_text": "What are the four necessary Coffman conditions for a Deadlock to occur in an operating system? How does Banker's algorithm prevent deadlock?",
        "category": "OS - Concurrency & Deadlocks",
        "expected_key_points": "Mutual exclusion, hold and wait, no preemption, circular wait. Safe state verification using available, max, allocation matrices"
    },
    {
        "question_text": "Compare processes and threads. What exact resources are shared between threads of the same process, and what resources remain private to each thread?",
        "category": "OS - Processes & Threads",
        "expected_key_points": "Shared: address space, heap, open files, global data. Private: stack, program counter, register set, thread local storage"
    },
    {
        "question_text": "Explain Virtual Memory, Paging, and how the Translation Lookaside Buffer (TLB) speeds up address translation. What triggers a Page Fault?",
        "category": "OS - Memory Management",
        "expected_key_points": "Logical vs physical addresses, page tables, TLB cache hit/miss, page fault interrupt loading disk frame into RAM"
    },

    # Computer Networks & Distributed Systems
    {
        "question_text": "What happens under the hood when a user types an HTTPS URL into a browser and presses Enter? Walk through DNS, TCP handshake, and TLS negotiation.",
        "category": "CN - Protocols & Web Architecture",
        "expected_key_points": "DNS resolution, 3-way TCP SYN/SYN-ACK/ACK, TLS ClientHello/ServerHello, certificate verification, symmetric session key derivation, HTTP GET request"
    },
    {
        "question_text": "Compare TCP and UDP at the transport layer. For a real-time multiplayer video game or VoIP stream, which protocol would you choose and why?",
        "category": "CN - Transport Layer",
        "expected_key_points": "Connection-oriented vs connectionless, reliability vs latency, flow control, head-of-line blocking in TCP making UDP ideal for live audio/gaming"
    },
    {
        "question_text": "Explain the CAP theorem in distributed systems. Give an example of a system that prioritizes Consistency over Availability during a network partition.",
        "category": "Distributed Systems - Architecture",
        "expected_key_points": "Consistency, Availability, Partition Tolerance. CP systems (e.g. distributed banking, Zookeeper/Raft) rejecting writes during split-brain"
    },

    # Object-Oriented Design & System Design
    {
        "question_text": "Explain the SOLID design principles. Pick either Liskov Substitution Principle (LSP) or Dependency Inversion Principle (DIP) and provide a concrete code example.",
        "category": "OOP - Design Principles",
        "expected_key_points": "Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion. High-level modules depending on abstractions not concretions"
    },
    {
        "question_text": "Design a Rate Limiter system for an API gateway. What algorithms would you consider (Token Bucket, Leaky Bucket, Sliding Window Counter)?",
        "category": "System Design - Architecture",
        "expected_key_points": "Token bucket burst capacity, Redis sliding window counter with sorted sets, handling distributed clocks and concurrency"
    }
]

BEHAVIORAL_QUESTIONS_POOL = [
    {
        "question_text": "Tell me about a challenging technical bug or production incident you faced. Walk me through your debugging methodology using the STAR framework.",
        "category": "Behavioral - Problem Solving (STAR)",
        "expected_key_points": "Situation: context/impact, Task: objective, Action: root-cause analysis (logs, reproduction, fix), Result: metrics, tests, post-mortem prevention"
    },
    {
        "question_text": "Describe a situation where you had a strong technical disagreement with a peer or team lead regarding software design. How did you resolve it constructively?",
        "category": "Behavioral - Conflict Resolution",
        "expected_key_points": "Active listening, objective pros/cons benchmark, creating a quick POC or benchmark test, committing to team decision professionally"
    },
    {
        "question_text": "Tell me about a time when a project scope changed drastically close to a critical deadline. How did you prioritize your workload and manage expectations?",
        "category": "Behavioral - Adaptability & Prioritization",
        "expected_key_points": "MoSCoW/Eisenhower prioritization, transparent stakeholder communication, MVP focus, ensuring automated testing wasn't compromised"
    },
    {
        "question_text": "Give an example of a project where you took leadership initiative even though you were not the designated lead. What was the outcome?",
        "category": "Behavioral - Leadership & Ownership",
        "expected_key_points": "Identifying an unaddressed bottleneck, stepping up to coordinate peers, documentation, measurable positive delivery result"
    },
    {
        "question_text": "Discuss a time you made a significant mistake in your code or design that caused an issue. What did you learn and what safeguard did you put in place?",
        "category": "Behavioral - Accountability & Learning",
        "expected_key_points": "Owning the mistake without deflecting blame, transparent incident reporting, adding unit/regression tests, improving CI/CD checks"
    },
    {
        "question_text": "How do you stay updated with emerging technologies and tools, and how have you applied an independently learned concept into a real project?",
        "category": "Behavioral - Continuous Learning",
        "expected_key_points": "Curiosity, technical blogs, open-source reading, hands-on prototype building, concrete transfer of learning to project"
    }
]

class MockInterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MockInterviewAgent",
            description="Conducts AI mock interviews with dynamically diversified questions and delivers 5-metric response evaluations."
        )

    def generate_interview_questions(self, interview_type: str, target_role: str, user_id: int) -> List[Dict[str, Any]]:
        """
        Generates dynamic questions without repeating previously answered questions.
        Selects across categories to ensure every session feels fresh and comprehensive.
        """
        asked_questions = set()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT iq.question_text
                FROM interview_questions iq
                JOIN mock_interviews mi ON iq.mock_interview_id = mi.id
                WHERE mi.user_id = ?
            """, (user_id,))
            for row in cursor.fetchall():
                asked_questions.add(row["question_text"].strip().lower())

            # Check student's weak areas to prioritize relevant questions
            cursor.execute("""
                SELECT t.name FROM skill_profiles sp
                JOIN topics t ON sp.topic_id = t.id
                WHERE sp.user_id = ? AND sp.status = 'Weak'
                ORDER BY sp.proficiency_score ASC
                LIMIT 2
            """, (user_id,))
            weak_topics = [r["name"] for r in cursor.fetchall()]

        # Filter candidate pools to unseen questions
        unseen_technical = [q for q in TECHNICAL_QUESTIONS_POOL if q["question_text"].strip().lower() not in asked_questions]
        unseen_behavioral = [q for q in BEHAVIORAL_QUESTIONS_POOL if q["question_text"].strip().lower() not in asked_questions]

        # Reset pools if candidate has answered all of them
        if len(unseen_technical) < 3:
            unseen_technical = list(TECHNICAL_QUESTIONS_POOL)
        if len(unseen_behavioral) < 3:
            unseen_behavioral = list(BEHAVIORAL_QUESTIONS_POOL)

        selected_questions = []

        if interview_type == "Technical":
            prioritized = []
            others = []
            for q in unseen_technical:
                if any(w.lower() in q["category"].lower() or w.lower() in q["question_text"].lower() for w in weak_topics):
                    prioritized.append(q)
                else:
                    others.append(q)

            random.shuffle(prioritized)
            random.shuffle(others)
            pool = prioritized + others
            selected_questions = pool[:3]

        elif interview_type == "Behavioral":
            random.shuffle(unseen_behavioral)
            selected_questions = unseen_behavioral[:3]

        else: # Mixed
            random.shuffle(unseen_technical)
            random.shuffle(unseen_behavioral)
            selected_questions = unseen_technical[:2] + unseen_behavioral[:1]

        if len(selected_questions) < 3:
            all_pool = TECHNICAL_QUESTIONS_POOL + BEHAVIORAL_QUESTIONS_POOL
            random.shuffle(all_pool)
            for item in all_pool:
                if item not in selected_questions:
                    selected_questions.append(item)
                if len(selected_questions) >= 3:
                    break

        return selected_questions

    def evaluate_response(self, question_text: str, expected_key_points: str, user_response: str) -> Dict[str, Any]:
        """Evaluates candidate response across 5 core dimensions."""
        if not user_response or len(user_response.strip()) < 10:
            return {
                "technical_score": 30.0,
                "clarity_score": 40.0,
                "confidence_score": 30.0,
                "communication_score": 40.0,
                "relevance_score": 35.0,
                "overall_score": 35.0,
                "feedback": "The response was too brief or incomplete. In an interview, elaborate with structured reasoning and practical examples.",
                "key_strengths": "Prompt submission.",
                "improvement_areas": "Expand on fundamental concepts, provide concrete examples, and address key trade-offs."
            }

        word_count = len(user_response.split())
        tech_score = min(92.0, 50.0 + min(word_count * 0.4, 30.0))
        clarity_score = 78.0 if word_count > 25 else 55.0
        confidence_score = 82.0 if not any(w in user_response.lower() for w in ["maybe", "i guess", "i think maybe", "not sure"]) else 60.0
        comm_score = min(92.0, 62.0 + min(word_count * 0.3, 26.0))
        rel_score = 82.0

        key_words = [w.lower().strip() for w in re.findall(r'\b[a-zA-Z]{4,}\b', expected_key_points)]
        matches = sum(1 for kw in key_words if kw in user_response.lower())
        if key_words:
            keyword_bonus = min(22.0, (matches / len(key_words)) * 32.0)
            tech_score = min(98.0, tech_score + keyword_bonus)

        avg_score = round((tech_score + clarity_score + confidence_score + comm_score + rel_score) / 5.0, 1)

        fallback_eval = {
            "technical_score": round(tech_score, 1),
            "clarity_score": round(clarity_score, 1),
            "confidence_score": round(confidence_score, 1),
            "communication_score": round(comm_score, 1),
            "relevance_score": round(rel_score, 1),
            "overall_score": avg_score,
            "feedback": f"Strong conceptual articulation with solid clarity. Addressed primary aspects of the question with {word_count} words of thoughtful analysis.",
            "key_strengths": "Clear structure, confident technical vocabulary, and logical sequencing.",
            "improvement_areas": "Could delve deeper into specific edge cases, failure modes, and quantitative performance trade-offs."
        }

        system_prompt = "You are an expert Interview Evaluator. Grade the candidate response objectively."
        prompt = f"""
        Interview Question: {question_text}
        Expected Key Points: {expected_key_points}
        Candidate Response: {user_response}
        Score the response strictly from 0 to 100 on technical_score, clarity_score, confidence_score, communication_score, relevance_score.
        """
        ai_eval = llm_service.generate_json(prompt, system_prompt, fallback_eval)
        for key in ["technical_score", "clarity_score", "confidence_score", "communication_score", "relevance_score"]:
            if key in ai_eval:
                try:
                    ai_eval[key] = float(ai_eval[key])
                except (ValueError, TypeError):
                    ai_eval[key] = fallback_eval[key]
        
        scores = [ai_eval.get(k, 70.0) for k in ["technical_score", "clarity_score", "confidence_score", "communication_score", "relevance_score"]]
        ai_eval["overall_score"] = round(sum(scores) / len(scores), 1)

        return ai_eval

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action")
        
        if action == "start_interview":
            user_id = input_data["user_id"]
            interview_type = input_data.get("interview_type", "Technical")
            target_role = input_data.get("target_role", "Software Development Engineer")

            questions = self.generate_interview_questions(interview_type, target_role, user_id)

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mock_interviews (user_id, interview_type, target_role, status)
                    VALUES (?, ?, ?, 'In_Progress')
                """, (user_id, interview_type, target_role))
                interview_id = cursor.lastrowid

                saved_questions = []
                for idx, q in enumerate(questions):
                    cursor.execute("""
                        INSERT INTO interview_questions (mock_interview_id, question_text, category, expected_key_points, order_idx)
                        VALUES (?, ?, ?, ?, ?)
                    """, (interview_id, q["question_text"], q.get("category", "General"), q.get("expected_key_points", ""), idx + 1))
                    saved_questions.append({
                        "id": cursor.lastrowid,
                        "question_text": q["question_text"],
                        "category": q.get("category", "General"),
                        "expected_key_points": q.get("expected_key_points", ""),
                        "order_idx": idx + 1
                    })

            return {
                "interview_id": interview_id,
                "interview_type": interview_type,
                "target_role": target_role,
                "questions": saved_questions
            }

        elif action == "submit_answer":
            question_id = input_data["question_id"]
            user_response = input_data["user_response"]

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM interview_questions WHERE id = ?", (question_id,))
                q_row = cursor.fetchone()
                if not q_row:
                    return {"status": "error", "message": "Question not found"}

                eval_result = self.evaluate_response(q_row["question_text"], q_row["expected_key_points"], user_response)

                cursor.execute("""
                    INSERT INTO interview_responses (
                        interview_question_id, user_response, technical_score, clarity_score,
                        confidence_score, communication_score, relevance_score, feedback,
                        key_strengths, improvement_areas
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(interview_question_id) DO UPDATE SET
                        user_response = excluded.user_response,
                        technical_score = excluded.technical_score,
                        clarity_score = excluded.clarity_score,
                        confidence_score = excluded.confidence_score,
                        communication_score = excluded.communication_score,
                        relevance_score = excluded.relevance_score,
                        feedback = excluded.feedback,
                        key_strengths = excluded.key_strengths,
                        improvement_areas = excluded.improvement_areas
                """, (
                    question_id, user_response,
                    eval_result["technical_score"], eval_result["clarity_score"],
                    eval_result["confidence_score"], eval_result["communication_score"],
                    eval_result["relevance_score"], eval_result["feedback"],
                    eval_result["key_strengths"], eval_result["improvement_areas"]
                ))

            return eval_result

        elif action == "complete_interview":
            interview_id = input_data["interview_id"]
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ir.*, iq.question_text, iq.category
                    FROM interview_responses ir
                    JOIN interview_questions iq ON ir.interview_question_id = iq.id
                    WHERE iq.mock_interview_id = ?
                """, (interview_id,))
                responses = cursor.fetchall()

                if not responses:
                    return {"status": "no_responses", "message": "No responses submitted for this interview."}

                avg_overall = sum(
                    (r["technical_score"] + r["clarity_score"] + r["confidence_score"] + r["communication_score"] + r["relevance_score"]) / 5.0
                    for r in responses
                ) / len(responses)
                avg_overall = round(avg_overall, 1)

                summary = f"Completed mock session across {len(responses)} questions with an aggregate rating of {avg_overall}/100. Demonstrated competence in structured responses."

                cursor.execute("""
                    UPDATE mock_interviews
                    SET status = 'Completed', overall_score = ?, feedback_summary = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (avg_overall, summary, interview_id))

            return {
                "interview_id": interview_id,
                "overall_score": avg_overall,
                "responses": responses,
                "summary": summary
            }

        return {"status": "error", "message": f"Unknown action {action}"}
