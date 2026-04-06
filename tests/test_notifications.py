import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_notifications_empty(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/notifications/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "unread_count" in data
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_create_notification(auth_client: AsyncClient):
    payload = {"title": "Test", "body": "Test body", "type": "info"}
    response = await auth_client.post("/api/v1/notifications/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
    assert data["read"] is False
    return data["id"]

@pytest.mark.asyncio
async def test_mark_notification_read(auth_client: AsyncClient):
    payload = {"title": "Mark Read Test", "body": "Body", "type": "info"}
    create_resp = await auth_client.post("/api/v1/notifications/", json=payload)
    notif_id = create_resp.json()["id"]
    response = await auth_client.post(f"/api/v1/notifications/{notif_id}/read")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_mark_all_notifications_read(auth_client: AsyncClient):
    for i in range(3):
        await auth_client.post("/api/v1/notifications/", json={"title": f"N{i}", "body": "B", "type": "info"})
    response = await auth_client.post("/api/v1/notifications/read-all")
    assert response.status_code == 204
    list_resp = await auth_client.get("/api/v1/notifications/")
    assert list_resp.json()["unread_count"] == 0

@pytest.mark.asyncio
async def test_delete_notification(auth_client: AsyncClient):
    payload = {"title": "Delete Me", "body": "Body", "type": "warning"}
    create_resp = await auth_client.post("/api/v1/notifications/", json=payload)
    notif_id = create_resp.json()["id"]
    response = await auth_client.delete(f"/api/v1/notifications/{notif_id}")
    assert response.status_code == 204