"""add shop_id to users

Revision ID: 5d63e1f055d9
Revises: 35019d9b9177
Create Date: 2026-09-25 14:58:44.245103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d63e1f055d9"
down_revision: Union[str, None] = "35019d9b9177"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("shop_id", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "shop_id")