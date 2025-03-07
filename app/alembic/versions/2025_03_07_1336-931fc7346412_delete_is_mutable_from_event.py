"""delete is_mutable from Event

Revision ID: 931fc7346412
Revises: 81f4fc90bc1c
Create Date: 2025-03-07 13:36:57.802286

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "931fc7346412"
down_revision: Union[str, None] = "81f4fc90bc1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("events", "is_mutable")


def downgrade() -> None:
    op.add_column(
        "events",
        sa.Column(
            "is_mutable",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
