"""Первая миграция

Revision ID: e4c6e943131d
Revises:
Create Date: 2025-02-14 20:05:29.226511

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4c6e943131d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "elements",
        sa.Column("en_name", sa.String(length=30), nullable=False),
        sa.Column("ru_name", sa.String(length=30), nullable=False),
        sa.Column("ru_text", sa.Text(), nullable=True),
        sa.Column("en_text", sa.Text(), nullable=True),
        sa.Column("is_positive", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_elements")),
        sa.UniqueConstraint("en_name", name=op.f("uq_elements_en_name")),
        sa.UniqueConstraint("ru_name", name=op.f("uq_elements_ru_name")),
    )
    op.create_index(op.f("ix_elements_id"), "elements", ["id"], unique=True)
    op.create_table(
        "events",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("moon_day", sa.String(length=10), nullable=True),
        sa.Column("en_name", sa.String(), nullable=False),
        sa.Column("ru_name", sa.String(), nullable=True),
        sa.Column("en_text", sa.Text(), nullable=True),
        sa.Column("ru_text", sa.Text(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("is_mutable", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=True)
    op.create_table(
        "haircutting_days",
        sa.Column("moon_day", sa.Integer(), nullable=False),
        sa.Column("en_name", sa.String(length=100), nullable=False),
        sa.Column("ru_name", sa.String(length=100), nullable=False),
        sa.Column("is_inauspicious", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_haircutting_days")),
        sa.UniqueConstraint("moon_day", name=op.f("uq_haircutting_days_moon_day")),
    )
    op.create_index(
        op.f("ix_haircutting_days_id"), "haircutting_days", ["id"], unique=True
    )
    op.create_table(
        "la_positions",
        sa.Column("moon_day", sa.Integer(), nullable=False),
        sa.Column("en_name", sa.String(length=100), nullable=False),
        sa.Column("ru_name", sa.String(length=100), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_la_positions")),
        sa.UniqueConstraint("moon_day", name=op.f("uq_la_positions_moon_day")),
    )
    op.create_index(op.f("ix_la_positions_id"), "la_positions", ["id"], unique=True)
    op.create_table(
        "skylight_arches",
        sa.Column("moon_day", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=10), nullable=False),
        sa.Column("en_desc", sa.String(length=100), nullable=False),
        sa.Column("ru_desc", sa.String(length=100), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skylight_arches")),
        sa.UniqueConstraint("moon_day", name=op.f("uq_skylight_arches_moon_day")),
    )
    op.create_index(
        op.f("ix_skylight_arches_id"), "skylight_arches", ["id"], unique=True
    )
    op.create_table(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=True)
    op.create_table(
        "yelam",
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("en_name", sa.String(length=30), nullable=False),
        sa.Column("ru_name", sa.String(length=30), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_yelam")),
        sa.UniqueConstraint("month", name=op.f("uq_yelam_month")),
    )
    op.create_index(op.f("ix_yelam_id"), "yelam", ["id"], unique=True)
    op.create_table(
        "day_info",
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("moon_day", sa.String(length=15), nullable=False),
        sa.Column("elements_id", sa.Integer(), nullable=False),
        sa.Column("arch_id", sa.Integer(), nullable=False),
        sa.Column("la_id", sa.Integer(), nullable=False),
        sa.Column("yelam_id", sa.Integer(), nullable=False),
        sa.Column("haircutting_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["arch_id"],
            ["skylight_arches.id"],
            name=op.f("fk_day_info_arch_id_skylight_arches"),
        ),
        sa.ForeignKeyConstraint(
            ["elements_id"],
            ["elements.id"],
            name=op.f("fk_day_info_elements_id_elements"),
        ),
        sa.ForeignKeyConstraint(
            ["haircutting_id"],
            ["haircutting_days.id"],
            name=op.f("fk_day_info_haircutting_id_haircutting_days"),
        ),
        sa.ForeignKeyConstraint(
            ["la_id"],
            ["la_positions.id"],
            name=op.f("fk_day_info_la_id_la_positions"),
        ),
        sa.ForeignKeyConstraint(
            ["yelam_id"], ["yelam.id"], name=op.f("fk_day_info_yelam_id_yelam")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_day_info")),
        sa.UniqueConstraint("date", name=op.f("uq_day_info_date")),
    )
    op.create_index(op.f("ix_day_info_id"), "day_info", ["id"], unique=True)
    op.create_table(
        "dayinfo_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("day_info_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["day_info_id"],
            ["day_info.id"],
            name=op.f("fk_dayinfo_events_day_info_id_day_info"),
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            name=op.f("fk_dayinfo_events_event_id_events"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dayinfo_events")),
    )


def downgrade() -> None:
    op.drop_table("dayinfo_events")
    op.drop_index(op.f("ix_day_info_id"), table_name="day_info")
    op.drop_table("day_info")
    op.drop_index(op.f("ix_yelam_id"), table_name="yelam")
    op.drop_table("yelam")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_skylight_arches_id"), table_name="skylight_arches")
    op.drop_table("skylight_arches")
    op.drop_index(op.f("ix_la_positions_id"), table_name="la_positions")
    op.drop_table("la_positions")
    op.drop_index(op.f("ix_haircutting_days_id"), table_name="haircutting_days")
    op.drop_table("haircutting_days")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")
    op.drop_index(op.f("ix_elements_id"), table_name="elements")
    op.drop_table("elements")
