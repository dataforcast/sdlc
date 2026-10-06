"""Business logic shared by the /triage endpoint and startup demo seeding."""

from uuid import uuid4

from app.mock_ai import classify_and_draft
from app.models import Ticket, TicketState
from app.store import TicketStore


async def create_ticket_from_text(store: TicketStore, ticket_text: str) -> Ticket:
    """Classify and draft an answer for raw ticket text, then persist a new pending ticket."""
    result = classify_and_draft(ticket_text)
    ticket = Ticket(
        id=str(uuid4()),
        user_id=None,
        priority=result.priority,
        category=result.category,
        updated_text=result.draft_text,
        state=TicketState.PENDING,
    )
    return await store.add(ticket)
