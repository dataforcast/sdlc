"""Backend API test: full list -> filter -> acquire -> update lifecycle."""

import os

import httpx2 as httpx
import pytest

BASE_URL = f"http://{os.environ.get('BACKEND_HOST', '127.0.0.1')}:{os.environ.get('BACKEND_PORT', '8010')}"
DEMO_USER_ID = os.environ.get("DEMO_USER_ID", "agent-1")


@pytest.mark.asyncio
async def test_tickets_list_returns_twenty_seeded_tickets() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/backend/api/tickets")

    assert response.status_code == 200
    tickets = response.json()["tickets"]
    assert len(tickets) == 20


@pytest.mark.asyncio
async def test_filter_by_state_returns_only_pending_at_start() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/backend/api/filter", json={"state": "pending"})

    assert response.status_code == 200
    tickets = response.json()["tickets"]
    assert len(tickets) >= 1
    assert all(ticket["state"] == "pending" for ticket in tickets)


@pytest.mark.asyncio
async def test_full_lifecycle_pending_to_closed() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        created = await client.post(
            "/backend/api/triage",
            json={"ticket_text": "The export feature keeps crashing, this is urgent"},
        )
        ticket_id = created.json()["id"]

        acquired = await client.post(
            "/backend/api/update",
            json={"ticket_id": ticket_id, "target_state": "reviewed"},
        )
        assert acquired.status_code == 200
        assert acquired.json()["state"] == "reviewed"
        assert acquired.json()["user_id"] == DEMO_USER_ID

        reacquired = await client.post(
            "/backend/api/update",
            json={"ticket_id": ticket_id, "target_state": "reviewed"},
        )
        assert reacquired.status_code == 200
        assert reacquired.json()["user_id"] == DEMO_USER_ID

        processing = await client.post(
            "/backend/api/update",
            json={
                "ticket_id": ticket_id,
                "target_state": "processing",
                "updated_text": "Edited final answer",
            },
        )
        assert processing.status_code == 200
        assert processing.json()["state"] == "processing"
        assert processing.json()["updated_text"] == "Edited final answer"

        closed = await client.post(
            "/backend/api/update",
            json={"ticket_id": ticket_id, "target_state": "closed"},
        )
        assert closed.status_code == 200
        assert closed.json()["state"] == "closed"

        illegal_reopen = await client.post(
            "/backend/api/update",
            json={"ticket_id": ticket_id, "target_state": "pending"},
        )
        assert illegal_reopen.status_code == 409


@pytest.mark.asyncio
async def test_update_unknown_ticket_returns_404() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/backend/api/update",
            json={"ticket_id": "does-not-exist", "target_state": "reviewed"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_illegal_direct_jump_returns_409() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        created = await client.post(
            "/backend/api/triage",
            json={"ticket_text": "General question about account settings"},
        )
        ticket_id = created.json()["id"]

        response = await client.post(
            "/backend/api/update",
            json={"ticket_id": ticket_id, "target_state": "processing"},
        )

    assert response.status_code == 409
