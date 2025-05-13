"""add quotes, lamas

Revision ID: abf5e5232273
Revises: cce757ed2b4f
Create Date: 2025-05-13 19:42:33.378830

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abf5e5232273"
down_revision: Union[str, None] = "cce757ed2b4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lamas",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("photo_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["photo_id"],
            ["event_photos.id"],
            name=op.f("fk_lamas_photo_id_event_photos"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lamas")),
        sa.UniqueConstraint("name", name=op.f("uq_lamas_name")),
    )
    op.create_index(op.f("ix_lamas_id"), "lamas", ["id"], unique=True)
    op.create_table(
        "quotes",
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("lama_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["lama_id"], ["lamas.id"], name=op.f("fk_quotes_lama_id_lamas")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quotes")),
    )
    op.create_index(op.f("ix_quotes_id"), "quotes", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_quotes_id"), table_name="quotes")
    op.drop_table("quotes")
    op.drop_index(op.f("ix_lamas_id"), table_name="lamas")
    op.drop_table("lamas")
