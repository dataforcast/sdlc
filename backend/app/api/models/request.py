"""
Pydantic request models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional

from backend.app.core.models.ticket import Category, Priority, State


class TicketFilterRequest(BaseModel):
    """
    Request model for filtering tickets.
    
    All fields are optional - if not provided, no filtering is applied on that field.
    """
    category: Optional[Category] = Field(
        None,
        description="Filter by ticket category"
    )
    priority: Optional[Priority] = Field(
        None,
        description="Filter by ticket priority"
    )
    state: Optional[State] = Field(
        None,
        description="Filter by ticket state"
    )


class TicketUpdateRequest(BaseModel):
    """
    Request model for updating a ticket.
    
    All fields except ticket_id are optional - only provided fields will be updated.
    """
    ticket_id: str = Field(
        ...,
        description="The ID of the ticket to update"
    )
    user_id: Optional[str] = Field(
        None,
        description="The user ID to assign to the ticket"
    )
    state: Optional[State] = Field(
        None,
        description="The new state of the ticket"
    )
    updated_text: Optional[str] = Field(
        None,
        description="The updated text from AI generation or agent input"
    )


class TriageRequest(BaseModel):
    """
    Request model for AI triage endpoint.
    
    Contains the ticket text to be classified and processed by AI.
    """
    ticket_text: str = Field(
        ...,
        description="The text of the ticket to classify and generate a response for",
        min_length=1
    )
