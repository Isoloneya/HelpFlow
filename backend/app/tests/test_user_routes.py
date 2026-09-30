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
    return _register_and_login(http_client, "useradmin@example.com", "password123", UserRole.ADMIN)


@pytest.fixture()
def client_token(http_client):
    return _register_and_login(http_client, "userclient@example.com", "password123")


def test_admin_can_create_agent(http_client, admin_token):
    response = http_client.post(
        "/api/users",
        json={"email": "newagent@example.com"},
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["role"] == "agent"
    assert "temporary_password" in body
    assert len(body["temporary_password"]) >= 8


def test_client_cannot_create_agent(http_client, client_token):
    response = http_client.post(
        "/api/users",
        json={"email": "shouldfail@example.com"},
        headers=_auth_header(client_token),
    )
    assert response.status_code == 403


def test_created_agent_can_login_with_temp_password(http_client, admin_token):
    created = http_client.post(
        "/api/users",
        json={"email": "loginagent@example.com"},
        headers=_auth_header(admin_token),
    ).get_json()

    response = http_client.post(
        "/api/auth/login",
        json={"email": "loginagent@example.com", "password": created["temporary_password"]},
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "agent"


def test_duplicate_agent_email_rejected(http_client, admin_token):
    payload = {"email": "dupagent@example.com"}
    http_client.post("/api/users", json=payload, headers=_auth_header(admin_token))
    response = http_client.post("/api/users", json=payload, headers=_auth_header(admin_token))
    assert response.status_code == 409


def test_admin_can_list_staff(http_client, admin_token):
    http_client.post(
        "/api/users", json={"email": "staffmember@example.com"}, headers=_auth_header(admin_token)
    )

    response = http_client.get("/api/users", headers=_auth_header(admin_token))
    assert response.status_code == 200
    emails = [u["email"] for u in response.get_json()]
    assert "staffmember@example.com" in emails
    assert "useradmin@example.com" in emails


def test_client_cannot_list_staff(http_client, client_token):
    response = http_client.get("/api/users", headers=_auth_header(client_token))
    assert response.status_code == 403


def test_admin_can_change_user_role(http_client, admin_token):
    created = http_client.post(
        "/api/users", json={"email": "promote@example.com"}, headers=_auth_header(admin_token)
    ).get_json()

    response = http_client.patch(
        f"/api/users/{created['id']}",
        json={"role": "admin"},
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"


def test_update_role_rejects_invalid_value(http_client, admin_token):
    created = http_client.post(
        "/api/users", json={"email": "invalidrole@example.com"}, headers=_auth_header(admin_token)
    ).get_json()

    response = http_client.patch(
        f"/api/users/{created['id']}",
        json={"role": "superadmin"},
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 422
