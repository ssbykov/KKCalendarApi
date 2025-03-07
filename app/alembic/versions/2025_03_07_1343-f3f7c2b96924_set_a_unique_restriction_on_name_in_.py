"""set a unique restriction on name in Event

Revision ID: f3f7c2b96924
Revises: 931fc7346412
Create Date: 2025-03-07 13:43:38.170788

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3f7c2b96924"
down_revision: Union[str, None] = "931fc7346412"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(op.f("uq_events_name"), "events", ["name"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_events_name"), "events", type_="unique")
