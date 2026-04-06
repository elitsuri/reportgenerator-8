"""Items CRUD endpoint tests."""
import pytest

@pytest.mark.asyncio
async def test_list_items_empty(client, auth_headers):
    resp = await client.get("/api/v1/items", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["data"] == []

@pytest.mark.asyncio
async def test_create_item(client, auth_headers):
    resp = await client.post("/api/v1/items", json={"title": "Test Item", "description": "desc"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Item"
    assert data["status"] == "active"

@pytest.mark.asyncio
async def test_get_item(client, auth_headers):
    create = await client.post("/api/v1/items", json={"title": "My Item"}, headers=auth_headers)
    item_id = create.json()["id"]
    resp = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id

@pytest.mark.asyncio
async def test_update_item(client, auth_headers):
    create = await client.post("/api/v1/items", json={"title": "Old"}, headers=auth_headers)
    item_id = create.json()["id"]
    resp = await client.patch(f"/api/v1/items/{item_id}", json={"title": "Updated"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"

@pytest.mark.asyncio
async def test_delete_item(client, auth_headers):
    create = await client.post("/api/v1/items", json={"title": "To Delete"}, headers=auth_headers)
    item_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_items_require_auth(client):
    resp = await client.get("/api/v1/items")
    assert resp.status_code == 401