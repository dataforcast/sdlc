"""Unit tests for ticket creation service logic."""

import pytest

from app.models import TicketState
from app.service import create_ticket_from_text
from app.store import TicketStore


@pytest.mark.asyncio
async def test_create_ticket_from_text_yields_pending_unassigned_ticket() -> None:
    store = TicketStore()

    ticket = await create_ticket_from_text(store, "My invoice has an incorrect charge")

    assert ticket.state == TicketState.PENDING
    assert ticket.user_id is None
    assert ticket.updated_text.strip() != ""
    assert ticket.id in {t.id for t in await store.list_all()}
