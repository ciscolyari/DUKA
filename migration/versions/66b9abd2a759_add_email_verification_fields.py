"""add email verification fields

Revision ID: 66b9abd2a759
Revises: 8f1d2a6c9e41
Create Date: 2026-10-07 15:55:26.237049
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "66b9abd2a759"
down_revision: Union[str, None] = "8f1d2a6c9e41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("verification_code", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("code_expires_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "code_expires_at")
    op.drop_column("users", "verification_code")