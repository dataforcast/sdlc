"""Unit tests for the ticket FSM transition rules."""

import pytest

from app.fsm import is_transition_allowed, legal_next_states
from app.models import TicketState


@pytest.mark.parametrize(
    "current,target",
    [
        (TicketState.PENDING, TicketState.REVIEWED),
        (TicketState.REVIEWED, TicketState.PROCESSING),
        (TicketState.PROCESSING, TicketState.CLOSED),
        (TicketState.PENDING, TicketState.PENDING),
        (TicketState.REVIEWED, TicketState.REVIEWED),
        (TicketState.PROCESSING, TicketState.PROCESSING),
        (TicketState.CLOSED, TicketState.CLOSED),
    ],
)
def test_allowed_transitions(current: TicketState, target: TicketState) -> None:
    assert is_transition_allowed(current, target) is True


@pytest.mark.parametrize(
    "current,target",
    [
        (TicketState.PENDING, TicketState.PROCESSING),
        (TicketState.PENDING, TicketState.CLOSED),
        (TicketState.REVIEWED, TicketState.PENDING),
        (TicketState.REVIEWED, TicketState.CLOSED),
        (TicketState.PROCESSING, TicketState.PENDING),
        (TicketState.PROCESSING, TicketState.REVIEWED),
        (TicketState.CLOSED, TicketState.PENDING),
        (TicketState.CLOSED, TicketState.REVIEWED),
        (TicketState.CLOSED, TicketState.PROCESSING),
    ],
)
def test_illegal_transitions(current: TicketState, target: TicketState) -> None:
    assert is_transition_allowed(current, target) is False


def test_closed_is_terminal() -> None:
    assert legal_next_states(TicketState.CLOSED) == frozenset({TicketState.CLOSED})
