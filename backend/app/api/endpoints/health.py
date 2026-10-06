"""
Health check endpoint.
"""

from fastapi import APIRouter

from backend.app.api.models.response import HealthResponse


# Create router for health endpoints
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API service"
)
async def health_check() -> HealthResponse:
    """
    Health endpoint to verify the API is running correctly.
    
    Returns:
        HealthResponse with status and version information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )
