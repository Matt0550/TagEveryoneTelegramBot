"""Fix invalid created_at in users

Revision ID: 6f594bf49e19
Revises: 4b7c4bc23142
Create Date: 2026-06-02 20:37:18.324721

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6f594bf49e19'
down_revision: str | Sequence[str] | None = '4b7c4bc23142'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE users SET created_at = '2023-01-01 00:00:00' WHERE TYPEOF(created_at) = 'integer' OR created_at = '2023'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
