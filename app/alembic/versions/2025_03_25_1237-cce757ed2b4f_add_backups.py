"""add backups

Revision ID: cce757ed2b4f
Revises: 574096789a3e
Create Date: 2025-03-25 12:37:54.446869

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cce757ed2b4f"
down_revision: Union[str, None] = "574096789a3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "backups",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_backups")),
        sa.UniqueConstraint("name", name=op.f("uq_backups_name")),
    )
    op.create_index(op.f("ix_backups_id"), "backups", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_backups_id"), table_name="backups")
    op.drop_table("backups")
