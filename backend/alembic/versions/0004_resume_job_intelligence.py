"""add resume and job intelligence tables"""
from alembic import op
import sqlalchemy as sa

revision = "0004_resume_job_intelligence"
down_revision = "0003_student_owned_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "resume_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("stored_name", sa.String(255), nullable=False, unique=True),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("extracted_json", sa.Text(), nullable=False),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_resume_documents_student_id", "resume_documents", ["student_id"])
    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company", sa.String(180), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("experience_level", sa.String(40), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("extracted_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_job_descriptions_student_id", "job_descriptions", ["student_id"])
    op.create_table(
        "job_comparisons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_job_comparisons_student_id", "job_comparisons", ["student_id"])
    op.create_index("ix_job_comparisons_job_id", "job_comparisons", ["job_id"])
    op.create_table(
        "job_preparation_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="Not Started"),
    )
    op.create_index("ix_job_preparation_tasks_student_id", "job_preparation_tasks", ["student_id"])
    op.create_index("ix_job_preparation_tasks_job_id", "job_preparation_tasks", ["job_id"])


def downgrade():
    for name in ("job_preparation_tasks", "job_comparisons", "job_descriptions", "resume_documents"):
        op.drop_table(name)
