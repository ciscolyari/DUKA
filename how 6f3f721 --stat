"""fix user role enum and remove product role"""
"""add expenses table"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ec2fc711f302"
down_revision: Union[str, None] = "a1b25283bc14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create userrole enum if it does not already exist
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

    # Remove default from users.role before changing its type
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role DROP DEFAULT
    """)

    # Change users.role to userrole enum
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE userrole
        USING role::text::userrole
    """)

    # Set default employee
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role SET DEFAULT 'employee'::userrole
    """)

    # Remove products.role only if it exists
    op.execute("""
        ALTER TABLE products
        DROP COLUMN IF EXISTS role
    """)


def downgrade() -> None:
    # Restore products.role only if needed
    op.add_column(
        "products",
        sa.Column(
            "role",
            sa.String(),
            nullable=True,
        ),
    )

    # Remove default from users.role
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role DROP DEFAULT
    """)

    # Change users.role back to VARCHAR
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
    """)

    # Drop userrole enum
    op.execute("""
        DROP TYPE IF EXISTS userrole
    """)