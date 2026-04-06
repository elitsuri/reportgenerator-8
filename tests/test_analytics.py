import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_analytics_overview_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/analytics/overview")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_analytics_overview_returns_stats(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_items" in data
    assert "total_users" in data
    assert "total_notifications" in data
    assert "items_this_week" in data
    assert "active_users_today" in data
    assert isinstance(data["total_items"], int)

@pytest.mark.asyncio
async def test_analytics_timeseries_default_days(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/analytics/timeseries")
    assert response.status_code == 200
    data = response.json()
    assert "points" in data
    assert "total" in data
    assert isinstance(data["points"], list)

@pytest.mark.asyncio
async def test_analytics_timeseries_custom_days(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/analytics/timeseries?days=7")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_analytics_timeseries_invalid_days(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/analytics/timeseries?days=0")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_analytics_top_items(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/analytics/top-items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)