"""add language to group_settings

Revision ID: c2f4a1b8d9e7
Revises: b1c0a4d7f2e1
Create Date: 2026-06-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c2f4a1b8d9e7"
down_revision: Union[str, Sequence[str], None] = "b1c0a4d7f2e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("group_settings", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "language",
                sa.String(length=8),
                nullable=False,
                server_default="en",
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("group_settings", schema=None) as batch_op:
        batch_op.drop_column("language")
