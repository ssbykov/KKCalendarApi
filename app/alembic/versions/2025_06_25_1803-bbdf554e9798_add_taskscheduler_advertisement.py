"""add TaskScheduler, Advertisement

Revision ID: bbdf554e9798
Revises: 7c5ce713dc3a
Create Date: 2025-06-25 18:03:33.392962

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.custom_types import ImageType


# revision identifiers, used by Alembic.
revision: str = "bbdf554e9798"
down_revision: Union[str, None] = "7c5ce713dc3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "advertisements",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("image_id", sa.Integer(), nullable=True),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("ids", sa.JSON(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["image_id"],
            ["event_photos.id"],
            name=op.f("fk_advertisements_image_id_event_photos"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_advertisements")),
    )
    op.create_index(op.f("ix_advertisements_id"), "advertisements", ["id"], unique=True)
    op.create_table(
        "task_schedulers",
        sa.Column("advertisement_id", sa.Integer(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column(
            "days",
            sa.String(length=50),
            nullable=False,
            comment="Comma-separated list of weekdays",
        ),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "hour >= 0 AND hour <= 23",
            name=op.f("ck_task_schedulers_check_hour_range"),
        ),
        sa.CheckConstraint(
            "minute >= 0 AND minute <= 59",
            name=op.f("ck_task_schedulers_check_minute_range"),
        ),
        sa.ForeignKeyConstraint(
            ["advertisement_id"],
            ["advertisements.id"],
            name=op.f("fk_task_schedulers_advertisement_id_advertisements"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_schedulers")),
    )
    op.create_index(
        op.f("ix_task_schedulers_id"), "task_schedulers", ["id"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_task_schedulers_id"), table_name="task_schedulers")
    op.drop_table("task_schedulers")
    op.drop_index(op.f("ix_advertisements_id"), table_name="advertisements")
    op.drop_table("advertisements")
