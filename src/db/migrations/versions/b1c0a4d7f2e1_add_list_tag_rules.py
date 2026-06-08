"""add_list_tag_rules

Revision ID: b1c0a4d7f2e1
Revises: a73b9f883308
Create Date: 2026-06-08 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "b1c0a4d7f2e1"
down_revision: Union[str, Sequence[str], None] = "a73b9f883308"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "list_tag_rules",
        sa.Column("list_id", sa.Uuid(), nullable=False),
        sa.Column("tag_value", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "mode",
            sa.Enum(
                "EXCLUDE",
                "INCLUDE_ONLY",
                "AUTO_ADD",
                "AUTO_REMOVE",
                name="listtagrulemode",
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["list_id"], ["tag_lists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("list_tag_rules", schema=None) as batch_op:
        batch_op.create_index(
            "ix_list_tag_rules_tag_value", ["tag_value"], unique=False
        )
        batch_op.create_index(
            "ix_list_tag_rules_list_active", ["list_id", "active"], unique=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("list_tag_rules", schema=None) as batch_op:
        batch_op.drop_index("ix_list_tag_rules_list_active")
        batch_op.drop_index("ix_list_tag_rules_tag_value")
    op.drop_table("list_tag_rules")
    sa.Enum(name="listtagrulemode").drop(op.get_bind(), checkfirst=True)
