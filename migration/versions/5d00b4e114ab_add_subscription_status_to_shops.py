"""add subscription status to shops

Revision ID: 5d00b4e114ab
Revises: 5035c6e4aa75
Create Date: 2026-10-06 17:12:42.995217
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d00b4e114ab"
down_revision: Union[str, None] = "5035c6e4aa75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "shops",
        sa.Column(
            "subscription_status",
            sa.String(length=50),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "shops",
        "subscription_status",
    )