"""
Domain models for ticket processing system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Category(str, Enum):
    """Allowed ticket categories."""
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    OTHER = "other"


class Priority(str, Enum):
    """Allowed ticket priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class State(str, Enum):
    """Allowed ticket states."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    PROCESSING = "processing"
    CLOSED = "closed"


@dataclass
class Ticket:
    """
    Domain model for a customer support ticket.
    
    Attributes:
        id: Unique identifier for the ticket
        user_id: ID of the agent currently assigned to the ticket
        priority: Ticket priority level
        category: Ticket category
        text: Original ticket text/description
        updated_text: AI-generated or agent-updated response text
        state: Current state in the ticket lifecycle
    """
    id: str
    user_id: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    category: Category = Category.OTHER
    text: str = ""
    updated_text: Optional[str] = None
    state: State = State.PENDING
