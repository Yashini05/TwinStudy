import json
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session
from pypdf import PdfReader
from docx import Document
from ..db import get_db
from ..models import CareerCertification, CareerExperience, CareerProfile, CareerProject, CareerSkill, JobComparison, JobDescription, JobPreparationTask, ResumeDocument, Student
from ..resume_intelligence import extract_job, extract_resume, match_job
from ..schemas import JobDescriptionInput, PreparationStatusInput, ResumeConfirmInput
from ..security import current_student
from ..storage import DocumentStorage, StorageConfigurationError, StoredObject, safe_original_name

router = APIRouter(prefix="/intelligence", tags=["resume and jobs"])
MAX_UPLOAD = 5 * 1024 * 1024


def storage() -> DocumentStorage:
    try:
        return DocumentStorage()
    except StorageConfigurationError as exc:
        raise HTTPException(503, str(exc)) from exc


def read_document(data: bytes, suffix: str) -> str:
    if suffix == ".pdf":
        import io
        return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
    if suffix == ".docx":
        import io
        return "\n".join(paragraph.text for paragraph in Document(io.BytesIO(data)).paragraphs)
    raise HTTPException(415, "Only PDF and DOCX files are supported")


@router.post("/resumes", status_code=201)
async def upload_resume(file: UploadFile = File(...), student: Student = Depends(current_student), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".pdf", ".docx"): raise HTTPException(415, "Only PDF and DOCX files are supported")
    data = await file.read()
    if len(data) > MAX_UPLOAD: raise HTTPException(413, "Resume must be 5 MB or smaller")
    try: text = read_document(data, suffix)
    except Exception as exc: raise HTTPException(422, f"Could not parse resume: {exc}") from exc
    if not text.strip(): raise HTTPException(422, "Resume contains no readable text")
    original_name = safe_original_name(file.filename)
    stored = f"students/{student.id}/resumes/{uuid.uuid4().hex}{suffix}"
    document_storage = storage()
    stored_object = document_storage.put(data, stored, file.content_type or "application/octet-stream")
    item = ResumeDocument(student_id=student.id, original_name=original_name, stored_name=stored,
                          storage_backend=stored_object.backend,
                          document_data=data if stored_object.backend == "database" else None,
                          content_type=file.content_type or "application/octet-stream", extracted_text=text[:100000],
                          extracted_json=json.dumps(extract_resume(text)))
    try:
        db.add(item); db.commit(); db.refresh(item)
    except Exception:
        db.rollback()
        document_storage.delete(stored_object)
        raise
    return {"id": item.id, "original_name": item.original_name, "extracted": json.loads(item.extracted_json), "confirmed": item.confirmed}


