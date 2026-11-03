"""add durable document storage metadata"""
from alembic import op
import sqlalchemy as sa

revision = "0005_r2_document_storage"
down_revision = "0004_resume_job_intelligence"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("resume_documents", sa.Column("storage_backend", sa.String(20), nullable=False, server_default="local"))
    op.add_column("job_descriptions", sa.Column("source_original_name", sa.String(255), nullable=True))
    op.add_column("job_descriptions", sa.Column("source_content_type", sa.String(120), nullable=True))
    op.add_column("job_descriptions", sa.Column("source_object_key", sa.String(500), nullable=True))
    op.add_column("job_descriptions", sa.Column("source_storage_backend", sa.String(20), nullable=True))


def downgrade():
    for column in ("source_storage_backend", "source_object_key", "source_content_type", "source_original_name"):
        op.drop_column("job_descriptions", column)
    op.drop_column("resume_documents", "storage_backend")
