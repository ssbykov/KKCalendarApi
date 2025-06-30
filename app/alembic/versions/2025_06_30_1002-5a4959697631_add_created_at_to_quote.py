"""add created_at to Quote

Revision ID: 5a4959697631
Revises: bbdf554e9798
Create Date: 2025-06-30 10:02:07.000924

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "5a4959697631"
down_revision: Union[str, None] = "bbdf554e9798"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "quotes",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("quotes", "created_at")
