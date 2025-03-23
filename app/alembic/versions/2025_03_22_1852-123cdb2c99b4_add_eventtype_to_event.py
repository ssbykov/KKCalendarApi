"""add EventType to Event

Revision ID: 123cdb2c99b4
Revises: 78b9bbff9824
Create Date: 2025-03-22 18:52:33.572273

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "123cdb2c99b4"
down_revision: Union[str, None] = "78b9bbff9824"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("events", sa.Column("type_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_events_type_id_event_types"),
        "events",
        "event_types",
        ["type_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_events_type_id_event_types"), "events", type_="foreignkey"
    )
    op.drop_column("events", "type_id")
