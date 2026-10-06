import type { Ticket } from '../../api/generated/models';
import { TicketRow } from './TicketRow';

interface TicketListProps {
  tickets: Ticket[];
  status: 'idle' | 'loading' | 'success' | 'error';
  error: string | null;
  selectedTicketId: string | null;
  onSelect: (ticketId: string) => void;
}

export function TicketList({ tickets, status, error, selectedTicketId, onSelect }: TicketListProps) {
  if (status === 'loading') {
    return <p>Loading tickets…</p>;
  }

  if (status === 'error') {
    return <div className="error-banner">{error}</div>;
  }

  if (tickets.length === 0) {
    return <p className="empty-state">No tickets match the current filters.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Category</th>
          <th>Priority</th>
          <th>State</th>
          <th>User</th>
        </tr>
      </thead>
      <tbody>
        {tickets.map((ticket) => (
          <TicketRow
            key={ticket.id}
            ticket={ticket}
            selected={ticket.id === selectedTicketId}
            onSelect={onSelect}
          />
        ))}
      </tbody>
    </table>
  );
}
