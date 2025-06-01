"""add EventType

Revision ID: 78b9bbff9824
Revises: 52725330b907
Create Date: 2025-03-22 18:23:36.169759

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "78b9bbff9824"
down_revision: Union[str, None] = "52725330b907"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_types",
        sa.Column("ru_name", sa.String(length=30), nullable=False),
        sa.Column("ru_desc", sa.String(length=100), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event_types")),
        sa.UniqueConstraint("ru_name", name=op.f("uq_event_types_ru_name")),
    )
    op.create_index(op.f("ix_event_types_id"), "event_types", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_event_types_id"), table_name="event_types")
    op.drop_table("event_types")
