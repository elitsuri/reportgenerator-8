import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_list_users_forbidden_for_regular(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/admin/users")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_list_users(admin_client: AsyncClient):
    response = await admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    user = data[0]
    assert "id" in user
    assert "email" in user
    assert "role" in user

@pytest.mark.asyncio
async def test_admin_update_role(admin_client: AsyncClient, test_user_id: int):
    response = await admin_client.put(
        f"/api/v1/admin/users/{test_user_id}/role",
        json={"role": "moderator"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "moderator"

@pytest.mark.asyncio
async def test_admin_update_role_invalid(admin_client: AsyncClient, test_user_id: int):
    response = await admin_client.put(
        f"/api/v1/admin/users/{test_user_id}/role",
        json={"role": "superuser"},
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_admin_stats(admin_client: AsyncClient):
    response = await admin_client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_items" in data