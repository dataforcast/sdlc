"""
Tests for core business logic.

Tests cover:
- FSM state transitions
- Ticket service operations
- AI service classification
"""

import pytest

from backend.app.core.models.ticket import Ticket, Category, Priority, State
from backend.app.core.fsm.state_machine import validate_transition, get_allowed_transitions
from backend.app.core.services.ticket_service import TicketService
from backend.app.core.services.ai_service import AIService


# ============================================================================
# FSM State Machine Tests
# ============================================================================

class TestStateMachine:
    """Tests for the FSM state machine implementation."""

    def test_valid_transitions(self):
        """Test all valid transitions from specifications."""
        # Main transitions
        assert validate_transition(State.PENDING, State.REVIEWED) == True
        assert validate_transition(State.REVIEWED, State.PROCESSING) == True
        assert validate_transition(State.PROCESSING, State.CLOSED) == True
        
    def test_self_transitions(self):
        """Test that all states can self-transition."""
        assert validate_transition(State.PENDING, State.PENDING) == True
        assert validate_transition(State.REVIEWED, State.REVIEWED) == True
        assert validate_transition(State.PROCESSING, State.PROCESSING) == True
        assert validate_transition(State.CLOSED, State.CLOSED) == True

    def test_invalid_transitions_to_closed(self):
        """Test that only processing can transition to closed."""
        assert validate_transition(State.PENDING, State.CLOSED) == False
        assert validate_transition(State.REVIEWED, State.CLOSED) == False

    def test_invalid_transitions_from_closed(self):
        """Test that closed state cannot transition to other states."""
        assert validate_transition(State.CLOSED, State.PENDING) == False
        assert validate_transition(State.CLOSED, State.REVIEWED) == False
        assert validate_transition(State.CLOSED, State.PROCESSING) == False

    def test_skip_transitions(self):
        """Test that skipping states is not allowed."""
        assert validate_transition(State.PENDING, State.PROCESSING) == False
        assert validate_transition(State.PENDING, State.CLOSED) == False
        assert validate_transition(State.REVIEWED, State.CLOSED) == False

    def test_get_allowed_transitions_pending(self):
        """Test allowed transitions from pending."""
        allowed = get_allowed_transitions(State.PENDING)
        assert allowed == {State.PENDING, State.REVIEWED}

    def test_get_allowed_transitions_reviewed(self):
        """Test allowed transitions from reviewed."""
        allowed = get_allowed_transitions(State.REVIEWED)
        assert allowed == {State.REVIEWED, State.PROCESSING}

    def test_get_allowed_transitions_processing(self):
        """Test allowed transitions from processing."""
        allowed = get_allowed_transitions(State.PROCESSING)
        assert allowed == {State.PROCESSING, State.CLOSED}

    def test_get_allowed_transitions_closed(self):
        """Test allowed transitions from closed."""
        allowed = get_allowed_transitions(State.CLOSED)
        assert allowed == {State.CLOSED}


# ============================================================================
# Ticket Service Tests
# ============================================================================

