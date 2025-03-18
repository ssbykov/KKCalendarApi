"""add photos table

Revision ID: 93de3ea5b2c8
Revises: f3f7c2b96924
Create Date: 2025-03-17 15:02:18.822331

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "93de3ea5b2c8"
down_revision: Union[str, None] = "f3f7c2b96924"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_photos",
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column(
            "photo_data",
            ImageType(),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event_photos")),
    )
    op.create_index(op.f("ix_event_photos_id"), "event_photos", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_event_photos_id"), table_name="event_photos")
    op.drop_table("event_photos")
