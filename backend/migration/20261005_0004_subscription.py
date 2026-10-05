# alembic/versions/20261005_0004_subscription.py
from alembic import op
import sqlalchemy as sa

revision = "20261005_0004"
down_revision = "20261003_0003"


def upgrade():
    op.add_column("shops", sa.Column(
        "subscription_plan",
        sa.Enum("trial", "basic", "standard", "premium", name="subscriptionplan"),
        nullable=False,
        server_default="trial",
    ))
    op.add_column("shops", sa.Column(
        "subscription_status",
        sa.Enum("active", "expired", "cancelled", name="subscriptionstatus"),
        nullable=False,
        server_default="active",
    ))
    op.add_column("shops", sa.Column("subscription_starts_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("shops", sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("shops", sa.Column("last_payment_ref", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("shops", "last_payment_ref")
    op.drop_column("shops", "subscription_expires_at")
    op.drop_column("shops", "subscription_starts_at")
    op.drop_column("shops", "subscription_status")
    op.drop_column("shops", "subscription_plan")