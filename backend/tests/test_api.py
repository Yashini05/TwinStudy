import os
import uuid
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_register_and_protected_route():
    response = client.post("/api/auth/register", json={"email": "test@example.com", "password": "password123", "name": "Test Student"})
    assert response.status_code in (201, 409)
    token = response.json()["access_token"] if response.status_code == 201 else client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "password123"}).json()["access_token"]
    assert client.get("/api/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_registration_duplicate_has_clear_error_and_login_works():
    email = f"registration-{uuid.uuid4().hex}@example.com"
    payload = {"email": email.upper(), "password": "password123", "name": "Registration Student"}
    created = client.post("/api/auth/register", json=payload)
    assert created.status_code == 201
    duplicate = client.post("/api/auth/register", json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Email is already registered"
    login = client.post("/api/auth/login", json={"email": email, "password": payload["password"]})
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_twin_prediction_is_isolated_and_simulation_is_read_only():
    suffix = uuid.uuid4().hex[:8]
    token = client.post("/api/auth/register", json={
        "email": f"analytics-{suffix}@example.com",
        "password": "password123",
        "name": "Analytics Student",
    }).json()["access_token"]
    other_token = client.post("/api/auth/register", json={
        "email": f"other-{suffix}@example.com",
        "password": "password123",
        "name": "Other Student",
    }).json()["access_token"]
    subject_id = client.post("/api/subjects", headers={"Authorization": f"Bearer {token}"},
                             json={"name": "Statistics"}).json()["id"]
    for index, score in enumerate((40, 60, 80)):
        client.post("/api/records", headers={"Authorization": f"Bearer {token}"},
                    json={"subject_id": subject_id, "assessment": f"Assessment {index}",
                          "score": score, "max_score": 100})
    client.post("/api/attendance", headers={"Authorization": f"Bearer {token}"},
                json={"subject_id": subject_id, "attended": 6, "total": 10})
    twin = client.get("/api/twin", headers={"Authorization": f"Bearer {token}"}).json()
    assert twin["prediction"]["method"] == "linear regression"
    assert client.get("/api/subjects", headers={"Authorization": f"Bearer {other_token}"}).json() == []
    history_before = client.get("/api/twin/history", headers={"Authorization": f"Bearer {token}"}).json()
    simulation = client.post("/api/simulate", headers={"Authorization": f"Bearer {token}"},
                             json={"study_hours_delta": 2, "attendance_delta": 5, "score_delta": 3})
    assert simulation.status_code == 200
    history_after = client.get("/api/twin/history", headers={"Authorization": f"Bearer {token}"}).json()
    assert len(history_after) == len(history_before)
