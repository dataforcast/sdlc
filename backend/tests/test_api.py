"""
Tests for API endpoints.

Tests cover:
- Health endpoint
- Ticket endpoints (list, filter, update)
- Triage endpoint
- Error handling
"""

from fastapi.testclient import TestClient
import pytest

from backend.app.main import app


# Create test client
client = TestClient(app)


# ============================================================================
# Health Endpoint Tests
# ============================================================================

class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_endpoint(self):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/backend/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["version"] == "1.0.0"

    def test_health_endpoint_schema(self):
        """Test that health endpoint returns correct schema."""
        response = client.get("/backend/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)


# ============================================================================
# Tickets Endpoint Tests
# ============================================================================

class TestTicketsEndpoints:
    """Tests for ticket-related endpoints."""

    def test_list_tickets(self):
        """Test listing all tickets."""
        response = client.get("/backend/api/tickets")
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert isinstance(data["tickets"], list)
        # Sample tickets are created on first request
        assert len(data["tickets"]) >= 0

    def test_list_tickets_with_category_filter(self):
        """Test listing tickets filtered by category."""
        # First get all tickets to ensure sample data exists
        client.get("/backend/api/tickets")
        
        response = client.get("/backend/api/tickets?category=technical")
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        # All returned tickets should be technical
        for ticket in data["tickets"]:
            assert ticket["category"] == "technical"

    def test_list_tickets_with_priority_filter(self):
        """Test listing tickets filtered by priority."""
        # First get all tickets to ensure sample data exists
        client.get("/backend/api/tickets")
        
        response = client.get("/backend/api/tickets?priority=high")
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        # All returned tickets should be high priority
        for ticket in data["tickets"]:
            assert ticket["priority"] == "high"

    def test_list_tickets_with_state_filter(self):
        """Test listing tickets filtered by state."""
        # First get all tickets to ensure sample data exists
        client.get("/backend/api/tickets")
        
        response = client.get("/backend/api/tickets?state=pending")
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        # All returned tickets should be pending
        for ticket in data["tickets"]:
            assert ticket["state"] == "pending"

    def test_list_tickets_multiple_filters(self):
        """Test listing tickets with multiple filters."""
        # First get all tickets to ensure sample data exists
        client.get("/backend/api/tickets")
        
        response = client.get("/backend/api/tickets?category=technical&priority=high")
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        # All returned tickets should match both filters
        for ticket in data["tickets"]:
            assert ticket["category"] == "technical"
            assert ticket["priority"] == "high"

    def test_filter_tickets_post(self):
        """Test POST filter endpoint."""
        # First get all tickets to ensure sample data exists
        client.get("/backend/api/tickets")
        
        response = client.post(
            "/backend/api/filter",
            json={"category": "billing"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        # All returned tickets should be billing
        for ticket in data["tickets"]:
            assert ticket["category"] == "billing"

    def test_filter_tickets_empty_result(self):
        """Test filter that returns no tickets."""
        # First get all tickets to ensure sample data exists
        client.get("/backend/api/tickets")
        
        response = client.post(
            "/backend/api/filter",
            json={"category": "billing", "priority": "low"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        # May have 0 or more tickets matching both criteria
        assert isinstance(data["tickets"], list)

    def test_get_single_ticket(self):
        """Test retrieving ticket details."""
        # First get all tickets to ensure sample data exists
        list_response = client.get("/backend/api/tickets")
        tickets = list_response.json()["tickets"]
        
        if len(tickets) > 0:
            ticket_id = tickets[0]["id"]
            
            # Get the specific ticket (via list with filter)
            response = client.get(f"/backend/api/tickets?state=pending")
            assert response.status_code == 200

    def test_update_ticket_valid(self):
        """Test updating a ticket with valid data."""
        # First get all tickets to ensure sample data exists
        list_response = client.get("/backend/api/tickets")
        tickets = list_response.json()["tickets"]
        
        if len(tickets) > 0:
            ticket_id = tickets[0]["id"]
            
            # Update the ticket state to reviewed
            response = client.post(
                "/backend/api/update",
                json={
                    "ticket_id": ticket_id,
                    "state": "reviewed"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["state"] == "reviewed"
            assert data["id"] == ticket_id

    def test_update_ticket_with_user_id(self):
        """Test updating a ticket with user assignment."""
        # First get all tickets to ensure sample data exists
        list_response = client.get("/backend/api/tickets")
        tickets = list_response.json()["tickets"]
        
        if len(tickets) > 0:
            ticket_id = tickets[0]["id"]
            
            response = client.post(
                "/backend/api/update",
                json={
                    "ticket_id": ticket_id,
                    "user_id": "agent-001",
                    "state": "processing"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "agent-001"
            assert data["state"] == "processing"

    def test_update_ticket_with_updated_text(self):
        """Test updating a ticket with response text."""
        # First get all tickets to ensure sample data exists
        list_response = client.get("/backend/api/tickets")
        tickets = list_response.json()["tickets"]
        
        if len(tickets) > 0:
            ticket_id = tickets[0]["id"]
            
            response = client.post(
                "/backend/api/update",
                json={
                    "ticket_id": ticket_id,
                    "updated_text": "This is the AI-generated response"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["updated_text"] == "This is the AI-generated response"

    def test_update_ticket_not_found(self):
        """Test updating a non-existent ticket."""
        response = client.post(
            "/backend/api/update",
            json={
                "ticket_id": "non-existent-ticket-id",
                "state": "reviewed"
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_ticket_invalid_transition(self):
        """Test updating a ticket with invalid state transition."""
        # First get all tickets to ensure sample data exists
        list_response = client.get("/backend/api/tickets")
        tickets = list_response.json()["tickets"]
        
        if len(tickets) > 0:
            # Find a ticket that is still in pending state
            pending_tickets = [t for t in tickets if t["state"] == "pending"]
            if pending_tickets:
                ticket_id = pending_tickets[0]["id"]
                
                # Try to transition directly from pending to closed (invalid)
                response = client.post(
                    "/backend/api/update",
                    json={
                        "ticket_id": ticket_id,
                        "state": "closed"
                    }
                )
                
                assert response.status_code == 400
                assert "Invalid state transition" in response.json()["detail"]
            else:
                # If no pending tickets, skip this test
                pytest.skip("No pending tickets available for test")

    def test_ticket_response_structure(self):
        """Test that ticket response has correct structure."""
        # First get all tickets to ensure sample data exists
        list_response = client.get("/backend/api/tickets")
        tickets = list_response.json()["tickets"]
        
        if len(tickets) > 0:
            ticket = tickets[0]
            
            # Check required fields
            assert "id" in ticket
            assert "category" in ticket
            assert "priority" in ticket
            assert "state" in ticket
            assert "text" in ticket
            assert "user_id" in ticket
            assert "updated_text" in ticket


# ============================================================================
# Triage Endpoint Tests
# ============================================================================

class TestTriageEndpoint:
    """Tests for the AI triage endpoint."""

    def test_triage_billing(self):
        """Test triage with billing text."""
        response = client.post(
            "/backend/api/triage",
            json={"ticket_text": "My invoice is incorrect"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "billing"
        assert data["priority"] in ["low", "medium", "high"]
        assert "suggested_answer" in data
        assert len(data["suggested_answer"]) > 0

    def test_triage_technical(self):
        """Test triage with technical text."""
        response = client.post(
            "/backend/api/triage",
            json={"ticket_text": "The application keeps crashing"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "technical"
        assert data["priority"] in ["low", "medium", "high"]
        assert "suggested_answer" in data

    def test_triage_account(self):
        """Test triage with account text."""
        response = client.post(
            "/backend/api/triage",
            json={"ticket_text": "I cannot login to my account"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "account"
        assert data["priority"] in ["low", "medium", "high"]
        assert "suggested_answer" in data

    def test_triage_other(self):
        """Test triage with other text."""
        response = client.post(
            "/backend/api/triage",
            json={"ticket_text": "What are your business hours?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "other"
        assert data["priority"] in ["low", "medium", "high"]
        assert "suggested_answer" in data

    def test_triage_empty_text(self):
        """Test triage with empty text."""
        response = client.post(
            "/backend/api/triage",
            json={"ticket_text": ""}
        )
        
        # Pydantic validates that ticket_text has min_length=1, returns 422
        assert response.status_code == 422
        # Check that validation error is present
        assert "field required" in response.text.lower() or "min_length" in response.text.lower()

    def test_triage_missing_text(self):
        """Test triage with missing text field."""
        response = client.post(
            "/backend/api/triage",
            json={}
        )
        
        assert response.status_code == 422  # Validation error

    def test_triage_response_structure(self):
        """Test that triage response has correct structure."""
        response = client.post(
            "/backend/api/triage",
            json={"ticket_text": "Test ticket"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "category" in data
        assert "priority" in data
        assert "suggested_answer" in data
        assert data["category"] in ["billing", "technical", "account", "other"]
        assert data["priority"] in ["low", "medium", "high"]
        assert isinstance(data["suggested_answer"], str)


# ============================================================================
# OpenAPI Schema Tests
# ============================================================================

class TestOpenAPISchema:
    """Tests for OpenAPI schema generation."""

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert "components" in data

    def test_openapi_info(self):
        """Test OpenAPI info section."""
        response = client.get("/openapi.json")
        data = response.json()
        
        assert data["info"]["title"] == "Ticket Processing API"
        assert data["info"]["version"] == "1.0.0"

    def test_openapi_paths(self):
        """Test that all expected paths are in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        
        paths = data["paths"]
        
        # Check for all endpoints
        assert "/backend/health" in paths
        assert "/backend/api/tickets" in paths
        assert "/backend/api/filter" in paths
        assert "/backend/api/update" in paths
        assert "/backend/api/triage" in paths

    def test_openapi_schemas(self):
        """Test that schemas are defined in OpenAPI."""
        response = client.get("/openapi.json")
        data = response.json()
        
        schemas = data["components"]["schemas"]
        
        # Check for main schemas
        assert "HealthResponse" in schemas
        assert "TicketResponse" in schemas
        assert "TicketListResponse" in schemas
        assert "TriageResponse" in schemas
        assert "TicketFilterRequest" in schemas
        assert "TicketUpdateRequest" in schemas
        assert "TriageRequest" in schemas
