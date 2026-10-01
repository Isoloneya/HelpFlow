from alembic import op
import sqlalchemy as sa


revision = "c5d5dceeb18a"
down_revision = "991f8c700fa0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("full_name", sa.String(length=120), nullable=False, server_default="Користувач"))
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("is_active")
        batch_op.drop_column("full_name")
