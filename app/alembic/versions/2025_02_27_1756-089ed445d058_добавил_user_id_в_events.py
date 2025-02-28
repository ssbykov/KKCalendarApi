"""Добавил user_id в Events

Revision ID: 089ed445d058
Revises: 71274dc64fdd
Create Date: 2025-02-27 17:56:46.181888

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "089ed445d058"
down_revision: Union[str, None] = "71274dc64fdd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("events", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_events_user_id_users"), "events", "users", ["user_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_events_user_id_users"), "events", type_="foreignkey")
    op.drop_column("events", "user_id")
