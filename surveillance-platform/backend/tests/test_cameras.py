"""Tests for camera management endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_camera(client: AsyncClient, auth_headers: dict):
    """Test camera creation."""
    response = await client.post(
        "/api/v1/cameras",
        json={
            "name": "Test Camera",
            "source_type": "file",
            "source_reference": "test_video.mp4",
            "location_label": "Test Location",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Camera"
    assert data["source_type"] == "file"
    assert data["status"] == "OFFLINE"


@pytest.mark.asyncio
async def test_list_cameras(client: AsyncClient, auth_headers: dict):
    """Test listing cameras."""
    # Create a camera first
    await client.post(
        "/api/v1/cameras",
        json={
            "name": "List Test Camera",
            "source_type": "file",
            "source_reference": "test.mp4",
        },
        headers=auth_headers,
    )
    response = await client.get("/api/v1/cameras", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_camera(client: AsyncClient, auth_headers: dict):
    """Test getting a specific camera."""
    create_resp = await client.post(
        "/api/v1/cameras",
        json={
            "name": "Get Test Camera",
            "source_type": "file",
            "source_reference": "test.mp4",
        },
        headers=auth_headers,
    )
    camera_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/cameras/{camera_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Get Test Camera"


@pytest.mark.asyncio
async def test_update_camera(client: AsyncClient, auth_headers: dict):
    """Test camera update."""
    create_resp = await client.post(
        "/api/v1/cameras",
        json={
            "name": "Update Test Camera",
            "source_type": "file",
            "source_reference": "test.mp4",
        },
        headers=auth_headers,
    )
    camera_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/cameras/{camera_id}",
        json={"name": "Updated Camera Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Camera Name"


@pytest.mark.asyncio
async def test_delete_camera(client: AsyncClient, auth_headers: dict):
    """Test camera deletion."""
    create_resp = await client.post(
        "/api/v1/cameras",
        json={
            "name": "Delete Test Camera",
            "source_type": "file",
            "source_reference": "test.mp4",
        },
        headers=auth_headers,
    )
    camera_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/cameras/{camera_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(f"/api/v1/cameras/{camera_id}", headers=auth_headers)
    assert get_resp.status_code == 404
