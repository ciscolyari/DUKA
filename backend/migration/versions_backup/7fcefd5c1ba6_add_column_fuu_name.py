"""add column fuu_name

Revision ID: 7fcefd5c1ba6
Revises: 8a624e9b7588
Create Date: 2026-09-22 21:42:35.194365
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7fcefd5c1ba6"
down_revision: Union[str, None] = "8a624e9b7588"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("fuu_name", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "fuu_name")