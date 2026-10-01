import enum

from app.extensions import db
from app.utils import utcnow


class TicketStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


ticket_participants = db.Table(
    "ticket_participants",
    db.Column("ticket_id", db.Integer, db.ForeignKey("tickets.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    status = db.Column(
        db.Enum(TicketStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TicketStatus.NEW,
        index=True,
    )
    priority = db.Column(
        db.Enum(TicketPriority, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TicketPriority.MEDIUM,
        index=True,
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False
    )
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assignee_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True, index=True
    )
    parent_ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=True)
    sla_deadline = db.Column(db.DateTime, nullable=False)
    sla_breached = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    category = db.relationship("Category", backref="tickets")
    client = db.relationship(
        "User", foreign_keys=[client_id], backref="tickets_created"
    )
    assignee = db.relationship(
        "User", foreign_keys=[assignee_id], backref="tickets_assigned"
    )
    parent_ticket = db.relationship("Ticket", remote_side=[id], backref="follow_up_tickets")
    operators = db.relationship("User", secondary=ticket_participants, backref="participating_tickets")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "category_id": self.category_id,
            "category_name": self.category.name,
            "client_id": self.client_id,
            "client_name": self.client.full_name,
            "client_email": self.client.email,
            "assignee_id": self.assignee_id,
            "assignee_email": self.assignee.email if self.assignee else None,
            "participant_ids": [operator.id for operator in self.operators],
            "participants": [
                {"id": operator.id, "full_name": operator.full_name, "email": operator.email}
                for operator in self.operators
            ],
            "parent_ticket_id": self.parent_ticket_id,
            "sla_deadline": self.sla_deadline.isoformat(),
            "sla_breached": self.sla_breached,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "attachments": [attachment.to_dict() for attachment in self.attachments if attachment.comment_id is None],
        }
