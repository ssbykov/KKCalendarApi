"""renamed the fields in the table EventType

Revision ID: 59e2da6ffd0d
Revises: 693f7172067e
Create Date: 2025-03-23 12:24:46.128072

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59e2da6ffd0d"
down_revision: Union[str, None] = "693f7172067e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("event_types", "ru_name", new_column_name="name")
    op.alter_column("event_types", "ru_desc", new_column_name="desc")
    op.drop_constraint("uq_event_types_ru_name", "event_types", type_="unique")
    op.create_unique_constraint(op.f("uq_event_types_name"), "event_types", ["name"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_event_types_name"), "event_types", type_="unique")
    op.create_unique_constraint("uq_event_types_ru_name", "event_types", ["name"])
    op.alter_column("event_types", "name", new_column_name="ru_name")
    op.alter_column("event_types", "desc", new_column_name="ru_desc")
