from app.extensions import db
from app.utils import utcnow


class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    storage_name = db.Column(db.String(255), nullable=False, unique=True)
    content_type = db.Column(db.String(120), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    ticket = db.relationship("Ticket", backref="attachments")
    comment = db.relationship("Comment", backref="attachments")
    uploader = db.relationship("User", backref="attachments")

    def to_dict(self):
        return {"id": self.id, "filename": self.filename, "content_type": self.content_type, "size": self.size, "created_at": self.created_at.isoformat()}
