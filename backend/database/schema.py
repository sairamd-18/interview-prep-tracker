"""
Relational Database Schema for Agentic AI Interview Preparation Tracker
Supports SQLite with foreign keys, indexes, and full relational integrity.
"""

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    target_role TEXT DEFAULT 'Software Development Engineer (SDE)',
    target_company TEXT DEFAULT 'Top Tech / Tier 1 Product',
    interview_date DATE,
    daily_study_hours REAL DEFAULT 3.0,
    experience_level TEXT DEFAULT 'Fresher / Entry Level',
    bio TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Subjects (DSA, DBMS, OS, Computer Networks, OOP, Aptitude, Behavioral)
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT DEFAULT 'BookOpen',
    display_order INTEGER DEFAULT 0
);

-- 4. Topics within subjects
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    difficulty_weight REAL DEFAULT 1.0,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(subject_id, name)
);

-- 5. Quiz Questions
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    options_json TEXT NOT NULL, -- JSON array of 4 options
    correct_answer INTEGER NOT NULL, -- index (0-3)
    explanation TEXT,
    difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- 6. Quiz Attempts
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    score_percentage REAL NOT NULL,
    time_taken_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 7. Skill Profiles (Continuously evolving per student & topic)
CREATE TABLE IF NOT EXISTS skill_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    proficiency_score REAL NOT NULL DEFAULT 0.0, -- 0 to 100
    status TEXT CHECK(status IN ('Weak', 'Moderate', 'Strong')) DEFAULT 'Moderate',
    confidence_level REAL DEFAULT 0.5, -- 0.0 to 1.0
    quizzes_taken INTEGER DEFAULT 0,
    last_evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    UNIQUE(user_id, topic_id)
);

-- 8. Study Plans
CREATE TABLE IF NOT EXISTS study_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    target_date DATE,
    total_weeks INTEGER DEFAULT 4,
    current_status TEXT CHECK(current_status IN ('Active', 'Completed', 'Archived')) DEFAULT 'Active',
    generated_by_agent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 9. Study Tasks
CREATE TABLE IF NOT EXISTS study_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_plan_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    topic_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
    estimated_minutes INTEGER DEFAULT 60,
    day_number INTEGER DEFAULT 1,
    deadline DATE,
    is_completed INTEGER DEFAULT 0, -- 0 or 1
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (study_plan_id) REFERENCES study_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 10. Coding Problems
CREATE TABLE IF NOT EXISTS coding_problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')) DEFAULT 'Easy',
    description TEXT NOT NULL,
    starter_code TEXT,
    test_cases_json TEXT, -- JSON array of test cases
    solution_notes TEXT,
    acceptance_rate REAL DEFAULT 70.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- 11. Coding Submissions
CREATE TABLE IF NOT EXISTS coding_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    language TEXT DEFAULT 'python',
    status TEXT CHECK(status IN ('Accepted', 'Wrong Answer', 'Time Limit Exceeded', 'Runtime Error')) DEFAULT 'Accepted',
    execution_time_ms INTEGER DEFAULT 45,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES coding_problems(id) ON DELETE CASCADE
);

-- 12. Mock Interviews
CREATE TABLE IF NOT EXISTS mock_interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interview_type TEXT CHECK(interview_type IN ('Technical', 'Behavioral', 'Mixed')) DEFAULT 'Technical',
    target_role TEXT DEFAULT 'Software Development Engineer',
    status TEXT CHECK(status IN ('In_Progress', 'Completed', 'Abandoned')) DEFAULT 'In_Progress',
    overall_score REAL DEFAULT 0.0,
    feedback_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 13. Interview Questions
CREATE TABLE IF NOT EXISTS interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mock_interview_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    category TEXT DEFAULT 'Technical',
    expected_key_points TEXT,
    order_idx INTEGER DEFAULT 0,
    FOREIGN KEY (mock_interview_id) REFERENCES mock_interviews(id) ON DELETE CASCADE
);

-- 14. Interview Responses
CREATE TABLE IF NOT EXISTS interview_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_question_id INTEGER UNIQUE NOT NULL,
    user_response TEXT NOT NULL,
    technical_score REAL DEFAULT 0.0,
    clarity_score REAL DEFAULT 0.0,
    confidence_score REAL DEFAULT 0.0,
    communication_score REAL DEFAULT 0.0,
    relevance_score REAL DEFAULT 0.0,
    feedback TEXT,
    key_strengths TEXT,
    improvement_areas TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_question_id) REFERENCES interview_questions(id) ON DELETE CASCADE
);

-- 15. Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_text TEXT NOT NULL,
    target_role TEXT DEFAULT 'Software Development Engineer',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 16. Resume Analyses
CREATE TABLE IF NOT EXISTS resume_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    overall_score REAL NOT NULL,
    structure_score REAL NOT NULL,
    keyword_score REAL NOT NULL,
    relevance_score REAL NOT NULL,
    matched_keywords_json TEXT,
    missing_keywords_json TEXT,
    skill_gaps_json TEXT,
    suggestions_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

-- 17. Agent Recommendations (Recorded outputs with explainability)
CREATE TABLE IF NOT EXISTS agent_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    recommendation_type TEXT NOT NULL,
    content_json TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    is_dismissed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 18. Progress Records (Historical snapshots of readiness)
CREATE TABLE IF NOT EXISTS progress_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    readiness_score REAL NOT NULL,
    dsa_score REAL DEFAULT 0.0,
    dbms_score REAL DEFAULT 0.0,
    os_score REAL DEFAULT 0.0,
    cn_score REAL DEFAULT 0.0,
    oop_score REAL DEFAULT 0.0,
    aptitude_score REAL DEFAULT 0.0,
    behavioral_score REAL DEFAULT 0.0,
    coding_completion_pct REAL DEFAULT 0.0,
    resume_score REAL DEFAULT 0.0,
    interview_avg_score REAL DEFAULT 0.0,
    study_plan_adherence REAL DEFAULT 0.0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_skill_profiles_user ON skill_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_study_tasks_user ON study_tasks(user_id, is_completed);
CREATE INDEX IF NOT EXISTS idx_coding_subs_user ON coding_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_records_user ON progress_records(user_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_agent_recs_user ON agent_recommendations(user_id, is_dismissed);
"""
