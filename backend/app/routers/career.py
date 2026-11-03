import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..career_analytics import career_state, ensure_roadmap
from ..db import get_db
from ..models import CareerCertification, CareerExperience, CareerGoal, CareerProfile, CareerProject, CareerRoadmapTask, CareerSkill, Student
from ..schemas import CareerCertificationInput, CareerExperienceInput, CareerGoalInput, CareerProfileInput, CareerProjectInput, CareerSkillInput, RoadmapStatusInput
from ..security import current_student

router = APIRouter(prefix="/career", tags=["career"])


def recalculate(student: Student, db: Session):
    state = career_state(student, db)
    ensure_roadmap(student, db, state)
    return state


@router.get("/profile")
def get_profile(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return db.query(CareerProfile).filter_by(student_id=student.id).first()


@router.put("/profile")
def update_profile(payload: CareerProfileInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerProfile).filter_by(student_id=student.id).first() or CareerProfile(student_id=student.id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.add(item); db.commit(); db.refresh(item); recalculate(student, db)
    return item


def crud_list(model, student, db):
    return db.query(model).filter_by(student_id=student.id).all()


@router.get("/skills")
def list_skills(student: Student = Depends(current_student), db: Session = Depends(get_db)): return crud_list(CareerSkill, student, db)


@router.post("/skills", status_code=201)
def add_skill(payload: CareerSkillInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = CareerSkill(student_id=student.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); recalculate(student, db); return item


@router.put("/skills/{item_id}")
def update_skill(item_id: int, payload: CareerSkillInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerSkill).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Skill not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); recalculate(student, db); return item


@router.delete("/skills/{item_id}", status_code=204)
def delete_skill(item_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerSkill).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Skill not found")
    db.delete(item); db.commit(); recalculate(student, db)


@router.get("/projects")
def list_projects(student: Student = Depends(current_student), db: Session = Depends(get_db)): return crud_list(CareerProject, student, db)


@router.post("/projects", status_code=201)
def add_project(payload: CareerProjectInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = CareerProject(student_id=student.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); recalculate(student, db); return item


@router.put("/projects/{item_id}")
def update_project(item_id: int, payload: CareerProjectInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerProject).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Project not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); recalculate(student, db); return item


@router.delete("/projects/{item_id}", status_code=204)
def delete_project(item_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerProject).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Project not found")
    db.delete(item); db.commit(); recalculate(student, db)


@router.get("/experience")
def list_experience(student: Student = Depends(current_student), db: Session = Depends(get_db)): return crud_list(CareerExperience, student, db)


@router.post("/experience", status_code=201)
def add_experience(payload: CareerExperienceInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = CareerExperience(student_id=student.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); recalculate(student, db); return item


@router.delete("/experience/{item_id}", status_code=204)
def delete_experience(item_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerExperience).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Experience not found")
    db.delete(item); db.commit(); recalculate(student, db)


@router.get("/certifications")
def list_certifications(student: Student = Depends(current_student), db: Session = Depends(get_db)): return crud_list(CareerCertification, student, db)


@router.post("/certifications", status_code=201)
def add_certification(payload: CareerCertificationInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = CareerCertification(student_id=student.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); recalculate(student, db); return item


@router.delete("/certifications/{item_id}", status_code=204)
def delete_certification(item_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerCertification).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Certification not found")
    db.delete(item); db.commit(); recalculate(student, db)


@router.get("/goals")
def list_goals(student: Student = Depends(current_student), db: Session = Depends(get_db)): return crud_list(CareerGoal, student, db)


@router.post("/goals", status_code=201)
def add_goal(payload: CareerGoalInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = CareerGoal(student_id=student.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); recalculate(student, db); return item


@router.get("/roadmap")
def roadmap(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    state = career_state(student, db); ensure_roadmap(student, db, state)
    return crud_list(CareerRoadmapTask, student, db)


@router.put("/roadmap/{item_id}")
def update_roadmap(item_id: int, payload: RoadmapStatusInput, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    item = db.query(CareerRoadmapTask).filter_by(id=item_id, student_id=student.id).first()
    if not item: raise HTTPException(404, "Roadmap task not found")
    item.status = payload.status; db.commit(); recalculate(student, db); return item


@router.get("/twin")
def twin(student: Student = Depends(current_student), db: Session = Depends(get_db)): return career_state(student, db)


@router.get("/history")
def history(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    from ..models import CareerTwinSnapshot
    return [{"id": item.id, "created_at": item.created_at, "state": json.loads(item.state_json)} for item in db.query(CareerTwinSnapshot).filter_by(student_id=student.id).order_by(CareerTwinSnapshot.created_at.desc()).limit(20).all()]
