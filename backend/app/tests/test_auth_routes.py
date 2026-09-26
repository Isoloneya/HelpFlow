import pytest


@pytest.fixture()
def http_client(app):
    return app.test_client()


def test_register_endpoint_creates_client(http_client):
    response = http_client.post(
        "/api/auth/register",
        json={"email": "route@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    assert response.get_json()["role"] == "client"


def test_register_endpoint_rejects_duplicate_email(http_client):
    payload = {"email": "dup2@example.com", "password": "password123"}
    http_client.post("/api/auth/register", json=payload)

    response = http_client.post("/api/auth/register", json=payload)

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "CONFLICT"


def test_register_endpoint_rejects_short_password(http_client):
    response = http_client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "password": "123"},
    )

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_register_endpoint_rejects_invalid_email(http_client):
    response = http_client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )

    assert response.status_code == 422


def test_login_endpoint_returns_token(http_client):
    payload = {"email": "loginroute@example.com", "password": "password123"}
    http_client.post("/api/auth/register", json=payload)

    response = http_client.post("/api/auth/login", json=payload)

    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert body["user"]["email"] == "loginroute@example.com"


def test_login_endpoint_rejects_wrong_password(http_client):
    payload = {"email": "wrongroute@example.com", "password": "password123"}
    http_client.post("/api/auth/register", json=payload)

    response = http_client.post(
        "/api/auth/login",
        json={"email": "wrongroute@example.com", "password": "incorrect"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_unknown_route_returns_json_404(http_client):
    response = http_client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"
