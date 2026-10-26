# Agentic AI Interview Preparation Tracker

An intelligent, multi-agent platform that continuously evaluates a student's technical and behavioral interview readiness, identifies weak areas, creates personalized adaptive study plans, recommends targeted coding problems, conducts conversational mock interviews, analyzes resumes for ATS compatibility, and calculates a dynamic Placement Readiness Score.

---

## 🌟 Core AI Multi-Agent Architecture

The platform is powered by **six specialized autonomous AI agents** orchestrated through a real-time reactive event loop:

```
                                    ┌──────────────────────────────────────┐
                                    │         Student Activities           │
                                    │ (Quizzes, Code, Interviews, Resumes) │
                                    └──────────────────┬───────────────────┘
                                                       │
                                    ┌──────────────────▼───────────────────┐
                                    │       Multi-Agent Orchestrator       │
                                    └──────┬──────┬──────┬──────┬──────┬───┘
                                           │      │      │      │      │
            ┌──────────────────────────────┼──────┼──────┼──────┼──────┼──────────────────────────────┐
            ▼                              ▼      ▼      ▼      ▼      ▼                              ▼
 ┌──────────────────────┐        ┌───────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐        ┌──────────────────────┐
 │ Agent 1: Skill       │        │ Agent 2:  │ │ Agent 3: │ │ Agent 4:│ │ Agent 5:│        │ Agent 6: Progress    │
 │ Assessment Agent     │───────►│ Study     │►│ Coding   │►│ Mock    │►│ Resume  │───────►│ Monitoring Agent     │
 │ (Diagnostic Quizzes) │        │ Planning  │ │ Recomm.  │ │Interv.  │ │ Analysis│        │ (Readiness Score)    │
 └──────────────────────┘        └───────────┘ └──────────┘ └─────────┘ └─────────┘        └──────────────────────┘
            │                          │            │            │           │                            │
            └──────────────────────────┴────────────┴─────┬──────┴───────────┴────────────────────────────┘
                                                          │
                                           ┌──────────────▼──────────────┐
                                           │     SQLite Relational DB    │
                                           │    (18 Tables & Triggers)   │
                                           └─────────────────────────────┘
```

### The Six Specialized Agents:

1. **Skill Assessment Agent (`SkillAssessmentAgent`)**
   - **Role**: Analyzes quiz and diagnostic test performance across 7 disciplines: DSA, DBMS, OS, Computer Networks, OOP, Aptitude, and Behavioral.
   - **Intelligence**: Evaluates topic-level proficiency ($0-100\%$) and categorizes mastery into `Weak` ($<50\%$), `Moderate` ($50-74\%$), or `Strong` ($\ge 75\%$) with Bayesian confidence scaling.

2. **Study Planning Agent (`StudyPlanningAgent`)**
   - **Role**: Synthesizes skill profiles, weak areas, target company/role, and available study hours into an adaptive schedule.
   - **Adaptive Loop**: Whenever diagnostic or coding performance signals a dip in a topic, this agent automatically restructures upcoming tasks, assigning higher priority drills to weak areas.

3. **Coding Recommendation Agent (`CodingRecommendationAgent`)**
   - **Role**: Recommends coding challenges matching the student's current proficiency level while avoiding already-completed challenges.
   - **Explainability**: Annotates every problem with clear rationale (e.g., *"Recommended because your Dynamic Programming proficiency is 35%. Starting with Easy difficulty helps build foundational intuition."*).

4. **Mock Interview Evaluation Agent (`MockInterviewAgent`)**
   - **Role**: Generates dynamic technical and behavioral interview questions tailored to target roles and weak topics.
   - **Evaluation**: Conducts turn-based conversational simulations, scoring candidate answers across 5 dimensions: **Technical Correctness**, **Clarity**, **Confidence**, **Communication**, and **Relevance**.

5. **Resume Analysis Agent (`ResumeAnalysisAgent`)**
   - **Role**: Audits uploaded or pasted resumes against role-specific technical benchmarks.
   - **Outputs**: Calculates an ATS compatibility score ($0-100\%$), identifies matched vs. missing keywords, isolates experience gaps, and generates high-impact bullet suggestions.

6. **Progress Monitoring Agent (`ProgressMonitoringAgent`)**
   - **Role**: The central cognitive aggregator that computes the composite **Placement Readiness Score (0-100%)**:
     $$\text{Readiness} = 0.35 \times \text{SkillProficiency} + 0.25 \times \text{CodingProgress} + 0.20 \times \text{InterviewAvg} + 0.10 \times \text{ResumeScore} + 0.10 \times \text{PlanAdherence}$$
   - **Outputs**: Tracks historical progress trends and generates prioritized next-best actions.

---

## 🗄️ Relational Database Schema (18 Tables)

Built with SQLite relational integrity, foreign key constraints, and performance indexes:

