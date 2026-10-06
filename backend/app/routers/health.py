"""Health check endpoint."""

from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(prefix="/backend", tags=["health"])


@router.get("/health", response_model=HealthResponse, operation_id="getHealth")
async def get_health() -> HealthResponse:
    """Return a static OK payload used by readiness probes and test scripts."""
    return HealthResponse(status="ok")
