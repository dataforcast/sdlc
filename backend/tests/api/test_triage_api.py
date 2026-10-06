"""Backend API test: ticket creation via /triage against a running server."""

import os

import httpx2 as httpx
import pytest

BASE_URL = f"http://{os.environ.get('BACKEND_HOST', '127.0.0.1')}:{os.environ.get('BACKEND_PORT', '8010')}"


@pytest.mark.asyncio
async def test_triage_creates_pending_ticket() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/backend/api/triage",
            json={"ticket_text": "My invoice shows an incorrect charge, please help"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "pending"
    assert payload["user_id"] is None
    assert payload["category"] == "billing"
    assert payload["updated_text"].strip() != ""


@pytest.mark.asyncio
async def test_triage_rejects_blank_text() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/backend/api/triage", json={"ticket_text": "   "})

    assert response.status_code == 422
