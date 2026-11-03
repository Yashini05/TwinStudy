import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./resume_intelligence_test.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def register(label):
    response = client.post("/api/auth/register", json={
        "email": f"{label}-{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "name": label,
    })
    return response.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_job_matching_persists_and_is_isolated():
    token = register("matcher")
    other = register("other")
    created = client.post("/api/intelligence/jobs", headers=headers(token), json={
        "company": "Example Labs", "title": "Python Developer", "experience_level": "Entry",
        "text": "Build Python services and SQL data workflows. 1 year experience.",
    })
    assert created.status_code == 201
    job_id = created.json()["id"]
    comparison = client.post(f"/api/intelligence/jobs/{job_id}/match", headers=headers(token))
    assert comparison.status_code == 200
    assert comparison.json()["score"] == 0
    assert client.get("/api/intelligence/jobs", headers=headers(other)).json() == []
    assert client.get("/api/intelligence/comparisons", headers=headers(token)).json()
    assert client.post(f"/api/intelligence/jobs/{job_id}/match", headers=headers(other)).status_code == 404


def test_resume_type_and_job_validation():
    token = register("validation")
    rejected = client.post("/api/intelligence/resumes", headers=headers(token), files={"file": ("resume.txt", b"not supported", "text/plain")})
    assert rejected.status_code == 415
    short_job = client.post("/api/intelligence/jobs", headers=headers(token), json={
        "company": "A", "title": "B", "experience_level": "Entry", "text": "short",
    })
    assert short_job.status_code == 422
