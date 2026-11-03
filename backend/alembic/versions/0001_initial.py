"""create academic digital twin tables

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("year", sa.String(40)), sa.Column("department", sa.String(120)),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("subjects", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False), sa.Column("code", sa.String(30)),
        sa.UniqueConstraint("student_id", "name"))
    op.create_table("academic_records", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assessment", sa.String(120), nullable=False), sa.Column("score", sa.Float(), nullable=False),
        sa.Column("max_score", sa.Float(), nullable=False), sa.Column("recorded_at", sa.DateTime(), nullable=False))
    op.create_table("attendance", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attended", sa.Integer(), nullable=False), sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False))
    op.create_table("study_activities", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.String(10), nullable=False), sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("topic", sa.String(120)))
    op.create_table("learning_preferences", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("style", sa.String(60), nullable=False), sa.Column("preferred_time", sa.String(60)))
    op.create_table("academic_goals", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(180), nullable=False), sa.Column("target_score", sa.Float()),
        sa.Column("due_date", sa.String(10)), sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table("digital_twin_snapshots", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("state_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade():
    for table in ("digital_twin_snapshots", "academic_goals", "learning_preferences", "study_activities",
                  "attendance", "academic_records", "subjects", "students"):
        op.drop_table(table)
