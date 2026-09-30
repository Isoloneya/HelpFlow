import secrets

from app.extensions import db
from app.models import User, UserRole
from app.errors import NotFoundError, ConflictError


def create_agent(email):
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise ConflictError("Користувач із таким email вже існує")

    temp_password = secrets.token_urlsafe(9)

    user = User(email=email, role=UserRole.AGENT)
    user.set_password(temp_password)
    db.session.add(user)
    db.session.commit()
    return user, temp_password


def list_staff():
    return (
        User.query.filter(User.role.in_(UserRole.STAFF))
        .order_by(User.created_at)
        .all()
    )


def update_user_role(user_id, role):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("Користувача не знайдено")

    user.role = role
    db.session.commit()
    return user
