"""add role column to users

Revision ID: db0394532b72
Revises: 7fcefd5c1ba6
Create Date: 2026-09-22 23:17:26.381621
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "db0394532b72"
down_revision: Union[str, None] = "7fcefd5c1ba6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="employee"
        )
    )


def downgrade() -> None:
    op.drop_column("users", "role")