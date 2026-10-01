from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.utils import utcnow


class UserRole:
    CLIENT = "client"
    AGENT = "agent"
    ADMIN = "admin"

    ALL = (CLIENT, AGENT, ADMIN)
    STAFF = (AGENT, ADMIN)


agent_categories = db.Table(
    "agent_categories",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False, default="Користувач")
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.CLIENT)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    categories = db.relationship("Category", secondary=agent_categories, backref="agents")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "category_ids": [category.id for category in self.categories],
            "active_ticket_count": sum(
                1 for ticket in self.tickets_assigned if ticket.status.value in ("new", "in_progress")
            ),
            "created_at": self.created_at.isoformat(),
        }
