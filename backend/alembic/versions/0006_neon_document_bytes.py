"""store document bytes in PostgreSQL for free-tier deployment"""
from alembic import op
import sqlalchemy as sa

revision = "0006_neon_document_bytes"
down_revision = "0005_r2_document_storage"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("resume_documents", sa.Column("document_data", sa.LargeBinary(), nullable=True))
    op.add_column("job_descriptions", sa.Column("source_document_data", sa.LargeBinary(), nullable=True))


def downgrade():
    op.drop_column("job_descriptions", "source_document_data")
    op.drop_column("resume_documents", "document_data")
