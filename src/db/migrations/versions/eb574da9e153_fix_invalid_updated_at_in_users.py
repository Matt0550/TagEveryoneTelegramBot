"""Fix invalid updated_at in users

Revision ID: eb574da9e153
Revises: 6f594bf49e19
Create Date: 2026-06-02 20:41:29.170292

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'eb574da9e153'
down_revision: str | Sequence[str] | None = '6f594bf49e19'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE users SET updated_at = NULL WHERE TYPEOF(updated_at) = 'integer' OR updated_at IN ('2023', '2024')")


def downgrade() -> None:
    """Downgrade schema."""
    pass
