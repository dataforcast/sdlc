/**
 * TicketList component - displays a list of tickets.
 */

import React from 'react';
import type { Ticket } from '../../types/api';
import { TicketRow } from './TicketRow';

interface Props {
  tickets: Ticket[];
  onSelect: (ticket: Ticket) => void;
  selectedId?: string;
}

export const TicketList: React.FC<Props> = ({ tickets, onSelect, selectedId }) => {
  if (tickets.length === 0) {
    return (
      <div className="ticket-list-empty" data-testid="ticket-list-empty">
        No tickets found matching your criteria.
      </div>
    );
  }

  return (
    <div className="ticket-list" data-testid="ticket-list">
      <div className="ticket-list-header">
        <span className="header-cell priority">Priority</span>
        <span className="header-cell category">Category</span>
        <span className="header-cell state">State</span>
        <span className="header-cell text">Text</span>
      </div>
      {tickets.map(ticket => (
        <TicketRow
          key={ticket.id}
          ticket={ticket}
          isSelected={ticket.id === selectedId}
          onClick={() => onSelect(ticket)}
        />
      ))}
    </div>
  );
};

export default TicketList;
