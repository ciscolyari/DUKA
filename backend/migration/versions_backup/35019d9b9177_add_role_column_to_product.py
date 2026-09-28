"""add role column to product

Revision ID: 35019d9b9177
Revises: c6432b1932df
Create Date: 2026-09-24 10:58:19.864443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "35019d9b9177"
down_revision: Union[str, None] = "c6432b1932df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="product",
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "role")