from app.extensions import db
from app.utils import utcnow


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.String(2000), nullable=False)
    is_internal = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    ticket = db.relationship("Ticket", backref="comments")
    author = db.relationship("User", backref="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "author_id": self.author_id,
            "body": self.body,
            "is_internal": self.is_internal,
            "attachments": [attachment.to_dict() for attachment in self.attachments],
            "created_at": self.created_at.isoformat(),
        }
