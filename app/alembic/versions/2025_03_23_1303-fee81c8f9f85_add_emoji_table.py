"""add Emoji table

Revision ID: fee81c8f9f85
Revises: 59e2da6ffd0d
Create Date: 2025-03-23 13:03:37.977776

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fee81c8f9f85"
down_revision: Union[str, None] = "59e2da6ffd0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "emoji",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("emoji", sa.Unicode(length=10), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_emoji")),
        sa.UniqueConstraint("name", name=op.f("uq_emoji_name")),
    )
    op.create_index(op.f("ix_emoji_id"), "emoji", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_emoji_id"), table_name="emoji")
    op.drop_table("emoji")
