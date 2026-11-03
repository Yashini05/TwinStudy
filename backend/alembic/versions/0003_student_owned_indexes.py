"""add ownership indexes used by ORM models"""
from alembic import op

revision = "0003_student_owned_indexes"
down_revision = "0002_career_twin"
branch_labels = None
depends_on = None


def upgrade():
    indexes = [
        ("ix_students_email", "students", ["email"], True),
        ("ix_subjects_student_id", "subjects", ["student_id"], False),
        ("ix_academic_records_student_id", "academic_records", ["student_id"], False),
        ("ix_academic_records_subject_id", "academic_records", ["subject_id"], False),
        ("ix_attendance_student_id", "attendance", ["student_id"], False),
        ("ix_attendance_subject_id", "attendance", ["subject_id"], False),
        ("ix_study_activities_student_id", "study_activities", ["student_id"], False),
        ("ix_academic_goals_student_id", "academic_goals", ["student_id"], False),
        ("ix_digital_twin_snapshots_student_id", "digital_twin_snapshots", ["student_id"], False),
        ("ix_career_profiles_student_id", "career_profiles", ["student_id"], True),
        ("ix_career_skills_student_id", "career_skills", ["student_id"], False),
        ("ix_career_projects_student_id", "career_projects", ["student_id"], False),
        ("ix_career_experiences_student_id", "career_experiences", ["student_id"], False),
        ("ix_career_certifications_student_id", "career_certifications", ["student_id"], False),
        ("ix_career_goals_student_id", "career_goals", ["student_id"], False),
        ("ix_career_roadmap_tasks_student_id", "career_roadmap_tasks", ["student_id"], False),
        ("ix_career_twin_snapshots_student_id", "career_twin_snapshots", ["student_id"], False),
    ]
    for name, table, columns, unique in indexes:
        op.create_index(name, table, columns, unique=unique)


def downgrade():
    for name in (
        "ix_career_twin_snapshots_student_id", "ix_career_roadmap_tasks_student_id",
        "ix_career_goals_student_id", "ix_career_certifications_student_id",
        "ix_career_experiences_student_id", "ix_career_projects_student_id",
        "ix_career_skills_student_id", "ix_career_profiles_student_id",
        "ix_digital_twin_snapshots_student_id", "ix_academic_goals_student_id",
        "ix_study_activities_student_id", "ix_attendance_subject_id",
        "ix_attendance_student_id", "ix_academic_records_subject_id",
        "ix_academic_records_student_id", "ix_subjects_student_id",
        "ix_students_email",
    ):
        op.drop_index(name)
