"""add unique=True in Lama.photo_id

Revision ID: 7c5ce713dc3a
Revises: abf5e5232273
Create Date: 2025-05-13 20:43:35.040264

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c5ce713dc3a"
down_revision: Union[str, None] = "abf5e5232273"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(op.f("uq_lamas_photo_id"), "lamas", ["photo_id"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_lamas_photo_id"), "lamas", type_="unique")
