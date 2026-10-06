"""add subscription fields to shops

Revision ID: 1eb282623f07
Revises: 75338a628c7b
Create Date: 2026-10-05 17:02:09.300404
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "1eb282623f07"
down_revision: Union[str, None] = "75338a628c7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add subscription start date
    op.add_column(
        "shops",
        sa.Column(
            "subscription_starts_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Add subscription expiry date
    op.add_column(
        "shops",
        sa.Column(
            "subscription_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Add payment reference
    op.add_column(
        "shops",
        sa.Column(
            "last_payment_ref",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # Add subscription status
    # Existing shops will automatically receive ACTIVE
    op.add_column(
        "shops",
        sa.Column(
            "subscription_status",
            sa.Enum(
                "ACTIVE",
                "EXPIRED",
                "CANCELLED",
                name="subscriptionstatus",
            ),
            nullable=False,
            server_default="ACTIVE",
        ),
    )


def downgrade() -> None:
    # Remove subscription status
    op.drop_column(
        "shops",
        "subscription_status",
    )

    # Remove payment reference
    op.drop_column(
        "shops",
        "last_payment_ref",
    )

    # Remove subscription expiry date
    op.drop_column(
        "shops",
        "subscription_expires_at",
    )

    # Remo
    op.drop_column(
        "shops",
        "subscription_starts_at",
    )