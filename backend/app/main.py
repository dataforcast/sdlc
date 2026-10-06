"""FastAPI application entrypoint: lifespan seeding, CORS, router mounting."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, tickets
from app.seed_data import SEED_TICKET_TEXTS
from app.service import create_ticket_from_text
from app.store import TicketStore


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the in-memory ticket store and seed it with 20 demo tickets."""
    store = TicketStore()
    for ticket_text in SEED_TICKET_TEXTS:
        await create_ticket_from_text(store, ticket_text)
    app.state.store = store
    yield


app = FastAPI(title="Ticket Triage API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tickets.router)
