import pytest

from app.models import User, UserRole
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
def admin_token(http_client):
    return _register_and_login(http_client, "catadmin@example.com", "password123", UserRole.ADMIN)


@pytest.fixture()
def client_token(http_client):
    return _register_and_login(http_client, "catclient@example.com", "password123")


def test_admin_can_create_category(http_client, admin_token):
    response = http_client.post(
        "/api/categories",
        json={"name": "Білінг", "sla_hours": 8},
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 201
    assert response.get_json()["sla_hours"] == 8


def test_client_cannot_create_category(http_client, client_token):
    response = http_client.post(
        "/api/categories",
        json={"name": "Білінг", "sla_hours": 8},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 403


def test_duplicate_category_name_rejected(http_client, admin_token):
    payload = {"name": "Доступ", "sla_hours": 4}
    http_client.post("/api/categories", json=payload, headers=_auth_header(admin_token))
    response = http_client.post("/api/categories", json=payload, headers=_auth_header(admin_token))
    assert response.status_code == 409


def test_any_authenticated_user_can_list_categories(http_client, admin_token, client_token):
    http_client.post(
        "/api/categories",
        json={"name": "Технічна підтримка", "sla_hours": 24},
        headers=_auth_header(admin_token),
    )
    response = http_client.get("/api/categories", headers=_auth_header(client_token))
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_admin_can_update_category(http_client, admin_token):
    created = http_client.post(
        "/api/categories",
        json={"name": "Стара назва", "sla_hours": 12},
        headers=_auth_header(admin_token),
    ).get_json()

    response = http_client.patch(
        f"/api/categories/{created['id']}",
        json={"sla_hours": 6},
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 200
    assert response.get_json()["sla_hours"] == 6


def test_delete_category_without_tickets_removes_it(http_client, admin_token):
    created = http_client.post(
        "/api/categories",
        json={"name": "Без тікетів", "sla_hours": 10},
        headers=_auth_header(admin_token),
    ).get_json()

    response = http_client.delete(
        f"/api/categories/{created['id']}", headers=_auth_header(admin_token)
    )
    assert response.status_code == 204


def test_delete_category_with_active_tickets_archives_it(http_client, admin_token, client_token):
    category = http_client.post(
        "/api/categories",
        json={"name": "Активна категорія", "sla_hours": 10},
        headers=_auth_header(admin_token),
    ).get_json()

    agent_token = _register_and_login(
        http_client, "catagent@example.com", "password123", UserRole.AGENT
    )

    http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category["id"]},
        headers=_auth_header(client_token),
    )

    response = http_client.delete(
        f"/api/categories/{category['id']}", headers=_auth_header(admin_token)
    )
    assert response.status_code == 200
    assert response.get_json()["is_archived"] is True


def test_delete_category_with_resolved_ticket_archives_it(http_client, admin_token, client_token):
    category = http_client.post(
        "/api/categories",
        json={"name": "Архівна категорія", "sla_hours": 10},
        headers=_auth_header(admin_token),
    ).get_json()
    agent_token = _register_and_login(
        http_client, "resolvedagent@example.com", "password123", UserRole.AGENT
    )
    ticket = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category["id"]},
        headers=_auth_header(client_token),
    ).get_json()
    http_client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "resolved"},
        headers=_auth_header(agent_token),
    )

    response = http_client.delete(
        f"/api/categories/{category['id']}", headers=_auth_header(admin_token)
    )

    assert response.status_code == 200
    assert response.get_json()["is_archived"] is True
