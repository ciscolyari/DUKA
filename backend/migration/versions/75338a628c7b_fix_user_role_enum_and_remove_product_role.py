"""fix user role enum and remove product role

Revision ID: 75338a628c7b
Revises: ec2fc711f302
Create Date: 2026-09-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "75338a628c7b"
down_revision: Union[str, None] = "ec2fc711f302"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Create the PostgreSQL enum if it does not already exist.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'userrole'
            ) THEN
                CREATE TYPE userrole AS ENUM ('admin', 'employee');
            END IF;
        END
        $$;
    """)

    # Remove the old VARCHAR default.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role DROP DEFAULT
    """)

    # Convert users.role from VARCHAR to PostgreSQL ENUM.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE userrole
        USING role::text::userrole
    """)

    # Set the new ENUM default.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        SET DEFAULT 'employee'::userrole
    """)

    # Product does not have a role in the current model.
    op.drop_column("products", "role")


def downgrade() -> None:

    # Remove ENUM default.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role DROP DEFAULT
    """)

    # Convert ENUM back to VARCHAR.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
    """)

    # Restore the old VARCHAR default.
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        SET DEFAULT 'employee'
    """)

    # Restore products.role.
    op.add_column(
        "products",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="product"
        )
    )

    # Remove the ENUM type.
    op.execute("""
        DROP TYPE IF EXISTS userrole
    """)