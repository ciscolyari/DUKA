"""add note to sales

Revision ID: 8f1d2a6c9e41
Revises: c6b1f28b006a
Create Date: 2026-10-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f1d2a6c9e41"
down_revision: Union[str, None] = "c6b1f28b006a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sales", sa.Column("note", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("sales", "note")
