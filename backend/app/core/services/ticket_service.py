"""
Ticket service - business logic for ticket management.

This service contains all business logic related to tickets:
- CRUD operations
- FSM validation
- Filtering
- Acquisition
"""

from typing import Dict, List, Optional
import uuid

from backend.app.core.models.ticket import Ticket, Category, Priority, State
from backend.app.core.fsm.state_machine import validate_transition


class TicketService:
    """
    Service for managing tickets.
    
    This is the central business logic component for ticket operations.
    All ticket-related business rules are enforced here.
    """

    def __init__(self):
        """Initialize the ticket service with an empty ticket store."""
        self._tickets: Dict[str, Ticket] = {}
        self._next_id_counter: int = 1

    def create_ticket(
        self,
        text: str,
        category: Category = Category.OTHER,
        priority: Priority = Priority.MEDIUM
    ) -> Ticket:
        """
        Create a new ticket.
        
        Args:
            text: The ticket text/content
            category: The ticket category (default: OTHER)
            priority: The ticket priority (default: MEDIUM)
            
        Returns:
            The created Ticket instance
        """
        ticket_id = f"ticket-{self._next_id_counter}"
        self._next_id_counter += 1
        
        ticket = Ticket(
            id=ticket_id,
            user_id=None,
            priority=priority,
            category=category,
            text=text,
            updated_text=None,
            state=State.PENDING
        )
        
        self._tickets[ticket_id] = ticket
        return ticket

    def list_tickets(
        self,
        category: Optional[Category] = None,
        priority: Optional[Priority] = None,
        state: Optional[State] = None
    ) -> List[Ticket]:
        """
        List tickets with optional filtering.
        
        Args:
            category: Optional category filter
            priority: Optional priority filter
            state: Optional state filter
            
        Returns:
            List of matching Ticket instances
        """
        tickets = list(self._tickets.values())
        
        # Apply filters
        if category is not None:
            tickets = [t for t in tickets if t.category == category]
        if priority is not None:
            tickets = [t for t in tickets if t.priority == priority]
        if state is not None:
            tickets = [t for t in tickets if t.state == state]
        
        return tickets

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Get a single ticket by ID.
        
        Args:
            ticket_id: The ID of the ticket to retrieve
            
        Returns:
            The Ticket instance if found, None otherwise
        """
        return self._tickets.get(ticket_id)

    def update_ticket(
        self,
        ticket_id: str,
        user_id: Optional[str] = None,
        new_state: Optional[State] = None,
        updated_text: Optional[str] = None
    ) -> Optional[Ticket]:
        """
        Update a ticket with FSM validation.
        
        This method enforces state transition rules defined in the FSM.
        Invalid transitions will raise a ValueError.
        
        Args:
            ticket_id: The ID of the ticket to update
            user_id: Optional user ID to assign
            new_state: Optional new state (will validate transition)
            updated_text: Optional updated text
            
        Returns:
            The updated Ticket instance if found
            
        Raises:
            ValueError: If the state transition is invalid
        """
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            return None
        
        # Validate state transition if state is being changed
        if new_state is not None and new_state != ticket.state:
            if not validate_transition(ticket.state, new_state):
                raise ValueError(
                    f"Invalid state transition: {ticket.state.value} -> {new_state.value}"
                )
        
        # Create a new ticket with updated values (dataclasses are immutable)
        updated_ticket = Ticket(
            id=ticket.id,
            user_id=user_id if user_id is not None else ticket.user_id,
            priority=ticket.priority,
            category=ticket.category,
            text=ticket.text,
            updated_text=updated_text if updated_text is not None else ticket.updated_text,
            state=new_state if new_state is not None else ticket.state
        )
        
        self._tickets[ticket_id] = updated_ticket
        return updated_ticket

    def acquire_ticket(self, ticket_id: str, user_id: str) -> Optional[Ticket]:
        """
        Acquire a ticket (assign to user and transition to reviewed).
        
        This is a convenience method that:
        1. Assigns the ticket to the specified user
        2. Transitions the ticket state to REVIEWED
        
        Note: According to FSM rules, pending -> processing is not allowed.
        The workflow is: pending -> reviewed -> processing.
        Acquiring a ticket moves it to reviewed state, and the agent can then
        transition it to processing when they start working on it.
        
        Args:
            ticket_id: The ID of the ticket to acquire
            user_id: The ID of the user acquiring the ticket
            
        Returns:
            The updated Ticket instance if found and acquired successfully
            
        Raises:
            ValueError: If the state transition is invalid
        """
        return self.update_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
            new_state=State.REVIEWED
        )

    def get_ticket_count(self) -> int:
        """Get the total number of tickets."""
        return len(self._tickets)

    def reset(self) -> None:
        """Reset the ticket service (clear all tickets). For testing only."""
        self._tickets.clear()
        self._next_id_counter = 1
