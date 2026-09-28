"""fix user role enum and remove product role

Revision ID: YOUR_REVISION_ID
Revises: ec2fc711f302
Create Date: 2026-09-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '75338a628c7b'
down_revision: Union[str, None] = "ec2fc711f302"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------------------------------
    # 1. Make sure the PostgreSQL enum type exists
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Convert users.role from VARCHAR to userrole ENUM
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role DROP DEFAULT
    """)

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE userrole
        USING role::text::userrole
    """)

    # ---------------------------------------------------------
    # 3. Set the correct default for users.role
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        SET DEFAULT 'employee'::userrole
    """)

    # ---------------------------------------------------------
    # 4. Remove the old Product role column
    # ---------------------------------------------------------
    op.drop_column("products", "role")


def downgrade() -> None:

    # ---------------------------------------------------------
    # 1. Remove ENUM default
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role DROP DEFAULT
    """)

    # ---------------------------------------------------------
    # 2. Convert ENUM back to VARCHAR
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
    """)

    # ---------------------------------------------------------
    # 3. Restore VARCHAR default
    # ---------------------------------------------------------
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        SET DEFAULT 'employee'
    """)

    # ---------------------------------------------------------
    # 4. Restore products.role
    # ---------------------------------------------------------
    op.add_column(
        "products",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="product"
        )
    )

    # ---------------------------------------------------------
    # 5. Remove ENUM type
    # ---------------------------------------------------------
    op.execute("""
        DROP TYPE IF EXISTS userrole
    """)