@router.get("/resumes")
def resumes(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return [{"id": item.id, "original_name": item.original_name, "created_at": item.created_at, "confirmed": item.confirmed,
             "extracted": json.loads(item.extracted_json)} for item in db.query(ResumeDocument).filter_by(student_id=student.id).all()]


@router.put("/resumes/{item_id}/confirm")
def confirm_resume(item_id: int, payload: ResumeConfirmInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(ResumeDocument).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Resume not found")
    item.confirmed = payload.confirmed; db.commit(); return {"id": item.id, "confirmed": item.confirmed}


@router.get("/resumes/{item_id}/download")
def download_resume(item_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(ResumeDocument).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Resume not found")
    try:
        data = storage().get(StoredObject(item.stored_name, item.storage_backend), item.document_data)
    except FileNotFoundError as exc:
        raise HTTPException(404, "Resume file is unavailable") from exc
    return Response(data, media_type=item.content_type, headers={"Content-Disposition": f'attachment; filename="{safe_original_name(item.original_name)}"'})


@router.delete("/resumes/{item_id}", status_code=204)
def delete_resume(item_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(ResumeDocument).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Resume not found")
    document_storage = storage()
    stored = StoredObject(item.stored_name, item.storage_backend)
    try:
        document_storage.delete(stored)
        db.delete(item)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return Response(status_code=204)


@router.post("/jobs", status_code=201)
def create_job(payload: JobDescriptionInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = JobDescription(student_id=student.id, company=payload.company, title=payload.title, experience_level=payload.experience_level,
                          source_text=payload.text, extracted_json=json.dumps(extract_job(payload.text)))
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "company": item.company, "title": item.title, "extracted": json.loads(item.extracted_json)}


@router.post("/jobs/upload", status_code=201)
async def upload_job(file: UploadFile = File(...), company: str = Form(...), title: str = Form(...),
                     experience_level: str = Form(...), student: Student = Depends(current_student), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".pdf", ".docx"): raise HTTPException(415, "Only PDF and DOCX files are supported")
    data = await file.read()
    if len(data) > MAX_UPLOAD: raise HTTPException(413, "Job description must be 5 MB or smaller")
    try: text = read_document(data, suffix)
    except Exception as exc: raise HTTPException(422, f"Could not parse job description: {exc}") from exc
    if len(text.strip()) < 30: raise HTTPException(422, "Job description contains insufficient readable text")
    original_name = safe_original_name(file.filename)
    stored = f"students/{student.id}/jobs/{uuid.uuid4().hex}{suffix}"
    document_storage = storage()
    stored_object = document_storage.put(data, stored, file.content_type or "application/octet-stream")
    item = JobDescription(student_id=student.id, company=company, title=title, experience_level=experience_level,
                          source_text=text[:100000], source_original_name=original_name,
                          source_content_type=file.content_type or "application/octet-stream",
                          source_object_key=stored_object.key, source_storage_backend=stored_object.backend,
                          source_document_data=data if stored_object.backend == "database" else None,
                          extracted_json=json.dumps(extract_job(text)))
    try:
        db.add(item); db.commit(); db.refresh(item)
    except Exception:
        db.rollback()
        document_storage.delete(stored_object)
        raise
    return {"id": item.id, "company": item.company, "title": item.title, "extracted": json.loads(item.extracted_json)}


@router.get("/jobs")
def jobs(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return [{"id": item.id, "company": item.company, "title": item.title, "experience_level": item.experience_level,
             "created_at": item.created_at, "extracted": json.loads(item.extracted_json)} for item in db.query(JobDescription).filter_by(student_id=student.id).order_by(JobDescription.created_at.desc()).all()]


@router.get("/jobs/{job_id}/download")
def download_job(job_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(JobDescription).filter_by(id=job_id, student_id=student.id).first()
    if not item or not item.source_object_key: raise HTTPException(404, "Job document not found")
    try:
        data = storage().get(StoredObject(item.source_object_key, item.source_storage_backend or "local"),
                             item.source_document_data)
    except FileNotFoundError as exc:
        raise HTTPException(404, "Job document is unavailable") from exc
    return Response(data, media_type=item.source_content_type or "application/octet-stream",
                    headers={"Content-Disposition": f'attachment; filename="{safe_original_name(item.source_original_name)}"'})


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(JobDescription).filter_by(id=job_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Job description not found")
    document_storage = storage() if item.source_object_key else None
    try:
        if document_storage and item.source_object_key:
            document_storage.delete(StoredObject(item.source_object_key, item.source_storage_backend or "local"))
        db.query(JobComparison).filter_by(job_id=item.id, student_id=student.id).delete()
        db.query(JobPreparationTask).filter_by(job_id=item.id, student_id=student.id).delete()
        db.delete(item); db.commit()
    except Exception:
        db.rollback()
        raise
    return Response(status_code=204)


@router.post("/jobs/{job_id}/match")
def compare_job(job_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter_by(id=job_id, student_id=student.id).first()
    if not job: raise HTTPException(404, "Job description not found")
    result = match_job(json.loads(job.extracted_json), db.query(CareerSkill).filter_by(student_id=student.id).all(),
                       db.query(CareerProject).filter_by(student_id=student.id).all(),
                       db.query(CareerExperience).filter_by(student_id=student.id).all(),
                       db.query(CareerCertification).filter_by(student_id=student.id).all(),
                       db.query(CareerProfile).filter_by(student_id=student.id).first())
    item = JobComparison(student_id=student.id, job_id=job.id, result_json=json.dumps(result)); db.add(item); db.commit(); db.refresh(item)
    return {"comparison_id": item.id, "job_id": job.id, **result}


@router.get("/comparisons")
def comparisons(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    rows = db.query(JobComparison, JobDescription).join(JobDescription, JobDescription.id == JobComparison.job_id).filter(JobComparison.student_id == student.id).order_by(JobComparison.created_at.desc()).all()
    return [{"id": comparison.id, "company": job.company, "title": job.title, "created_at": comparison.created_at, "result": json.loads(comparison.result_json)} for comparison, job in rows]


@router.get("/jobs/{job_id}/prep")
def prep(job_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    if not db.query(JobDescription).filter_by(id=job_id, student_id=student.id).first(): raise HTTPException(404, "Job description not found")
    if not db.query(JobPreparationTask).filter_by(job_id=job_id, student_id=student.id).count():
        tasks = [("Learn missing skills", "Study the highest-priority missing job requirements."), ("Practise", "Complete targeted exercises for the role requirements."),
                 ("Improve projects", "Add evidence and measurable outcomes to the most relevant project."), ("Prepare interviews", "Practise role-specific technical and behavioural interview questions.")]
        db.add_all(JobPreparationTask(student_id=student.id, job_id=job_id, title=title, detail=detail) for title, detail in tasks); db.commit()
    return db.query(JobPreparationTask).filter_by(job_id=job_id, student_id=student.id).all()


@router.put("/prep/{task_id}")
def update_prep(task_id: int, payload: PreparationStatusInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(JobPreparationTask).filter_by(id=task_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Preparation task not found")
    item.status = payload.status; db.commit(); return item
