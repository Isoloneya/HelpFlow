import io

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
    return _register_and_login(http_client, "client@example.com", "password123")


@pytest.fixture()
def agent_token(http_client):
    return _register_and_login(http_client, "agent@example.com", "password123", UserRole.AGENT)


@pytest.fixture()
def category(db):
    cat = Category(name="Технічна підтримка", sla_hours=24)
    db.session.add(cat)
    db.session.commit()
    for agent in User.query.filter_by(role=UserRole.AGENT).all():
        agent.categories.append(cat)
    db.session.commit()
    return cat


def test_create_ticket_requires_auth(http_client, category):
    response = http_client.post(
        "/api/tickets",
        json={"title": "T", "description": "D", "category_id": category.id},
    )
    assert response.status_code == 401


def test_client_can_create_ticket(http_client, client_token, agent_token, category):
    response = http_client.post(
        "/api/tickets",
        json={"title": "Проблема з логіном", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] == "new"
    assert body["assignee_id"] is not None


def test_client_can_create_ticket_with_attachment(http_client, client_token, agent_token, category, app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    response = http_client.post(
        "/api/tickets",
        data={
            "title": "Файл у зверненні",
            "description": "Опис",
            "category_id": str(category.id),
            "priority": "high",
            "files": (io.BytesIO(b"test attachment"), "details.txt"),
        },
        headers=_auth_header(client_token),
    )

    assert response.status_code == 201
    attachment = response.get_json()["attachments"][0]
    download = http_client.get(
        f"/api/tickets/{response.get_json()['id']}/attachments/{attachment['id']}",
        headers=_auth_header(client_token),
    )
    assert download.status_code == 200
    assert download.data == b"test attachment"


def test_agent_cannot_create_ticket(http_client, agent_token, category):
    response = http_client.post(
        "/api/tickets",
        json={"title": "T", "description": "D", "category_id": category.id},
        headers=_auth_header(agent_token),
    )
    assert response.status_code == 403


def test_client_sees_only_own_tickets(http_client, client_token, agent_token, category):
    http_client.post(
        "/api/tickets",
        json={"title": "Моє", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    )

    other_token = _register_and_login(http_client, "other@example.com", "password123")

    response = http_client.get("/api/tickets", headers=_auth_header(other_token))

    assert response.status_code == 200
    assert response.get_json() == []


def test_client_cannot_view_others_ticket(http_client, client_token, agent_token, category):
    created = http_client.post(
        "/api/tickets",
        json={"title": "Приватне", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    other_token = _register_and_login(http_client, "other2@example.com", "password123")

    response = http_client.get(
        f"/api/tickets/{created['id']}", headers=_auth_header(other_token)
    )

    assert response.status_code == 403


def test_get_ticket_not_found(http_client, client_token):
    response = http_client.get("/api/tickets/999", headers=_auth_header(client_token))
    assert response.status_code == 404


def test_client_cannot_update_ticket(http_client, client_token, agent_token, category):
    created = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    response = http_client.patch(
        f"/api/tickets/{created['id']}",
        json={"status": "in_progress"},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 403


def test_client_can_close_own_ticket(http_client, client_token, agent_token, category):
    created = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    response = http_client.patch(
        f"/api/tickets/{created['id']}",
        json={"status": "closed"},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "closed"


def test_assigned_agent_can_update_status(http_client, client_token, agent_token, category):
    created = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    response = http_client.patch(
        f"/api/tickets/{created['id']}",
        json={"status": "in_progress", "priority": "high"},
        headers=_auth_header(agent_token),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"


def test_other_agent_cannot_update_ticket(http_client, client_token, agent_token, category):
    created = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    other_agent_token = _register_and_login(
        http_client, "otheragent@example.com", "password123", UserRole.AGENT
    )

    response = http_client.patch(
        f"/api/tickets/{created['id']}",
        json={"status": "in_progress"},
        headers=_auth_header(other_agent_token),
    )
    assert response.status_code == 403


def test_update_rejects_invalid_status(http_client, client_token, agent_token, category):
    created = http_client.post(
        "/api/tickets",
        json={"title": "Тікет", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    response = http_client.patch(
        f"/api/tickets/{created['id']}",
        json={"status": "not_a_real_status"},
        headers=_auth_header(agent_token),
    )
    assert response.status_code == 422
