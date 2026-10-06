"""
Ticket API endpoints.

Provides endpoints for:
- Listing tickets
- Filtering tickets
- Updating tickets
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from backend.app.core.models.ticket import Category, Priority, State
from backend.app.core.services.ticket_service import TicketService
from backend.app.api.models.request import TicketFilterRequest, TicketUpdateRequest
from backend.app.api.models.response import TicketListResponse, TicketResponse


# Create router for ticket endpoints
router = APIRouter(prefix="/api")

# Initialize service (singleton for simplicity - in production use DI)
# Note: This creates a shared service instance. For production, consider
# using dependency injection for better testability
_ticket_service = TicketService()

# Initialize with sample tickets
_sample_tickets_created = False


def _ensure_sample_tickets():
    """Create sample tickets on first request (for demo purposes)."""
    global _sample_tickets_created
    if not _sample_tickets_created:
        sample_tickets = [
            ("I can't login to my account", Category.ACCOUNT, Priority.HIGH),
            ("My invoice #12345 is incorrect", Category.BILLING, Priority.MEDIUM),
            ("The application crashes on startup", Category.TECHNICAL, Priority.HIGH),
            ("General inquiry about your services", Category.OTHER, Priority.LOW),
            ("Payment failed for subscription renewal", Category.BILLING, Priority.HIGH),
            ("Feature request: dark mode", Category.OTHER, Priority.LOW),
            ("API is returning 500 errors", Category.TECHNICAL, Priority.HIGH),
            ("Forgot password reset not working", Category.ACCOUNT, Priority.MEDIUM),
        ]
        for text, category, priority in sample_tickets:
            _ticket_service.create_ticket(text, category, priority)
        _sample_tickets_created = True


@router.get(
    "/tickets",
    response_model=TicketListResponse,
    summary="List Tickets",
    description="Get a list of all tickets, optionally filtered by category, priority, or state"
)
async def list_tickets(
    category: Optional[Category] = None,
    priority: Optional[Priority] = None,
    state: Optional[State] = None
) -> TicketListResponse:
    """
    List tickets with optional filtering.
    
    Args:
        category: Optional category filter
        priority: Optional priority filter
        state: Optional state filter
        
    Returns:
        TicketListResponse containing all matching tickets
    """
    _ensure_sample_tickets()
    
    tickets = _ticket_service.list_tickets(
        category=category,
        priority=priority,
        state=state
    )
    
    # Convert domain models to response models
    ticket_responses = [TicketResponse.from_domain(t) for t in tickets]
    
    return TicketListResponse(tickets=ticket_responses)


@router.post(
    "/filter",
    response_model=TicketListResponse,
    summary="Filter Tickets",
    description="Filter tickets using a request body with category, priority, and state"
)
async def filter_tickets(
    filter_request: TicketFilterRequest
) -> TicketListResponse:
    """
    Filter tickets based on provided criteria.
    
    This endpoint accepts a POST request with filter parameters in the body.
    
    Args:
        filter_request: Filter criteria (category, priority, state)
        
    Returns:
        TicketListResponse containing all matching tickets
    """
    _ensure_sample_tickets()
    
    tickets = _ticket_service.list_tickets(
        category=filter_request.category,
        priority=filter_request.priority,
        state=filter_request.state
    )
    
    # Convert domain models to response models
    ticket_responses = [TicketResponse.from_domain(t) for t in tickets]
    
    return TicketListResponse(tickets=ticket_responses)


@router.post(
    "/update",
    response_model=TicketResponse,
    summary="Update Ticket",
    description="Update a ticket's state, assigned user, or text content",
    status_code=status.HTTP_200_OK
)
async def update_ticket(
    update_request: TicketUpdateRequest
) -> TicketResponse:
    """
    Update a ticket with the provided information.
    
    This endpoint enforces FSM (Finite State Machine) rules for state transitions.
    Invalid transitions will return a 400 Bad Request error.
    
    Args:
        update_request: Update request containing ticket_id and optional fields
        
    Returns:
        TicketResponse with the updated ticket
        
    Raises:
        HTTPException 404: If ticket not found
        HTTPException 400: If state transition is invalid
    """
    _ensure_sample_tickets()
    
    try:
        ticket = _ticket_service.update_ticket(
            ticket_id=update_request.ticket_id,
            user_id=update_request.user_id,
            new_state=update_request.state,
            updated_text=update_request.updated_text
        )
        
        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id '{update_request.ticket_id}' not found"
            )
        
        return TicketResponse.from_domain(ticket)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
