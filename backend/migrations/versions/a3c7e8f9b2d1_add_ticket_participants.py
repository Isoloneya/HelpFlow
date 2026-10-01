from alembic import op
import sqlalchemy as sa

revision = "a3c7e8f9b2d1"
down_revision = "f2b9d4a1c6e3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ticket_participants",
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("ticket_id", "user_id"),
    )
    op.execute("INSERT INTO ticket_participants (ticket_id, user_id) SELECT id, assignee_id FROM tickets WHERE assignee_id IS NOT NULL")


def downgrade():
    op.drop_table("ticket_participants")
