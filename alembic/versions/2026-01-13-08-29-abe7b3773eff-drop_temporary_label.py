"""drop_temporary_label

Revision ID: abe7b3773eff
Revises: f71a73e20503
Create Date: 2026-01-13 08:29:33.538576

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "abe7b3773eff"
down_revision = "f71a73e20503"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("practice", "temporary_label")


def downgrade():
    op.add_column("practice", sa.Column("temporary_label", sa.String(length=120), nullable=True))
