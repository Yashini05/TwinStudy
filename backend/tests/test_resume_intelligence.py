import os
import uuid
import io
import tempfile
import atexit
from pathlib import Path
from docx import Document

TEST_DB = Path(tempfile.gettempdir()) / f"twinstudy-resume-test-{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
atexit.register(lambda: TEST_DB.unlink(missing_ok=True))

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.db import SessionLocal
from app.models import ResumeDocument
from app.storage import DocumentStorage, StorageConfigurationError, safe_original_name

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


def docx_bytes(text):
    document = Document()
    document.add_paragraph(text)
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def test_document_upload_download_delete_and_isolation():
    token = register("document-owner")
    other = register("document-other")
    uploaded = client.post("/api/intelligence/resumes", headers=headers(token),
                           files={"file": ("../private resume.docx", docx_bytes("Skills: Python"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert uploaded.status_code == 201
    item_id = uploaded.json()["id"]
    assert uploaded.json()["original_name"] == "private resume.docx"
    assert client.get(f"/api/intelligence/resumes/{item_id}/download", headers=headers(token)).status_code == 200
    assert client.get(f"/api/intelligence/resumes/{item_id}/download", headers=headers(other)).status_code == 404
    assert client.delete(f"/api/intelligence/resumes/{item_id}", headers=headers(other)).status_code == 404
    assert client.delete(f"/api/intelligence/resumes/{item_id}", headers=headers(token)).status_code == 204
    assert client.get(f"/api/intelligence/resumes/{item_id}/download", headers=headers(token)).status_code == 404


def test_production_upload_persists_bytes_in_database():
    previous = settings.app_env
    settings.app_env = "production"
    settings.r2_account_id = None
    settings.r2_access_key_id = None
    settings.r2_secret_access_key = None
    settings.r2_bucket_name = None
    settings.r2_endpoint_url = None
    try:
        token = register("database-document-owner")
        uploaded = client.post(
            "/api/intelligence/resumes",
            headers=headers(token),
            files={"file": ("resume.docx", docx_bytes("Skills: Python"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert uploaded.status_code == 201
        session = SessionLocal()
        try:
            item = session.get(ResumeDocument, uploaded.json()["id"])
            assert item is not None
            assert item.storage_backend == "database"
            assert item.document_data
            assert client.get(f"/api/intelligence/resumes/{item.id}/download", headers=headers(token)).content == item.document_data
        finally:
            session.close()
    finally:
        settings.app_env = previous


def test_job_document_upload_download_and_delete():
    token = register("job-document-owner")
    uploaded = client.post("/api/intelligence/jobs/upload", headers=headers(token), data={
        "company": "Example Labs", "title": "Python Developer", "experience_level": "Entry",
    }, files={"file": ("job.docx", docx_bytes("Build Python services and SQL workflows with measurable outcomes."), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert uploaded.status_code == 201
    job_id = uploaded.json()["id"]
    assert client.get(f"/api/intelligence/jobs/{job_id}/download", headers=headers(token)).status_code == 200
    assert client.delete(f"/api/intelligence/jobs/{job_id}", headers=headers(token)).status_code == 204
    assert client.get(f"/api/intelligence/jobs/{job_id}/download", headers=headers(token)).status_code == 404


def test_storage_adapters_and_database_production_mode(monkeypatch):
    assert safe_original_name("../../resume?.pdf") == "resume_.pdf"
    class Body:
        def read(self): return b"contents"
    class Client:
        def __init__(self): self.objects = {}
        def put_object(self, **kwargs): self.objects[kwargs["Key"]] = kwargs["Body"]
        def get_object(self, **kwargs): return {"Body": Body()}
        def delete_object(self, **kwargs): self.objects.pop(kwargs["Key"], None)
    fake = Client()
    monkeypatch.setattr("app.storage.settings.r2_account_id", "account")
    monkeypatch.setattr("app.storage.settings.r2_access_key_id", "key")
    monkeypatch.setattr("app.storage.settings.r2_secret_access_key", "secret")
    monkeypatch.setattr("app.storage.settings.r2_bucket_name", "bucket")
    monkeypatch.setattr("app.storage.settings.r2_endpoint_url", "https://r2.example")
    monkeypatch.setattr(DocumentStorage, "_client", lambda self: fake)
    r2 = DocumentStorage()
    stored = r2.put(b"contents", "students/1/resumes/file.pdf", "application/pdf")
    assert stored.backend == "r2"
    assert r2.get(stored) == b"contents"
    r2.delete(stored)
    assert fake.objects == {}
    previous = settings.app_env
    settings.app_env = "production"
    settings.r2_account_id = None
    settings.r2_access_key_id = None
    settings.r2_secret_access_key = None
    settings.r2_bucket_name = None
    settings.r2_endpoint_url = None
    try:
        database = DocumentStorage()
        stored = database.put(b"contents", "students/1/resumes/file.pdf", "application/pdf")
        assert database.use_database is True
        assert stored.backend == "database"
        assert database.get(stored, b"contents") == b"contents"
        database.delete(stored)
    finally:
        settings.app_env = previous
