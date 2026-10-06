"""Concurrency invariant tests for the in-memory ticket store.

The FSM allows self-loops (e.g. reviewed -> reviewed), so a concurrent
duplicate "acquire" does not raise -- it is accepted as a no-op resubmission.
The invariant that actually matters here is race-free: ownership (user_id)
must never be corrupted or reassigned by a losing concurrent request, and
concurrent edits to distinct fields must not be lost.
"""

import asyncio

import pytest

from app.models import Category, Priority, Ticket, TicketState
from app.store import InvalidTransitionError, TicketStore


async def _make_pending_ticket(store: TicketStore, ticket_id: str = "concurrency-ticket") -> Ticket:
    ticket = Ticket(
        id=ticket_id,
        user_id=None,
        priority=Priority.MEDIUM,
        category=Category.OTHER,
        updated_text="draft",
        state=TicketState.PENDING,
    )
    return await store.add(ticket)


@pytest.mark.asyncio
async def test_concurrent_acquire_assigns_ownership_exactly_once() -> None:
    store = TicketStore()
    await _make_pending_ticket(store)

    results = await asyncio.gather(
        store.apply_update("concurrency-ticket", TicketState.REVIEWED, demo_user_id="agent-a"),
        store.apply_update("concurrency-ticket", TicketState.REVIEWED, demo_user_id="agent-b"),
    )

    # Both calls succeed (the second is a legal reviewed->reviewed self-loop),
    # but ownership must be assigned to exactly one of the two requesters and
    # never overwritten by the other, racing call.
    owners = {ticket.user_id for ticket in results}
    assert owners == {"agent-a"} or owners == {"agent-b"}

    final = (await store.list_all())[0]
    assert final.state == TicketState.REVIEWED
    assert final.user_id in {"agent-a", "agent-b"}


@pytest.mark.asyncio
async def test_concurrent_edits_to_distinct_fields_are_not_lost() -> None:
    store = TicketStore()
    ticket = await _make_pending_ticket(store)
    await store.apply_update(ticket.id, TicketState.REVIEWED, demo_user_id="agent-a")

    await asyncio.gather(
        store.apply_update(
            ticket.id, TicketState.REVIEWED, demo_user_id="agent-a", category=Category.BILLING
        ),
        store.apply_update(
            ticket.id, TicketState.REVIEWED, demo_user_id="agent-a", priority=Priority.HIGH
        ),
    )

    final = (await store.list_all())[0]
    assert final.category == Category.BILLING
    assert final.priority == Priority.HIGH
    assert final.state == TicketState.REVIEWED


@pytest.mark.asyncio
async def test_concurrent_illegal_transition_never_succeeds() -> None:
    store = TicketStore()
    await _make_pending_ticket(store)

    results = await asyncio.gather(
        store.apply_update("concurrency-ticket", TicketState.PROCESSING, demo_user_id="agent-a"),
        store.apply_update("concurrency-ticket", TicketState.PROCESSING, demo_user_id="agent-b"),
        return_exceptions=True,
    )

    # pending -> processing is never a legal single-step transition, regardless
    # of ordering, so both racing attempts must fail.
    assert all(isinstance(result, InvalidTransitionError) for result in results)

    final = (await store.list_all())[0]
    assert final.state == TicketState.PENDING
