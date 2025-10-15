"""добавлена модель для Яндекс токенов

Revision ID: 1607957a5438
Revises: 5a4959697631
Create Date: 2025-10-15 19:53:30.935212

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "1607957a5438"
down_revision: Union[str, None] = "5a4959697631"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "yandex_tokens",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_yandex_tokens")),
    )


def downgrade() -> None:
    op.drop_table("yandex_tokens")
