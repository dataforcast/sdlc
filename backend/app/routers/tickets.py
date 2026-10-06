"""Ticket triage, listing, filtering and update endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.models import TicketListResponse, TriageRequest, FilterRequest, UpdateRequest, Ticket
from app.service import create_ticket_from_text
from app.store import InvalidTransitionError, TicketNotFoundError, TicketStore
from app.config import settings

router = APIRouter(prefix="/backend/api", tags=["tickets"])


def get_store(request: Request) -> TicketStore:
    """Resolve the application's ticket store from app state (set up in lifespan)."""
    return request.app.state.store


@router.post("/triage", response_model=Ticket, operation_id="triage")
async def triage(
    body: TriageRequest,
    store: TicketStore = Depends(get_store),
) -> Ticket:
    """Classify incoming free text and draft a suggested answer, creating a new pending ticket."""
    return await create_ticket_from_text(store, body.ticket_text)


@router.get("/tickets", response_model=TicketListResponse, operation_id="listTickets")
async def list_tickets(store: TicketStore = Depends(get_store)) -> TicketListResponse:
    """Return the full list of tickets."""
    return TicketListResponse(tickets=await store.list_all())


@router.post("/filter", response_model=TicketListResponse, operation_id="filterTickets")
async def filter_tickets(
    body: FilterRequest,
    store: TicketStore = Depends(get_store),
) -> TicketListResponse:
    """Return tickets matching the given attribute filters (AND-combined)."""
    tickets = await store.filter(
        category=body.category,
        priority=body.priority,
        state=body.state,
        user_id=body.user_id,
    )
    return TicketListResponse(tickets=tickets)


@router.post("/update", response_model=Ticket, operation_id="updateTicket")
async def update_ticket(
    body: UpdateRequest,
    store: TicketStore = Depends(get_store),
) -> Ticket:
    """Submit a ticket with its updated state and optional edited fields.

    Also serves as "acquire" when target_state is "reviewed" on a pending
    ticket: the backend then auto-assigns the hardcoded demo user.
    """
    try:
        return await store.apply_update(
            ticket_id=body.ticket_id,
            target_state=body.target_state,
            demo_user_id=settings.demo_user_id,
            category=body.category,
            priority=body.priority,
            updated_text=body.updated_text,
        )
    except TicketNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Ticket {body.ticket_id} not found") from exc
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
