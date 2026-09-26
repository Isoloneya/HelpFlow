from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User, UserRole
from app.errors import ConflictError, UnauthorizedError


def register_client(email, password):
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise ConflictError("Користувач із таким email вже існує")

    user = User(email=email, role=UserRole.CLIENT)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise UnauthorizedError("Невірний email або пароль")

    token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    return user, token
