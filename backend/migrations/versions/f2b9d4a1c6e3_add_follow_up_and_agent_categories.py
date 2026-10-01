from alembic import op
import sqlalchemy as sa

revision = "f2b9d4a1c6e3"
down_revision = "e7a0dc98f1c5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "agent_categories",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "category_id"),
    )
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(sa.Column("parent_ticket_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_tickets_parent_ticket", "tickets", ["parent_ticket_id"], ["id"])
    with op.batch_alter_table("attachments") as batch_op:
        batch_op.add_column(sa.Column("comment_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_attachments_comment", "comments", ["comment_id"], ["id"])


def downgrade():
    with op.batch_alter_table("attachments") as batch_op:
        batch_op.drop_constraint("fk_attachments_comment", type_="foreignkey")
        batch_op.drop_column("comment_id")
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_constraint("fk_tickets_parent_ticket", type_="foreignkey")
        batch_op.drop_column("parent_ticket_id")
    op.drop_table("agent_categories")
