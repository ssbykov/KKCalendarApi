"""переименовал поле moon_day в moon_date в Event

Revision ID: bcb7d2c3ab2b
Revises: 5fb374ce5d4d
Create Date: 2025-10-17 14:52:28.264150

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "bcb7d2c3ab2b"
down_revision: Union[str, None] = "5fb374ce5d4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "events",
        "moon_day",
        new_column_name="moon_date",
        existing_type=sa.String(length=20),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "events",
        "moon_date",
        new_column_name="moon_day",
        existing_type=sa.String(length=20),
        existing_nullable=True,
    )
