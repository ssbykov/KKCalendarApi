"""изменена настройка DateTime в YandexToken

Revision ID: 5fb374ce5d4d
Revises: 1607957a5438
Create Date: 2025-10-15 21:56:58.722745

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5fb374ce5d4d"
down_revision: Union[str, None] = "1607957a5438"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "yandex_tokens",
        "expires_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "yandex_tokens",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "yandex_tokens",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    op.alter_column(
        "yandex_tokens",
        "expires_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
