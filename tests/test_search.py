import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_search_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/search/?q=test")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_search_all_empty_results(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/search/?q=zzznomatch")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "users" in data
    assert len(data["items"]) == 0

@pytest.mark.asyncio
async def test_search_items_only(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/search/?q=sample&type=items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "users" in data
    assert data["users"] == []

@pytest.mark.asyncio
async def test_search_users_only(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/search/?q=admin&type=users")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []

@pytest.mark.asyncio
async def test_search_missing_q(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/search/")
    assert response.status_code == 422