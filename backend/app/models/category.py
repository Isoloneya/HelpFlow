from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sla_hours = db.Column(db.Integer, nullable=False)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)

    def has_active_tickets(self):
        from app.models.ticket import Ticket, TicketStatus

        active_statuses = (TicketStatus.NEW, TicketStatus.IN_PROGRESS)
        return (
            Ticket.query.filter(
                Ticket.category_id == self.id,
                Ticket.status.in_(active_statuses),
            ).count()
            > 0
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sla_hours": self.sla_hours,
            "is_archived": self.is_archived,
        }
