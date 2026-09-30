"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@test.com",
            "password": "securepass123",
            "role": "OPERATOR",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["role"] == "OPERATOR"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "pass123456"},
    )
    # Duplicate
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "pass123456"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login returns tokens."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "pass123456"},
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "pass123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, auth_headers: dict):
    """Test getting current user with valid token."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test-admin@test.com"
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test getting current user without token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No credentials provided
