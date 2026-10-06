"""In-memory ticket persistence with an atomic check->mutate->commit invariant.

A single store-wide asyncio.Lock guards every mutation. At this scale (a
~20-ticket demo store, a handful of concurrent demo agents) a per-ticket lock
dict would introduce its own race (lock creation under concurrent /triage
calls) for no measurable concurrency benefit, so a single lock is the
simplest primitive that keeps check -> mutate -> commit atomic.
"""

import asyncio

from app.fsm import is_transition_allowed
from app.models import Category, Priority, Ticket, TicketState


class TicketNotFoundError(Exception):
    """Raised when an operation references an unknown ticket id."""


class InvalidTransitionError(Exception):
    """Raised when a requested state transition is not allowed by the FSM."""


class TicketStore:
    """Thread-safe (asyncio) in-memory collection of tickets."""

    def __init__(self) -> None:
        self._tickets: dict[str, Ticket] = {}
        self._lock = asyncio.Lock()

    async def add(self, ticket: Ticket) -> Ticket:
        async with self._lock:
            self._tickets[ticket.id] = ticket
            return ticket.model_copy()

    async def list_all(self) -> list[Ticket]:
        async with self._lock:
            return [ticket.model_copy() for ticket in self._tickets.values()]

    async def filter(
        self,
        category: Category | None = None,
        priority: Priority | None = None,
        state: TicketState | None = None,
        user_id: str | None = None,
    ) -> list[Ticket]:
        async with self._lock:
            tickets = [ticket.model_copy() for ticket in self._tickets.values()]

        def matches(ticket: Ticket) -> bool:
            if category is not None and ticket.category != category:
                return False
            if priority is not None and ticket.priority != priority:
                return False
            if state is not None and ticket.state != state:
                return False
            if user_id is not None and ticket.user_id != user_id:
                return False
            return True

        return [ticket for ticket in tickets if matches(ticket)]

    async def apply_update(
        self,
        ticket_id: str,
        target_state: TicketState,
        demo_user_id: str,
        category: Category | None = None,
        priority: Priority | None = None,
        updated_text: str | None = None,
    ) -> Ticket:
        """Validate and apply a state transition plus optional field edits atomically.

        Auto-assigns demo_user_id to the ticket when the transition being
        committed is pending -> reviewed ("acquire"); the client never
        supplies user_id directly.
        """
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if ticket is None:
                raise TicketNotFoundError(ticket_id)

            if not is_transition_allowed(ticket.state, target_state):
                raise InvalidTransitionError(
                    f"Cannot transition ticket {ticket_id} from "
                    f"{ticket.state.value} to {target_state.value}"
                )

            if ticket.state == TicketState.PENDING and target_state == TicketState.REVIEWED:
                ticket.user_id = demo_user_id

            if category is not None:
                ticket.category = category
            if priority is not None:
                ticket.priority = priority
            if updated_text is not None:
                ticket.updated_text = updated_text

            ticket.state = target_state

            return ticket.model_copy()
