import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./career_test.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def register(label: str):
    return client.post("/api/auth/register", json={
        "email": f"{label}-{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "name": label.title(),
    }).json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_career_profile_skill_project_readiness_and_isolation():
    token = register("career-student")
    other = register("other-student")
    assert client.put("/api/career/profile", headers=auth(token), json={
        "degree": "BSc", "department": "Computer Science", "institution": "Example University",
        "graduation_year": 2027, "target_role": "Software Engineer",
        "professional_summary": "Student building reliable software.",
    }).status_code == 200
    skill = client.post("/api/career/skills", headers=auth(token), json={
        "name": "Python", "category": "Programming", "proficiency": "Intermediate",
        "learning_status": "Applied", "experience_months": 12, "evidence": "TwinStudy project",
    })
    assert skill.status_code == 201
    project = client.post("/api/career/projects", headers=auth(token), json={
        "name": "TwinStudy", "description": "A student analytics platform with measurable outputs.",
        "category": "Academic", "technologies": "Python, React", "skills_demonstrated": "Programming",
    })
    assert project.status_code == 201
    assert client.post("/api/career/experience", headers=auth(token), json={
        "kind": "Internship", "title": "Developer intern", "organization": "Example Labs",
    }).status_code == 201
    assert client.post("/api/career/certifications", headers=auth(token), json={
        "name": "Cloud Fundamentals", "issuer": "Example Academy",
    }).status_code == 201
    state = client.get("/api/career/twin", headers=auth(token)).json()
    assert state["readiness_score"] is not None
    assert state["projects_count"] == 1
    assert client.get("/api/career/skills", headers=auth(other)).json() == []
    roadmap = client.get("/api/career/roadmap", headers=auth(token)).json()
    assert len(roadmap) == 5
    assert client.put(f"/api/career/roadmap/{roadmap[0]['id']}", headers=auth(token),
                      json={"status": "Completed"}).status_code == 200
    assert client.get("/api/career/history", headers=auth(token)).json()


def test_career_validation_keeps_api_explicit():
    token = register("validation")
    response = client.post("/api/career/skills", headers=auth(token), json={
        "name": "Python", "category": "Programming", "proficiency": "Master",
    })
    assert response.status_code == 422
