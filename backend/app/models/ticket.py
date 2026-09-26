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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "category_id": self.category_id,
            "client_id": self.client_id,
            "assignee_id": self.assignee_id,
            "sla_deadline": self.sla_deadline.isoformat(),
            "sla_breached": self.sla_breached,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
