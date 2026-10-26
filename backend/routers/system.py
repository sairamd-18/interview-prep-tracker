"""
System router: Health checks, agent status, and pipeline diagnostics.
"""
from fastapi import APIRouter
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/system", tags=["System & Diagnostics"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Agentic AI Interview Preparation Tracker",
        "version": "2.0.0",
        "agents_count": 6
    }

@router.get("/agents")
def get_agents_status():
    return {
        "agents": [
            {
                "name": orchestrator.skill_agent.name,
                "role": "Skill Assessment Agent",
                "status": "online",
                "calls": orchestrator.skill_agent.call_count,
                "latency_ms": round(orchestrator.skill_agent.get_avg_latency(), 2)
            },
            {
                "name": orchestrator.study_agent.name,
                "role": "Study Planning Agent",
                "status": "online",
                "calls": orchestrator.study_agent.call_count,
                "latency_ms": round(orchestrator.study_agent.get_avg_latency(), 2)
            },
            {
                "name": orchestrator.coding_agent.name,
                "role": "Coding Recommendation Agent",
                "status": "online",
                "calls": orchestrator.coding_agent.call_count,
                "latency_ms": round(orchestrator.coding_agent.get_avg_latency(), 2)
            },
            {
                "name": orchestrator.interview_agent.name,
                "role": "Mock Interview Agent",
                "status": "online",
                "calls": orchestrator.interview_agent.call_count,
                "latency_ms": round(orchestrator.interview_agent.get_avg_latency(), 2)
            },
            {
                "name": orchestrator.resume_agent.name,
                "role": "Resume Analysis Agent",
                "status": "online",
                "calls": orchestrator.resume_agent.call_count,
                "latency_ms": round(orchestrator.resume_agent.get_avg_latency(), 2)
            },
            {
                "name": orchestrator.progress_agent.name,
                "role": "Progress Monitoring Agent",
                "status": "online",
                "calls": orchestrator.progress_agent.call_count,
                "latency_ms": round(orchestrator.progress_agent.get_avg_latency(), 2)
            }
        ]
    }
