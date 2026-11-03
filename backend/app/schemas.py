from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthInput(BaseModel):
    email: str
    password: str = Field(min_length=8)
    name: str = Field(min_length=2, max_length=120)


class LoginInput(BaseModel):
    email: str
    password: str


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    year: str | None = None
    department: str | None = None


class ProfileInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    year: str | None = None
    department: str | None = None


class SubjectInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str | None = Field(default=None, max_length=30)


class SubjectOut(SubjectInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RecordInput(BaseModel):
    subject_id: int
    assessment: str = Field(min_length=2, max_length=120)
    max_score: float = Field(gt=0)
    score: float = Field(ge=0)

    @field_validator("score")
    @classmethod
    def score_not_over_max(cls, value, info):
        maximum = info.data.get("max_score")
        if maximum is not None and value > maximum:
            raise ValueError("score cannot exceed max_score")
        return value


class AttendanceInput(BaseModel):
    subject_id: int
    attended: int = Field(ge=0)
    total: int = Field(gt=0)


class StudyInput(BaseModel):
    date: str
    hours: float = Field(ge=0, le=24)
    topic: str | None = None


class PreferenceInput(BaseModel):
    style: str = Field(min_length=2, max_length=60)
    preferred_time: str | None = None


class GoalInput(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    target_score: float | None = Field(default=None, ge=0, le=100)
    due_date: str | None = None


class SimulationInput(BaseModel):
    study_hours_delta: float = Field(default=0, ge=-24, le=24)
    attendance_delta: float = Field(default=0, ge=-100, le=100)
    score_delta: float = Field(default=0, ge=-100, le=100)


class CareerProfileInput(BaseModel):
    degree: str | None = None
    department: str | None = None
    institution: str | None = None
    graduation_year: int | None = Field(default=None, ge=1900, le=2200)
    career_interests: str | None = None
    target_role: str | None = None
    preferred_industries: str | None = None
    preferred_locations: str | None = None
    career_goals: str | None = None
    professional_summary: str | None = None


class CareerSkillInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: str = Field(min_length=2, max_length=80)
    proficiency: str = Field(pattern="^(Beginner|Elementary|Intermediate|Advanced|Expert)$")
    learning_status: str = Field(default="Learning", pattern="^(Learning|Practising|Applied|Verified)$")
    experience_months: int = Field(default=0, ge=0, le=600)
    evidence: str | None = None
    verified: bool = False


class CareerProjectInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=10)
    problem_solved: str | None = None
    technologies: str | None = None
    category: str = "Personal"
    github_url: str | None = None
    live_demo_url: str | None = None
    contribution: str | None = None
    skills_demonstrated: str | None = None
    start_date: str | None = None
    completion_date: str | None = None


class CareerExperienceInput(BaseModel):
    kind: str = Field(pattern="^(Internship|Work|Hackathon|Competition|Award|Research)$")
    title: str = Field(min_length=2, max_length=160)
    organization: str = Field(min_length=2, max_length=160)
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class CareerCertificationInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    issuer: str = Field(min_length=2, max_length=160)
    issue_date: str | None = None
    credential_url: str | None = None


class CareerGoalInput(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    status: str = Field(default="Not Started", pattern="^(Not Started|In Progress|Completed)$")


class RoadmapStatusInput(BaseModel):
    status: str = Field(pattern="^(Not Started|In Progress|Completed)$")


class JobDescriptionInput(BaseModel):
    company: str = Field(min_length=2, max_length=180)
    title: str = Field(min_length=2, max_length=180)
    experience_level: str = Field(pattern="^(Entry|Junior|Mid|Senior|Lead)$")
    text: str = Field(min_length=30)


class ResumeConfirmInput(BaseModel):
    confirmed: bool


class PreparationStatusInput(BaseModel):
    status: str = Field(pattern="^(Not Started|In Progress|Completed)$")


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