class TestTicketService:
    """Tests for the TicketService class."""

    @pytest.fixture
    def service(self):
        """Create a fresh TicketService instance for each test."""
        return TicketService()

    def test_create_ticket(self, service):
        """Test creating a new ticket."""
        ticket = service.create_ticket(
            "Test ticket text",
            Category.TECHNICAL,
            Priority.HIGH
        )
        
        assert ticket.id is not None
        assert ticket.text == "Test ticket text"
        assert ticket.category == Category.TECHNICAL
        assert ticket.priority == Priority.HIGH
        assert ticket.state == State.PENDING
        assert ticket.user_id is None
        assert ticket.updated_text is None

    def test_create_ticket_defaults(self, service):
        """Test creating a ticket with default values."""
        ticket = service.create_ticket("Test")
        
        assert ticket.category == Category.OTHER
        assert ticket.priority == Priority.MEDIUM
        assert ticket.state == State.PENDING

    def test_list_tickets_empty(self, service):
        """Test listing tickets when none exist."""
        tickets = service.list_tickets()
        assert len(tickets) == 0

    def test_list_tickets_all(self, service):
        """Test listing all tickets."""
        service.create_ticket("Ticket 1", Category.TECHNICAL, Priority.HIGH)
        service.create_ticket("Ticket 2", Category.BILLING, Priority.LOW)
        service.create_ticket("Ticket 3", Category.ACCOUNT, Priority.MEDIUM)
        
        tickets = service.list_tickets()
        assert len(tickets) == 3

    def test_list_tickets_filter_category(self, service):
        """Test filtering tickets by category."""
        service.create_ticket("Tech 1", Category.TECHNICAL, Priority.HIGH)
        service.create_ticket("Tech 2", Category.TECHNICAL, Priority.LOW)
        service.create_ticket("Billing 1", Category.BILLING, Priority.MEDIUM)
        
        tech_tickets = service.list_tickets(category=Category.TECHNICAL)
        assert len(tech_tickets) == 2
        assert all(t.category == Category.TECHNICAL for t in tech_tickets)

    def test_list_tickets_filter_priority(self, service):
        """Test filtering tickets by priority."""
        service.create_ticket("High 1", Category.TECHNICAL, Priority.HIGH)
        service.create_ticket("High 2", Category.BILLING, Priority.HIGH)
        service.create_ticket("Low 1", Category.ACCOUNT, Priority.LOW)
        
        high_tickets = service.list_tickets(priority=Priority.HIGH)
        assert len(high_tickets) == 2
        assert all(t.priority == Priority.HIGH for t in high_tickets)

    def test_list_tickets_filter_state(self, service):
        """Test filtering tickets by state."""
        service.create_ticket("Ticket 1")
        service.create_ticket("Ticket 2")
        service.create_ticket("Ticket 3")
        
        # Update one ticket's state
        tickets = service.list_tickets()
        service.update_ticket(tickets[0].id, new_state=State.REVIEWED)
        
        reviewed_tickets = service.list_tickets(state=State.REVIEWED)
        assert len(reviewed_tickets) == 1

    def test_list_tickets_multiple_filters(self, service):
        """Test filtering with multiple criteria."""
        service.create_ticket("Tech High", Category.TECHNICAL, Priority.HIGH)
        service.create_ticket("Tech Low", Category.TECHNICAL, Priority.LOW)
        service.create_ticket("Billing High", Category.BILLING, Priority.HIGH)
        
        tickets = service.list_tickets(
            category=Category.TECHNICAL,
            priority=Priority.HIGH
        )
        assert len(tickets) == 1
        assert tickets[0].category == Category.TECHNICAL
        assert tickets[0].priority == Priority.HIGH

    def test_get_ticket(self, service):
        """Test retrieving a specific ticket by ID."""
        created = service.create_ticket("Test ticket")
        
        retrieved = service.get_ticket(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.text == "Test ticket"

    def test_get_ticket_not_found(self, service):
        """Test retrieving a non-existent ticket."""
        ticket = service.get_ticket("non-existent-id")
        assert ticket is None

    def test_update_ticket_valid_transition(self, service):
        """Test updating ticket with valid state transition."""
        ticket = service.create_ticket("Test")
        
        # Valid: pending -> reviewed
        updated = service.update_ticket(ticket.id, new_state=State.REVIEWED)
        assert updated.state == State.REVIEWED
        
        # Valid: reviewed -> processing
        updated = service.update_ticket(ticket.id, new_state=State.PROCESSING)
        assert updated.state == State.PROCESSING
        
        # Valid: processing -> closed
        updated = service.update_ticket(ticket.id, new_state=State.CLOSED)
        assert updated.state == State.CLOSED

    def test_update_ticket_invalid_transition(self, service):
        """Test that invalid state transitions raise ValueError."""
        ticket = service.create_ticket("Test")
        
        # Invalid: pending -> closed
        with pytest.raises(ValueError) as exc_info:
            service.update_ticket(ticket.id, new_state=State.CLOSED)
        
        assert "Invalid state transition" in str(exc_info.value)

    def test_update_ticket_user_id(self, service):
        """Test updating ticket user assignment."""
        ticket = service.create_ticket("Test")
        
        updated = service.update_ticket(ticket.id, user_id="user-123")
        assert updated.user_id == "user-123"

    def test_update_ticket_updated_text(self, service):
        """Test updating ticket text."""
        ticket = service.create_ticket("Original text")
        
        updated = service.update_ticket(
            ticket.id,
            updated_text="AI-generated response"
        )
        assert updated.updated_text == "AI-generated response"

    def test_acquire_ticket(self, service):
        """Test acquiring a ticket."""
        ticket = service.create_ticket("Test")
        
        acquired = service.acquire_ticket(ticket.id, "agent-001")
        assert acquired is not None
        assert acquired.user_id == "agent-001"
        assert acquired.state == State.REVIEWED

    def test_acquire_ticket_invalid_state(self, service):
        """Test that acquiring a closed ticket raises error."""
        ticket = service.create_ticket("Test")
        
        # First transition to closed via valid path: pending -> reviewed -> processing -> closed
        reviewed_ticket = service.update_ticket(ticket.id, new_state=State.REVIEWED)
        assert reviewed_ticket is not None
        assert reviewed_ticket.state == State.REVIEWED
        
        processing_ticket = service.update_ticket(ticket.id, new_state=State.PROCESSING)
        assert processing_ticket is not None
        assert processing_ticket.state == State.PROCESSING
        
        closed_ticket = service.update_ticket(ticket.id, new_state=State.CLOSED)
        assert closed_ticket is not None
        assert closed_ticket.state == State.CLOSED
        
        # Try to acquire (should fail: closed -> reviewed is invalid)
        with pytest.raises(ValueError) as exc_info:
            service.acquire_ticket(ticket.id, "agent-001")
        assert "Invalid state transition" in str(exc_info.value)

    def test_get_ticket_count(self, service):
        """Test getting ticket count."""
        assert service.get_ticket_count() == 0
        
        service.create_ticket("Ticket 1")
        assert service.get_ticket_count() == 1
        
        service.create_ticket("Ticket 2")
        assert service.get_ticket_count() == 2

    def test_reset(self, service):
        """Test resetting the service."""
        service.create_ticket("Ticket 1")
        service.create_ticket("Ticket 2")
        
        assert service.get_ticket_count() == 2
        
        service.reset()
        
        assert service.get_ticket_count() == 0


# ============================================================================
# AI Service Tests
# ============================================================================

class TestAIService:
    """Tests for the AIService class."""

    @pytest.fixture
    def service(self):
        """Create a fresh AIService instance for each test."""
        return AIService()

    def test_triage_billing(self, service):
        """Test triage for billing-related ticket."""
        result = service.triage("My invoice is incorrect and I need a refund")
        
        assert result["category"] == "billing"
        assert "suggested_answer" in result
        assert len(result["suggested_answer"]) > 0

    def test_triage_technical(self, service):
        """Test triage for technical-related ticket."""
        result = service.triage("The application crashes when I try to login")
        
        assert result["category"] == "technical"
        assert "suggested_answer" in result

    def test_triage_account(self, service):
        """Test triage for account-related ticket."""
        result = service.triage("I forgot my password and need to reset it")
        
        assert result["category"] == "account"
        assert "suggested_answer" in result

    def test_triage_other(self, service):
        """Test triage for other category ticket."""
        result = service.triage("What are your office hours?")
        
        assert result["category"] == "other"
        assert "suggested_answer" in result

    def test_triage_empty_text(self, service):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError):
            service.triage("")
        
        with pytest.raises(ValueError):
            service.triage("   ")

    def test_triage_priority_classification(self, service):
        """Test priority classification."""
        # Test urgent detection
        result = service.triage("This is an urgent critical emergency")
        assert result["priority"] == "high"
        
        # Test bug/error detection
        result = service.triage("There is a bug in the application")
        assert result["priority"] in ["high", "medium", "low"]

    def test_triage_result_structure(self, service):
        """Test that triage result has correct structure."""
        result = service.triage("Test ticket")
        
        assert isinstance(result, dict)
        assert "category" in result
        assert "priority" in result
        assert "suggested_answer" in result
        assert result["category"] in ["billing", "technical", "account", "other"]
        assert result["priority"] in ["low", "medium", "high"]
