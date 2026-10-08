"""add address to shops

Revision ID: c6b1f28b006a
Revises: 5d00b4e114ab
Create Date: 2026-10-07 12:17:34.656592

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c6b1f28b006a"
down_revision: Union[str, None] = "5d00b4e114ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new shop fields
    op.add_column(
        "shops",
        sa.Column("address", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "shops",
        sa.Column("phone", sa.String(length=50), nullable=True),
    )

    # Existing shops need a value for this non-null column
    op.add_column(
        "shops",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # Remove the old database column
    op.drop_column("shops", "Active")

    # Remove server default after existing rows have been populated
    op.alter_column(
        "shops",
        "is_active",
        server_default=None,
    )


def downgrade() -> None:
    # Restore old column
    op.add_column(
        "shops",
        sa.Column(
            "Active",
            sa.Boolean(),
            nullable=True,
        ),
    )

    # Remove new columns
    op.drop_column("shops", "is_active")
    op.drop_column("shops", "phone")
    op.drop_column("shops", "address")