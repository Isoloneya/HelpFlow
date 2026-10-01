from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import User
from app.errors import UnauthorizedError


def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedError("Користувача не знайдено")
    return user
