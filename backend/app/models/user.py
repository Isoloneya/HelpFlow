from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.utils import utcnow


class UserRole:
    CLIENT = "client"
    AGENT = "agent"
    ADMIN = "admin"

    ALL = (CLIENT, AGENT, ADMIN)
    STAFF = (AGENT, ADMIN)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.CLIENT)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }
