"""set length of moon_day 20

Revision ID: 693f7172067e
Revises: 123cdb2c99b4
Create Date: 2025-03-23 11:53:07.958522

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "693f7172067e"
down_revision: Union[str, None] = "123cdb2c99b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "events",
        "moon_day",
        existing_type=sa.VARCHAR(length=10),
        type_=sa.String(length=20),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "events",
        "moon_day",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=10),
        existing_nullable=True,
    )
