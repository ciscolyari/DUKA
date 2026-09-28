"""fix user role enum values

Revision ID: c6432b1932df
Revises: db0394532b72
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op


revision: str = "c6432b1932df"
down_revision: Union[str, None] = "db0394532b72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'ADMIN' TO 'admin'"
    )
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'EMPLOYEE' TO 'employee'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'admin' TO 'ADMIN'"
    )
    op.execute(
        "ALTER TYPE userrole RENAME VALUE 'employee' TO 'EMPLOYEE'"
    )