"""add career digital twin tables"""
from alembic import op
import sqlalchemy as sa

revision = "0002_career_twin"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    fk = lambda: sa.ForeignKey("students.id", ondelete="CASCADE")
    op.create_table("career_profiles", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), fk(), nullable=False, unique=True),
        sa.Column("degree", sa.String(160)), sa.Column("department", sa.String(160)), sa.Column("institution", sa.String(180)),
        sa.Column("graduation_year", sa.Integer()), sa.Column("career_interests", sa.Text()), sa.Column("target_role", sa.String(160)),
        sa.Column("preferred_industries", sa.Text()), sa.Column("preferred_locations", sa.Text()), sa.Column("career_goals", sa.Text()),
        sa.Column("professional_summary", sa.Text()), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("career_skills", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False), sa.Column("category", sa.String(80), nullable=False), sa.Column("proficiency", sa.String(30), nullable=False),
        sa.Column("learning_status", sa.String(30), nullable=False), sa.Column("experience_months", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.Text()), sa.Column("verified", sa.Boolean(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("career_projects", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("name", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("problem_solved", sa.Text()),
        sa.Column("technologies", sa.Text()), sa.Column("category", sa.String(80), nullable=False), sa.Column("github_url", sa.String(300)),
        sa.Column("live_demo_url", sa.String(300)), sa.Column("contribution", sa.Text()), sa.Column("skills_demonstrated", sa.Text()),
        sa.Column("start_date", sa.String(10)), sa.Column("completion_date", sa.String(10)), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("career_experiences", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("organization", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()), sa.Column("start_date", sa.String(10)), sa.Column("end_date", sa.String(10)))
    op.create_table("career_certifications", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("name", sa.String(160), nullable=False), sa.Column("issuer", sa.String(160), nullable=False), sa.Column("issue_date", sa.String(10)),
        sa.Column("credential_url", sa.String(300)))
    op.create_table("career_goals", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("title", sa.String(180), nullable=False), sa.Column("status", sa.String(30), nullable=False))
    op.create_table("career_roadmap_tasks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("phase", sa.String(40), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False))
    op.create_table("career_twin_snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), fk(), nullable=False),
        sa.Column("state_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade():
    for table in ("career_twin_snapshots", "career_roadmap_tasks", "career_goals", "career_certifications",
                  "career_experiences", "career_projects", "career_skills", "career_profiles"):
        op.drop_table(table)
