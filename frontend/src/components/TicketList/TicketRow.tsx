/**
 * TicketRow component - displays a single ticket in the list.
 */

import React from 'react';
import type { Ticket } from '../../types/api';

interface Props {
  ticket: Ticket;
  isSelected: boolean;
  onClick: () => void;
}

const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'high': return 'priority-high';
    case 'medium': return 'priority-medium';
    case 'low': return 'priority-low';
    default: return '';
  }
};

const getStateColor = (state: string): string => {
  switch (state) {
    case 'pending': return 'state-pending';
    case 'reviewed': return 'state-reviewed';
    case 'processing': return 'state-processing';
    case 'closed': return 'state-closed';
    default: return '';
  }
};

export const TicketRow: React.FC<Props> = ({ ticket, isSelected, onClick }) => {
  return (
    <div
      className={`ticket-row ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      data-testid={`ticket-row-${ticket.id}`}
    >
      <span className={`cell priority ${getPriorityColor(ticket.priority)}`}>
        {ticket.priority}
      </span>
      <span className="cell category">{ticket.category}</span>
      <span className={`cell state ${getStateColor(ticket.state)}`}>
        {ticket.state}
      </span>
      <span className="cell text">
        {ticket.text.length > 60 ? `${ticket.text.substring(0, 60)}...` : ticket.text}
      </span>
    </div>
  );
};

export default TicketRow;
