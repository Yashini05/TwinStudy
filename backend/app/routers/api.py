import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..analytics import calculate_twin
from ..db import get_db
from ..models import AcademicGoal, AcademicRecord, Attendance, LearningPreference, StudyActivity, Subject, Student
from ..schemas import (AuthInput, AttendanceInput, GoalInput, LoginInput, PreferenceInput, ProfileInput, RecordInput,
                       SimulationInput, StudentOut, StudyInput, SubjectInput, SubjectOut, TokenOut)
from ..security import create_token, current_student, hash_password, verify_password

router = APIRouter()


@router.post("/auth/register", response_model=TokenOut, status_code=201)
def register(payload: AuthInput, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.query(Student).filter_by(email=email).first():
        raise HTTPException(409, "Email is already registered")
    student = Student(email=email, password_hash=hash_password(payload.password), name=payload.name.strip())
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email is already registered")
    db.refresh(student)
    return {"access_token": create_token(student.id)}


@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(email=payload.email.lower()).first()
    if not student or not verify_password(payload.password, student.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return {"access_token": create_token(student.id)}


@router.get("/me", response_model=StudentOut)
def me(student: Student = Depends(current_student)):
    return student


@router.put("/me", response_model=StudentOut)
def update_me(payload: ProfileInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    for key, value in payload.model_dump().items():
        setattr(student, key, value)
    db.commit(); db.refresh(student)
    return student


@router.get("/subjects", response_model=list[SubjectOut])
def subjects(student: Student = Depends(current_student)):
    return student.subjects


@router.post("/subjects", response_model=SubjectOut, status_code=201)
def add_subject(payload: SubjectInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    if any(item.name.lower() == payload.name.lower() for item in student.subjects):
        raise HTTPException(409, "Subject already exists")
    item = Subject(student_id=student.id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.post("/records", status_code=201)
def add_record(payload: RecordInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    if not db.query(Subject).filter_by(id=payload.subject_id, student_id=student.id).first():
        raise HTTPException(404, "Subject not found")
    item = AcademicRecord(student_id=student.id, **payload.model_dump())
    db.add(item); db.commit()
    return {"id": item.id}


@router.post("/attendance", status_code=201)
def add_attendance(payload: AttendanceInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    if payload.attended > payload.total or not db.query(Subject).filter_by(id=payload.subject_id, student_id=student.id).first():
        raise HTTPException(400, "Invalid attendance or subject")
    item = Attendance(student_id=student.id, **payload.model_dump())
    db.add(item); db.commit()
    return {"id": item.id}


@router.post("/study", status_code=201)
def add_study(payload: StudyInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = StudyActivity(student_id=student.id, **payload.model_dump())
    db.add(item); db.commit()
    return {"id": item.id}


@router.put("/preferences")
def preferences(payload: PreferenceInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = student.preferences or LearningPreference(student_id=student.id)
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.add(item); db.commit()
    return payload


@router.post("/goals", status_code=201)
def add_goal(payload: GoalInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = AcademicGoal(student_id=student.id, **payload.model_dump())
    db.add(item); db.commit()
    return {"id": item.id}


@router.get("/twin")
def twin(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return calculate_twin(student, db)


@router.get("/twin/history")
def twin_history(student: Student = Depends(current_student)):
    return [{"id": item.id, "created_at": item.created_at, "state": json.loads(item.state_json)} for item in student.twins[-20:]]


@router.post("/simulate")
def simulate(payload: SimulationInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    state = calculate_twin(student, db, persist=False)
    base = state["average_score"] or 0
    projected = min(100, max(0, base + payload.score_delta + payload.study_hours_delta * 2 + payload.attendance_delta * 0.15))
    return {"baseline": base, "projected": round(projected, 1), "change": round(projected - base, 1),
            "assumptions": ["Study hours contribute up to a modest projected improvement.", "Attendance contribution is capped by the 100% score range.",
                            "Simulation is hypothetical and does not change stored student records."]}
