"""
Pydantic response models for API endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional

from backend.app.core.models.ticket import Category, Priority, State


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    version: str


class TicketResponse(BaseModel):
    """
    Response model for a single ticket.
    
    This is the API representation of a ticket, converted from the domain model.
    """
    id: str
    user_id: Optional[str] = None
    priority: Priority
    category: Category
    text: str
    updated_text: Optional[str] = None
    state: State

    @classmethod
    def from_domain(cls, ticket: "Ticket") -> "TicketResponse":
        """
        Convert domain Ticket model to API response model.
        
        Args:
            ticket: Domain Ticket instance
            
        Returns:
            TicketResponse instance
        """
        from backend.app.core.models.ticket import Ticket
        return cls(
            id=ticket.id,
            user_id=ticket.user_id,
            priority=ticket.priority,
            category=ticket.category,
            text=ticket.text,
            updated_text=ticket.updated_text,
            state=ticket.state
        )


class TicketListResponse(BaseModel):
    """Response model for list of tickets."""
    tickets: List[TicketResponse]


class TriageResponse(BaseModel):
    """
    Response model for AI triage.
    
    Contains the classification result and AI-generated response.
    """
    category: Category
    priority: Priority
    suggested_answer: str


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
