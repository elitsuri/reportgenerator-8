"""Authentication endpoint tests."""
import pytest

@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "full_name": "New User",
        "password": "Password123!",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_register_duplicate(client, test_user):
    resp = await client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "full_name": "Dup",
        "password": "Password123!",
    })
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_login(client, test_user):
    resp = await client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "Password123!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    resp = await client.post("/api/v1/auth/login", data={
        "username": test_user.email,
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401