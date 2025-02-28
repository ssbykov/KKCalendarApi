"""Добавил ограничение nullable=False на поле ru_name

Revision ID: 81f4fc90bc1c
Revises: 089ed445d058
Create Date: 2025-02-27 19:46:45.517042

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81f4fc90bc1c"
down_revision: Union[str, None] = "089ed445d058"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("events", "ru_name", existing_type=sa.VARCHAR(), nullable=False)


def downgrade() -> None:
    op.alter_column("events", "ru_name", existing_type=sa.VARCHAR(), nullable=True)
