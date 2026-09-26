import pytest

from app.services import auth_service
from app.models import User, UserRole
from app.errors import ConflictError, UnauthorizedError


def test_register_client_creates_user_with_client_role(db):
    user = auth_service.register_client("new@example.com", "password123")

    assert user.id is not None
    assert user.role == UserRole.CLIENT
    assert user.check_password("password123")


def test_register_client_rejects_duplicate_email(db):
    auth_service.register_client("dup@example.com", "password123")

    with pytest.raises(ConflictError):
        auth_service.register_client("dup@example.com", "password456")


def test_authenticate_returns_user_and_token(db):
    auth_service.register_client("login@example.com", "password123")

    user, token = auth_service.authenticate("login@example.com", "password123")

    assert user.email == "login@example.com"
    assert isinstance(token, str) and len(token) > 0


def test_authenticate_rejects_wrong_password(db):
    auth_service.register_client("wrong@example.com", "password123")

    with pytest.raises(UnauthorizedError):
        auth_service.authenticate("wrong@example.com", "incorrect")


def test_authenticate_rejects_unknown_email(db):
    with pytest.raises(UnauthorizedError):
        auth_service.authenticate("ghost@example.com", "password123")
