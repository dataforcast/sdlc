"""
Triage API endpoint.

Provides AI-powered ticket classification and response generation.
"""

from fastapi import APIRouter, HTTPException, status

from backend.app.core.services.ai_service import AIService
from backend.app.api.models.request import TriageRequest
from backend.app.api.models.response import TriageResponse


# Create router for triage endpoints
router = APIRouter(prefix="/api")

# Initialize AI service (singleton for simplicity)
_ai_service = AIService()


@router.post(
    "/triage",
    response_model=TriageResponse,
    summary="Classify Ticket",
    description="Classify an incoming ticket and generate a suggested AI response"
)
async def triage_ticket(
    triage_request: TriageRequest
) -> TriageResponse:
    """
    Classify a ticket and draft a suggested answer using AI.
    
    This endpoint takes the ticket text and returns:
    - category: Classified category
    - priority: Classified priority
    - suggested_answer: AI-generated response suggestion
    
    Args:
        triage_request: Request containing ticket_text
        
    Returns:
        TriageResponse with classification and suggested answer
        
    Raises:
        HTTPException 400: If ticket_text is empty or invalid
    """
    try:
        result = _ai_service.triage(triage_request.ticket_text)
        
        return TriageResponse(
            category=result["category"],
            priority=result["priority"],
            suggested_answer=result["suggested_answer"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing ticket: {str(e)}"
        )
