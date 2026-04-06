import io
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_image_success(auth_client: AsyncClient, tmp_path):
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    files = {"file": ("test.png", io.BytesIO(content), "image/png")}
    response = await auth_client.post("/api/v1/upload/file", files=files)
    assert response.status_code == 201
    data = response.json()
    assert "url" in data
    assert "filename" in data
    assert "size" in data

@pytest.mark.asyncio
async def test_upload_bad_content_type(auth_client: AsyncClient):
    content = b"<script>alert(1)</script>"
    files = {"file": ("evil.html", io.BytesIO(content), "text/html")}
    response = await auth_client.post("/api/v1/upload/file", files=files)
    assert response.status_code == 415

@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient):
    content = b"data"
    files = {"file": ("file.txt", io.BytesIO(content), "text/plain")}
    response = await client.post("/api/v1/upload/file", files=files)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_upload_file_too_large(auth_client: AsyncClient):
    big_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("big.txt", io.BytesIO(big_content), "text/plain")}
    response = await auth_client.post("/api/v1/upload/file", files=files)
    assert response.status_code == 413

@pytest.mark.asyncio
async def test_upload_pdf(auth_client: AsyncClient):
    content = b"%PDF-1.4 test content"
    files = {"file": ("doc.pdf", io.BytesIO(content), "application/pdf")}
    response = await auth_client.post("/api/v1/upload/file", files=files)
    assert response.status_code == 201