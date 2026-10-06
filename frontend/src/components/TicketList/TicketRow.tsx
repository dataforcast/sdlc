import type { Ticket } from '../../api/generated/models';

interface TicketRowProps {
  ticket: Ticket;
  selected: boolean;
  onSelect: (ticketId: string) => void;
}

export function TicketRow({ ticket, selected, onSelect }: TicketRowProps) {
  return (
    <tr className={selected ? 'selected' : ''} onClick={() => onSelect(ticket.id)}>
      <td>{ticket.id.slice(0, 8)}</td>
      <td>{ticket.category}</td>
      <td>{ticket.priority}</td>
      <td>
        <span className="state-badge">{ticket.state}</span>
      </td>
      <td>{ticket.user_id ?? '—'}</td>
    </tr>
  );
}
