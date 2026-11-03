from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(120))
    year: Mapped[str | None] = mapped_column(String(40), nullable=True)
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subjects = relationship("Subject", back_populates="student", cascade="all, delete-orphan")
    records = relationship("AcademicRecord", back_populates="student", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    study_activities = relationship("StudyActivity", back_populates="student", cascade="all, delete-orphan")
    preferences = relationship("LearningPreference", back_populates="student", uselist=False, cascade="all, delete-orphan")
    goals = relationship("AcademicGoal", back_populates="student", cascade="all, delete-orphan")
    twins = relationship("DigitalTwinSnapshot", back_populates="student", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("email", name="students_email_key"),)


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    student = relationship("Student", back_populates="subjects")
    records = relationship("AcademicRecord", back_populates="subject", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="subject", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("student_id", "name"),)


class AcademicRecord(Base):
    __tablename__ = "academic_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    assessment: Mapped[str] = mapped_column(String(120))
    score: Mapped[float] = mapped_column(Float)
    max_score: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="records")
    subject = relationship("Subject", back_populates="records")


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    attended: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")


class StudyActivity(Base):
    __tablename__ = "study_activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    date: Mapped[str] = mapped_column(String(10))
    hours: Mapped[float] = mapped_column(Float)
    topic: Mapped[str | None] = mapped_column(String(120), nullable=True)
    student = relationship("Student", back_populates="study_activities")


class LearningPreference(Base):
    __tablename__ = "learning_preferences"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True)
    style: Mapped[str] = mapped_column(String(60))
    preferred_time: Mapped[str | None] = mapped_column(String(60), nullable=True)
    student = relationship("Student", back_populates="preferences")


class AcademicGoal(Base):
    __tablename__ = "academic_goals"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    target_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    student = relationship("Student", back_populates="goals")


class DigitalTwinSnapshot(Base):
    __tablename__ = "digital_twin_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    state_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="twins")


class CareerProfile(Base):
    __tablename__ = "career_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True, index=True)
    degree: Mapped[str | None] = mapped_column(String(160), nullable=True)
    department: Mapped[str | None] = mapped_column(String(160), nullable=True)
    institution: Mapped[str | None] = mapped_column(String(180), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    career_interests: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(160), nullable=True)
    preferred_industries: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_locations: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    professional_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint("student_id", name="career_profiles_student_id_key"),)


class CareerSkill(Base):
    __tablename__ = "career_skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80))
    proficiency: Mapped[str] = mapped_column(String(30))
    learning_status: Mapped[str] = mapped_column(String(30), default="Learning")
    experience_months: Mapped[int] = mapped_column(Integer, default=0)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CareerProject(Base):
    __tablename__ = "career_projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    problem_solved: Mapped[str | None] = mapped_column(Text, nullable=True)
    technologies: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80))
    github_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    live_demo_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    contribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_demonstrated: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    completion_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CareerExperience(Base):
    __tablename__ = "career_experiences"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(160))
    organization: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(10), nullable=True)


class CareerCertification(Base):
    __tablename__ = "career_certifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    issuer: Mapped[str] = mapped_column(String(160))
    issue_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(300), nullable=True)


class CareerGoal(Base):
    __tablename__ = "career_goals"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(30), default="Not Started")


class CareerRoadmapTask(Base):
    __tablename__ = "career_roadmap_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    phase: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(180))
    detail: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="Not Started")


class CareerTwinSnapshot(Base):
    __tablename__ = "career_twin_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    state_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResumeDocument(Base):
    __tablename__ = "resume_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    storage_backend: Mapped[str] = mapped_column(String(20), default="local")
    document_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    content_type: Mapped[str] = mapped_column(String(120))
    extracted_text: Mapped[str] = mapped_column(Text)
    extracted_json: Mapped[str] = mapped_column(Text)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    company: Mapped[str] = mapped_column(String(180))
    title: Mapped[str] = mapped_column(String(180))
    experience_level: Mapped[str] = mapped_column(String(40))
    source_text: Mapped[str] = mapped_column(Text)
    source_original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_storage_backend: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_document_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    extracted_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobComparison(Base):
    __tablename__ = "job_comparisons"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobPreparationTask(Base):
    __tablename__ = "job_preparation_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    detail: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="Not Started")
