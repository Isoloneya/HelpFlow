import pytest

from app.models import User, UserRole, Category
from app.extensions import db as _db


@pytest.fixture()
def http_client(app):
    return app.test_client()


def _register_and_login(http_client, email, password, role=None):
    http_client.post("/api/auth/register", json={"email": email, "password": password})
    if role:
        user = User.query.filter_by(email=email).first()
        user.role = role
        _db.session.commit()

    response = http_client.post("/api/auth/login", json={"email": email, "password": password})
    return response.get_json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def client_token(http_client):
    return _register_and_login(http_client, "commclient@example.com", "password123")


@pytest.fixture()
def agent_token(http_client):
    return _register_and_login(http_client, "commagent@example.com", "password123", UserRole.AGENT)


@pytest.fixture()
def category(db):
    cat = Category(name="Категорія коментарів", sla_hours=24)
    db.session.add(cat)
    db.session.commit()
    return cat


@pytest.fixture()
def ticket(http_client, client_token, agent_token, category):
    response = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    )
    return response.get_json()


def test_client_can_post_public_comment(http_client, client_token, ticket):
    response = http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Питання від клієнта"},
        headers=_auth_header(client_token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["is_internal"] is False


def test_client_cannot_post_internal_comment(http_client, client_token, ticket):
    response = http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Спроба", "is_internal": True},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 403


def test_agent_can_post_internal_comment(http_client, agent_token, ticket):
    response = http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Внутрішня нотатка", "is_internal": True},
        headers=_auth_header(agent_token),
    )

    assert response.status_code == 201
    assert response.get_json()["is_internal"] is True


def test_client_does_not_see_internal_comments(http_client, client_token, agent_token, ticket):
    http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Публічне"},
        headers=_auth_header(client_token),
    )
    http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Внутрішнє", "is_internal": True},
        headers=_auth_header(agent_token),
    )

    response = http_client.get(
        f"/api/tickets/{ticket['id']}/comments", headers=_auth_header(client_token)
    )

    body = response.get_json()
    assert len(body) == 1
    assert body[0]["is_internal"] is False


def test_agent_sees_all_comments(http_client, client_token, agent_token, ticket):
    http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Публічне"},
        headers=_auth_header(client_token),
    )
    http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Внутрішнє", "is_internal": True},
        headers=_auth_header(agent_token),
    )

    response = http_client.get(
        f"/api/tickets/{ticket['id']}/comments", headers=_auth_header(agent_token)
    )

    assert len(response.get_json()) == 2


def test_other_client_cannot_comment_on_foreign_ticket(http_client, client_token, ticket):
    other_token = _register_and_login(http_client, "otherclient@example.com", "password123")

    response = http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": "Чужий тікет"},
        headers=_auth_header(other_token),
    )
    assert response.status_code == 403


def test_comment_on_missing_ticket_returns_404(http_client, client_token):
    response = http_client.post(
        "/api/tickets/999/comments",
        json={"body": "Немає тікета"},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 404


def test_empty_body_rejected(http_client, client_token, ticket):
    response = http_client.post(
        f"/api/tickets/{ticket['id']}/comments",
        json={"body": ""},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 422
