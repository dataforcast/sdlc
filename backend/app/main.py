"""
Main FastAPI application entry point.

This module creates and configures the FastAPI application with all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import health, tickets, triage
from app.config import settings


# Create FastAPI application
app = FastAPI(
    title="Ticket Processing API",
    version="1.0.0",
    description="""
    API for processing customer support tickets with AI assistance.
    
    This API provides endpoints for:
    - Managing customer support tickets
    - Filtering tickets by various criteria
    - Classifying tickets using AI
    - Updating ticket state with FSM validation
    
    **Business Rules:**
    - All business logic is processed in the backend
    - State transitions follow FSM rules:
      - pending -> reviewed -> processing -> closed
      - All states can self-transition
      - Invalid transitions are rejected
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{settings.frontend_port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/backend")
app.include_router(tickets.router, prefix="/backend")
app.include_router(triage.router, prefix="/backend")


# For standalone testing (if needed)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
