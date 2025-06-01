"""add Emoji relationship to Event

Revision ID: 574096789a3e
Revises: fee81c8f9f85
Create Date: 2025-03-23 13:27:39.229287

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "574096789a3e"
down_revision: Union[str, None] = "fee81c8f9f85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("events", sa.Column("emoji_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_events_emoji_id_emoji"),
        "events",
        "emoji",
        ["emoji_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_events_emoji_id_emoji"), "events", type_="foreignkey")
    op.drop_column("events", "emoji_id")
