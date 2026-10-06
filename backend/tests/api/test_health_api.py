"""Backend API test: health endpoint against a running server."""

import os

import httpx2 as httpx
import pytest

BASE_URL = f"http://{os.environ.get('BACKEND_HOST', '127.0.0.1')}:{os.environ.get('BACKEND_PORT', '8010')}"


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/backend/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
