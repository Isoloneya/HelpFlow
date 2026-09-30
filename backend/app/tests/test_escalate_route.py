from datetime import timedelta

import pytest

from app.models import User, UserRole, Category, Ticket, TicketStatus, TicketPriority
from app.extensions import db as _db
from app.utils import utcnow


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
    return _register_and_login(http_client, "escadmin@example.com", "password123", UserRole.ADMIN)


@pytest.fixture()
def client_token(http_client):
    return _register_and_login(http_client, "escclientroute@example.com", "password123")


def test_client_cannot_trigger_escalation(http_client, client_token):
    response = http_client.post("/api/tickets/escalate", headers=_auth_header(client_token))
    assert response.status_code == 403


def test_admin_can_trigger_escalation(http_client, admin_token, client_token):
    agent_token = _register_and_login(
        http_client, "escagentroute@example.com", "password123", UserRole.AGENT
    )
    category = Category(name="Ескалація роут", sla_hours=1)
    _db.session.add(category)
    _db.session.commit()

    created = http_client.post(
        "/api/tickets",
        json={"title": "Прострочене", "description": "Опис", "category_id": category.id},
        headers=_auth_header(client_token),
    ).get_json()

    ticket = _db.session.get(Ticket, created["id"])
    ticket.sla_deadline = utcnow() - timedelta(minutes=1)
    _db.session.commit()

    response = http_client.post("/api/tickets/escalate", headers=_auth_header(admin_token))

    assert response.status_code == 200
    body = response.get_json()
    assert body["escalated_to_urgent"] == 1

    updated = http_client.get(
        f"/api/tickets/{created['id']}", headers=_auth_header(admin_token)
    ).get_json()
    assert updated["priority"] == "urgent"
    assert updated["sla_breached"] is True
