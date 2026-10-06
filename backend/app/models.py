"""Pydantic domain models and API request/response contracts."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class TicketState(str, Enum):
    """Allowed ticket lifecycle states (see app.fsm for legal transitions)."""

    PENDING = "pending"
    REVIEWED = "reviewed"
    PROCESSING = "processing"
    CLOSED = "closed"


class Ticket(BaseModel):
    """A support ticket. Used both as the internal record and the API response_model."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str
    user_id: str | None = Field(default=None, description="User in charge of processing")
    priority: Priority
    category: Category
    updated_text: str = Field(description="AI-drafted (and optionally agent-edited) answer")
    state: TicketState


class TriageRequest(BaseModel):
    """Raw free-text support request submitted for classification and drafting."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticket_text: str = Field(min_length=1, max_length=4000)

    @field_validator("ticket_text", mode="before")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ticket_text must not be blank")
        return value


class FilterRequest(BaseModel):
    """Optional attribute filters, AND-combined."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: Category | None = None
    priority: Priority | None = None
    state: TicketState | None = None
    user_id: str | None = None


class UpdateRequest(BaseModel):
    """Submit a ticket with its target state and optional edited fields.

    No user_id field: the acting identity is never client-supplied.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticket_id: str
    target_state: TicketState
    category: Category | None = None
    priority: Priority | None = None
    updated_text: str | None = Field(default=None, max_length=4000)


class TicketListResponse(BaseModel):
    """List payload returned by /tickets and /filter."""

    model_config = ConfigDict(extra="forbid")

    tickets: list[Ticket]


class HealthResponse(BaseModel):
    """Health check payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["ok"]