| # | Table | Purpose |
|---|-------|---------|
| 1 | `users` | User accounts, roles, credentials |
| 2 | `user_profiles` | Student goals, target role, company, target interview date, daily hours |
| 3 | `subjects` | 7 core disciplines (DSA, DBMS, OS, CN, OOP, Aptitude, Behavioral) |
| 4 | `topics` | Fine-grained subject topics with difficulty weights |
| 5 | `questions` | Diagnostic quiz questions with multiple choices and explanations |
| 6 | `quiz_attempts` | Historical quiz submission records and scores |
| 7 | `skill_profiles` | Evolving topic proficiency scores, status (`Weak`/`Moderate`/`Strong`), confidence levels |
| 8 | `study_plans` | Active preparation schedules generated by Agent 2 |
| 9 | `study_tasks` | Daily tasks, estimated minutes, priorities, deadlines, completion flags |
| 10 | `coding_problems` | LeetCode-style problem catalog with test cases and starter templates |
| 11 | `coding_submissions` | Candidate code submissions, execution times, test statuses |
| 12 | `mock_interviews` | Mock interview sessions, types, overall scores, feedback summaries |
| 13 | `interview_questions` | Dynamic questions generated for each mock session |
| 14 | `interview_responses` | 5-dimension scores and qualitative feedback per answer |
| 15 | `resumes` | Uploaded / pasted candidate resumes |
| 16 | `resume_analyses` | ATS scores, keyword matches/misses, skill gaps, suggestions |
| 17 | `agent_recommendations` | Explainable recommendation logs from agents |
| 18 | `progress_records` | Periodic snapshots of composite readiness for trend analysis |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ & npm 9+

### 1. Backend Setup
```bash
# Optional: create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies (if not already installed)
pip install fastapi uvicorn pydantic python-multipart requests
```

### 2. Initialize Database and Seed Data
```bash
python -m backend.database.seed_data
```
*Creates the database `backend/database/interview_tracker.db` with 7 subjects, 28+ quiz questions, 10+ coding problems, and pre-seeded student history.*

### 3. Start Backend Server
```bash
python run_app.py
```
*Runs on `http://127.0.0.1:8000` (Interactive Swagger Docs at `http://127.0.0.1:8000/docs`).*

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
*Opens on `http://127.0.0.1:5173`.*

> **One-Click Startup on Windows**: Simply run `start_dev.bat` in the root folder!

---

## 🔑 Pre-Seeded Demo Account
For instant demonstration without manual registration:
- **Email**: `demo@example.com`
- **Password**: `password123`
- *Includes pre-configured weak area in Dynamic Programming to showcase the adaptive feedback cascade.*

---

## 📊 The 8 Performance & Research Metrics

Viewable in the **Progress & Research** module:
1. **Skill Assessment Accuracy**: Confidence-to-score alignment ($>78\%$)
2. **Study Plan Adherence Rate**: Completed vs. scheduled tasks ratio
3. **Recommendation Relevance**: Solved rate of curated problem recommendations
4. **Mock Interview Evaluation Accuracy**: Consistency across multi-metric evaluations ($>85\%$)
5. **Resume Improvement Rate**: Historical ATS score delta ($+12-15\%$)
6. **Readiness Score Improvement**: Cumulative placement readiness trajectory
7. **User Engagement Rate**: Aggregated diagnostic, coding, and interview activity
8. **System Response Time**: Sub-$50\text{ ms}$ average latency across all 6 agents

---

## 🛠️ Environment Variables Configuration

Copy `.env.example` to `.env`:
```env
# Optional external LLMs (System uses built-in high-accuracy engine if omitted)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# JWT Secret
JWT_SECRET_KEY=agentic-ai-super-secret-jwt-key-2026-production

# Database Path
DB_PATH=backend/database/interview_tracker.db
```

---

## 🌐 Complete REST API Reference

### Authentication & Profile
- `POST /api/auth/register` - Create student account
- `POST /api/auth/login` - Login and get JWT token
- `GET  /api/auth/me` - Current authenticated user
- `GET  /api/profile` - Student goal and target role
- `PUT  /api/profile/update` - Update target company, hours, interview date

### Skill Assessment (Agent 1)
- `GET  /api/assessment/subjects` - List subjects with proficiency
- `GET  /api/assessment/topics/{subject_id}` - Topic breakdown
- `GET  /api/assessment/quiz` - Fetch quiz questions
- `POST /api/assessment/submit` - Submit answers and trigger multi-agent cascade
- `GET  /api/assessment/skill-profile` - Full skill profile

### Study Planner (Agent 2)
- `GET  /api/planner/current` - Active study plan and tasks
- `POST /api/planner/generate` - AI plan generation / replanning
- `POST /api/planner/tasks/{id}/toggle` - Toggle task completion status
- `POST /api/planner/tasks` - Add custom task

### Coding Practice (Agent 3)
- `GET  /api/coding/problems` - Browse problem catalog
- `GET  /api/coding/problems/{slug}` - Problem details & starter code
- `POST /api/coding/submit` - Test and record code submission
- `GET  /api/coding/recommendations` - Tailored problem recommendations
- `GET  /api/coding/history` - Candidate submission history

### Mock Interview (Agent 4)
- `POST /api/interview/start` - Generate questions & start session
- `POST /api/interview/respond` - Submit turn response & get 5-metric score
- `POST /api/interview/complete` - Finalize report & update readiness
- `GET  /api/interview/history` - Past interview records

### Resume Analyzer (Agent 5)
- `POST /api/resume/analyze` - Analyze pasted text
- `POST /api/resume/upload` - Upload PDF/text file
- `GET  /api/resume/history` - Past resume analyses

### Analytics & System (Agent 6 & Orchestrator)
- `GET  /api/analytics/dashboard` - Readiness dashboard & next actions
- `GET  /api/analytics/metrics` - 8 system performance metrics
- `GET  /api/analytics/trends` - Historical readiness snapshots
- `GET  /api/system/health` - Health check
- `GET  /api/system/agents` - Live latency and call counts for all 6 agents
