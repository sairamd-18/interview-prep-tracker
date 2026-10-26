"""
Agent 5: Resume Analysis Agent
Analyzes candidate resumes for target roles, assessing structure, technical keywords,
relevance, project descriptions, identifying skill gaps, and generating an actionable scorecard.
"""
import json
import re
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.llm_service import llm_service
from backend.database.db import get_db

# Role-specific benchmark keywords
ROLE_BENCHMARKS = {
    "Software Development Engineer (SDE)": [
        "Data Structures", "Algorithms", "Python", "Java", "C++", "SQL", "Git", "REST API",
        "System Design", "Microservices", "Docker", "CI/CD", "Unit Testing", "AWS", "Kubernetes"
    ],
    "Frontend Developer": [
        "JavaScript", "TypeScript", "React", "Vue", "HTML5", "CSS3", "Tailwind CSS", "Redux",
        "Webpack", "Vite", "Responsive Design", "Web Performance", "Accessibility / a11y", "REST API"
    ],
    "Backend Developer": [
        "Python", "Node.js", "Java", "FastAPI", "Express", "Spring Boot", "PostgreSQL", "MongoDB",
        "Redis", "Kafka", "Docker", "API Design", "Distributed Systems", "Authentication", "Linux"
    ],
    "Data Scientist / ML Engineer": [
        "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Pandas", "NumPy",
        "Scikit-Learn", "SQL", "Data Visualization", "NLP", "Feature Engineering", "Model Evaluation"
    ]
}

class ResumeAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ResumeAnalysisAgent",
            description="Evaluates resume text against target job roles, detecting keyword matches, skill gaps, and structural formatting."
        )

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
            user_id: int
            resume_text: str
            target_role: str (optional)
            filename: str (optional)
        Output:
            resume_id: int
            overall_score: float
            structure_score: float
            keyword_score: float
            relevance_score: float
            matched_keywords: List[str]
            missing_keywords: List[str]
            skill_gaps: List[str]
            suggestions: List[str]
        """
        user_id = input_data.get("user_id")
        resume_text = input_data.get("resume_text", "")
        target_role = input_data.get("target_role", "Software Development Engineer (SDE)")
        filename = input_data.get("filename", "Uploaded_Resume.txt")

        if not resume_text or len(resume_text.strip()) < 40:
            return {"status": "error", "message": "Resume text is too brief to analyze meaningfully."}

        # 1. Structural evaluation
        has_education = bool(re.search(r'\b(education|university|college|b\.tech|bachelor|degree)\b', resume_text, re.IGNORECASE))
        has_skills = bool(re.search(r'\b(skills|technologies|proficiencies|languages)\b', resume_text, re.IGNORECASE))
        has_projects = bool(re.search(r'\b(projects|experience|internship|work)\b', resume_text, re.IGNORECASE))
        has_contact = bool(re.search(r'[\w\.-]+@[\w\.-]+', resume_text))
        has_metrics = bool(re.search(r'\b(\d+%\s*|\d+x|\$\d+|\d+\s*users|\d+\s*ms)\b', resume_text, re.IGNORECASE))

        structure_pts = 40.0
        if has_education: structure_pts += 15.0
        if has_skills: structure_pts += 15.0
        if has_projects: structure_pts += 15.0
        if has_contact: structure_pts += 10.0
        if has_metrics: structure_pts += 5.0
        structure_score = min(100.0, structure_pts)

        # 2. Keyword & Skill Gap Analysis
        benchmarks = ROLE_BENCHMARKS.get(target_role, ROLE_BENCHMARKS["Software Development Engineer (SDE)"])
        matched_keywords = []
        missing_keywords = []

        resume_lower = resume_text.lower()
        for kw in benchmarks:
            if kw.lower() in resume_lower:
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        keyword_ratio = len(matched_keywords) / len(benchmarks) if benchmarks else 0.5
        keyword_score = round(min(100.0, keyword_ratio * 100.0 + 10.0), 1)
        relevance_score = round(min(100.0, keyword_score * 0.7 + structure_score * 0.3), 1)

        overall_score = round(0.25 * structure_score + 0.40 * keyword_score + 0.35 * relevance_score, 1)

        # 3. LLM Enhancement / Intelligent Heuristics
        system_prompt = "You are an ATS (Applicant Tracking System) and Senior Technical Hiring Manager."
        prompt = f"""
        Target Role: {target_role}
        Resume Text Snippet: {resume_text[:2000]}
        Matched Keywords: {matched_keywords}
        Missing Benchmarks: {missing_keywords}

        Analyze the resume and return valid JSON with:
        - skill_gaps: 3 concise bullet points identifying missing foundational skills or experiences.
        - suggestions: 3 actionable, specific improvements to improve ATS score and interview callback rates.
        """

        fallback_analysis = {
            "skill_gaps": [
                f"Lacks explicit mention of modern production tools like {', '.join(missing_keywords[:2])} for the {target_role} role.",
                "Project descriptions have limited quantitative metrics (e.g. latency reduction, user scale, efficiency improvements).",
                "Needs stronger demonstration of automated testing and CI/CD pipelines."
            ],
            "suggestions": [
                "Incorporate action verbs and quantify achievements using Google's formula: 'Accomplished [X] measured by [Y] by doing [Z]'.",
                f"Add critical missing technical keywords ({', '.join(missing_keywords[:3])}) naturally into project descriptions.",
                "Ensure clear bullet points under each project highlighting technical architecture, tools used, and personal contribution."
            ]
        }

        ai_feedback = llm_service.generate_json(prompt, system_prompt, fallback_analysis)
        skill_gaps = ai_feedback.get("skill_gaps", fallback_analysis["skill_gaps"])
        suggestions = ai_feedback.get("suggestions", fallback_analysis["suggestions"])

        # 4. Save to Database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resumes (user_id, filename, file_text, target_role)
                VALUES (?, ?, ?, ?)
            """, (user_id, filename, resume_text, target_role))
            resume_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO resume_analyses (
                    resume_id, overall_score, structure_score, keyword_score, relevance_score,
                    matched_keywords_json, missing_keywords_json, skill_gaps_json, suggestions_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resume_id, overall_score, structure_score, keyword_score, relevance_score,
                json.dumps(matched_keywords), json.dumps(missing_keywords),
                json.dumps(skill_gaps), json.dumps(suggestions)
            ))

        return {
            "resume_id": resume_id,
            "filename": filename,
            "target_role": target_role,
            "overall_score": overall_score,
            "structure_score": structure_score,
            "keyword_score": keyword_score,
            "relevance_score": relevance_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "skill_gaps": skill_gaps,
            "suggestions": suggestions
        }
