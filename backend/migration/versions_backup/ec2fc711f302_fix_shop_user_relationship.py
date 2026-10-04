"""fix shop user relationship

Revision ID: ec2fc711f302
Revises: 5d63e1f055d9
Create Date: 2026-09-25 16:53:28.278993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ec2fc711f302"
down_revision: Union[str, None] = "5d63e1f055d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Copy the existing shop relationship from shops.user_id
    # into users.shop_id.
    op.execute("""
        UPDATE users
        SET shop_id = shops.id
        FROM shops
        WHERE users.id = shops.user_id
          AND users.shop_id IS NULL
    """)

    # Remove the old foreign key.
    op.drop_constraint(
        "shops_user_id_fkey",
        "shops",
        type_="foreignkey"
    )

    # Remove the old relationship column.
    op.drop_column("shops", "user_id")

    # Add the new foreign key.
    op.create_foreign_key(
        "users_shop_id_fkey",
        "users",
        "shops",
        ["shop_id"],
        ["id"]
    )


def downgrade() -> None:
    # Add the old column back.
    op.add_column(
        "shops",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Restore the relationship where possible.
    op.execute("""
        UPDATE shops
        SET user_id = users.id
        FROM users
        WHERE users.shop_id = shops.id
    """)

    # Make the old column NOT NULL again.
    op.alter_column(
        "shops",
        "user_id",
        nullable=False
    )

    # Remove the new foreign key.
    op.drop_constraint(
        "users_shop_id_fkey",
        "users",
        type_="foreignkey"
    )

    # Restore the old foreign key.
    op.create_foreign_key(
        "shops_user_id_fkey",
        "shops",
        "users",
        ["user_id"],
        ["id"]
    )