"""Ticket state machine: single source of truth for legal transitions.

Allowed transitions (from specs/specs.md):
    pending -> reviewed
    reviewed -> processing
    processing -> closed
    pending -> pending
    reviewed -> reviewed
    processing -> processing
    closed -> closed
"""

from app.models import TicketState

ALLOWED_TRANSITIONS: dict[TicketState, frozenset[TicketState]] = {
    TicketState.PENDING: frozenset({TicketState.PENDING, TicketState.REVIEWED}),
    TicketState.REVIEWED: frozenset({TicketState.REVIEWED, TicketState.PROCESSING}),
    TicketState.PROCESSING: frozenset({TicketState.PROCESSING, TicketState.CLOSED}),
    TicketState.CLOSED: frozenset({TicketState.CLOSED}),
}


def is_transition_allowed(current: TicketState, target: TicketState) -> bool:
    """Return True if moving from current to target is a legal FSM transition."""
    return target in ALLOWED_TRANSITIONS[current]


def legal_next_states(current: TicketState) -> frozenset[TicketState]:
    """Return the set of states reachable in one step from current (including self-loop)."""
    return ALLOWED_TRANSITIONS[current]
