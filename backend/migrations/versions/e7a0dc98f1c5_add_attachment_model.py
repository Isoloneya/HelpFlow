from alembic import op
import sqlalchemy as sa


revision = "e7a0dc98f1c5"
down_revision = "c5d5dceeb18a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("attachments", sa.Column("id", sa.Integer(), nullable=False), sa.Column("ticket_id", sa.Integer(), nullable=False), sa.Column("uploader_id", sa.Integer(), nullable=False), sa.Column("filename", sa.String(length=255), nullable=False), sa.Column("storage_name", sa.String(length=255), nullable=False), sa.Column("content_type", sa.String(length=120), nullable=False), sa.Column("size", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]), sa.ForeignKeyConstraint(["uploader_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("storage_name"))


def downgrade():
    op.drop_table("attachments")
