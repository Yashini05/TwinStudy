import json
from datetime import datetime
from sqlalchemy.orm import Session
from .models import CareerCertification, CareerExperience, CareerProfile, CareerProject, CareerRoadmapTask, CareerSkill, CareerTwinSnapshot, Student

ROLE_SKILLS = {
    "software engineer": ["Programming", "Software development", "Databases"],
    "data scientist": ["Data science", "Programming", "Statistics"],
    "product manager": ["Business and management", "Communication", "Problem solving"],
    "designer": ["Design", "Communication", "Problem solving"],
}


def career_state(student: Student, db: Session, persist: bool = True) -> dict:
    profile = db.query(CareerProfile).filter_by(student_id=student.id).first()
    skills = db.query(CareerSkill).filter_by(student_id=student.id).all()
    projects = db.query(CareerProject).filter_by(student_id=student.id).all()
    experiences = db.query(CareerExperience).filter_by(student_id=student.id).all()
    certifications = db.query(CareerCertification).filter_by(student_id=student.id).all()
    tasks = db.query(CareerRoadmapTask).filter_by(student_id=student.id).all()
    role = (profile.target_role if profile else "") or ""
    required = ROLE_SKILLS.get(role.lower(), [])
    existing_categories = {skill.category.lower() for skill in skills}
    missing = [item for item in required if item.lower() not in existing_categories]
    evidence_points = sum(1 for skill in skills if skill.evidence or skill.verified)
    score_parts = {
        "profile": 20 if profile and profile.target_role and profile.degree and profile.professional_summary else 0,
        "skills": min(30, len(skills) * 10),
        "evidence": min(20, (len(projects) * 8) + (evidence_points * 4)),
        "experience": min(15, len(experiences) * 8),
        "credentials": min(10, len(certifications) * 5),
        "roadmap": min(5, sum(1 for task in tasks if task.status == "Completed")),
    }
    enough_data = bool(profile and (skills or projects or experiences))
    readiness = round(sum(score_parts.values()), 1) if enough_data else None
    recommendations = []
    for category in missing:
        recommendations.append({"phase": "Learn", "title": f"Build {category}", "detail": f"Study and practise one foundational {category} skill."})
    if not projects:
        recommendations.append({"phase": "Build", "title": "Create a portfolio project", "detail": "Build one project that demonstrates your target-role skills."})
    if not experiences:
        recommendations.append({"phase": "Demonstrate", "title": "Add practical evidence", "detail": "Log an internship, hackathon, research activity, or meaningful contribution."})
    if not recommendations:
        recommendations.append({"phase": "Prepare", "title": "Practise target-role interviews", "detail": "Complete a mock interview and document feedback."})
    state = {
        "profile_completion": round(sum(bool(getattr(profile, field, None)) for field in ("degree", "department", "institution", "graduation_year", "target_role", "professional_summary")) / 6 * 100) if profile else 0,
        "target_role": role or None, "readiness_score": readiness, "insufficient_data": not enough_data,
        "score_breakdown": score_parts, "required_categories": required, "missing_categories": missing,
        "skills_count": len(skills), "projects_count": len(projects), "experiences_count": len(experiences),
        "certifications_count": len(certifications), "completed_tasks": sum(1 for task in tasks if task.status == "Completed"),
        "recommendations": recommendations, "updated_at": datetime.utcnow().isoformat(),
    }
    if persist:
        db.add(CareerTwinSnapshot(student_id=student.id, state_json=json.dumps(state)))
        db.commit()
    return state


def ensure_roadmap(student: Student, db: Session, state: dict):
    if db.query(CareerRoadmapTask).filter_by(student_id=student.id).count():
        return
    tasks = [
        ("Learn", "Close the top skill gap", "Learn the first missing skill for your selected role."),
        ("Practise", "Complete deliberate practice", "Complete three exercises and reflect on your results."),
        ("Build", "Ship a portfolio project", "Create a project with clear documentation and demonstrated skills."),
        ("Demonstrate", "Collect evidence", "Add a project, certification, or practical experience record."),
        ("Prepare", "Practise interviews", "Complete a mock interview and record improvement actions."),
    ]
    for phase, title, detail in tasks:
        db.add(CareerRoadmapTask(student_id=student.id, phase=phase, title=title, detail=detail))
    db.commit()
