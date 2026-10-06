"""
Finite State Machine (FSM) implementation for ticket state transitions.

This module implements the ticket state machine with the following allowed transitions:
- pending -> reviewed
- reviewed -> processing  
- processing -> closed
- All states can self-transition (pending->pending, reviewed->reviewed, etc.)
- closed -> closed only (terminal state)
"""

from enum import Enum
from typing import Dict, Set

from backend.app.core.models.ticket import State


# Allowed transitions mapping
ALLOWED_TRANSITIONS: Dict[State, Set[State]] = {
    State.PENDING: {State.PENDING, State.REVIEWED},
    State.REVIEWED: {State.REVIEWED, State.PROCESSING},
    State.PROCESSING: {State.PROCESSING, State.CLOSED},
    State.CLOSED: {State.CLOSED},
}


def validate_transition(current_state: State, new_state: State) -> bool:
    """
    Validate if a transition from current_state to new_state is allowed.
    
    Args:
        current_state: The current state of the ticket
        new_state: The desired new state
        
    Returns:
        True if the transition is valid, False otherwise
    """
    return new_state in ALLOWED_TRANSITIONS.get(current_state, set())


def get_allowed_transitions(state: State) -> Set[State]:
    """
    Get all allowed transitions from a given state.
    
    Args:
        state: The current state
        
    Returns:
        Set of states that can be transitioned to
    """
    return ALLOWED_TRANSITIONS.get(state, set())
