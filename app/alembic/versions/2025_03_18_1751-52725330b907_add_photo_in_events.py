"""add photo in events

Revision ID: 52725330b907
Revises: 93de3ea5b2c8
Create Date: 2025-03-18 17:51:03.885309

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "52725330b907"
down_revision: Union[str, None] = "93de3ea5b2c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("events", sa.Column("photo_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_events_photo_id_event_photos"),
        "events",
        "event_photos",
        ["photo_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_events_photo_id_event_photos"), "events", type_="foreignkey"
    )
    op.drop_column("events", "photo_id")
