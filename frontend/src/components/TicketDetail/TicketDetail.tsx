import { useEffect, useState } from 'react';
import { updateTicket } from '../../api/generated/client';
import { Category, Priority, TicketState } from '../../api/generated/models';
import type { Ticket } from '../../api/generated/models';
import { legalNextStates } from '../../fsm';

interface TicketDetailProps {
  ticket: Ticket | null;
  onUpdated: () => void;
}

function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { detail?: unknown } } }).response;
    if (response?.data?.detail) {
      return String(response.data.detail);
    }
  }
  return 'Unable to submit this ticket. Please try again.';
}

export function TicketDetail({ ticket, onUpdated }: TicketDetailProps) {
  const [targetState, setTargetState] = useState<TicketState>(TicketState.pending);
  const [category, setCategory] = useState<Category>(Category.other);
  const [priority, setPriority] = useState<Priority>(Priority.medium);
  const [updatedText, setUpdatedText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticket) return;
    const nextStates = legalNextStates(ticket.state);
    setTargetState(nextStates[nextStates.length - 1] ?? ticket.state);
    setCategory(ticket.category);
    setPriority(ticket.priority);
    setUpdatedText(ticket.updated_text);
    setError(null);
  }, [ticket]);

  if (!ticket) {
    return (
      <div className="panel">
        <p className="empty-state">Select a ticket from the list to see its details.</p>
      </div>
    );
  }

  async function handleAcquire() {
    if (!ticket) return;
    setSubmitting(true);
    setError(null);
    try {
      await updateTicket({ ticket_id: ticket.id, target_state: TicketState.reviewed });
      onUpdated();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSubmit() {
    if (!ticket) return;
    setSubmitting(true);
    setError(null);
    try {
      await updateTicket({
        ticket_id: ticket.id,
        target_state: targetState,
        category,
        priority,
        updated_text: updatedText,
      });
      onUpdated();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="panel ticket-detail">
      <h3>Ticket {ticket.id.slice(0, 8)}</h3>
      <p>
        State: <span className="state-badge">{ticket.state}</span>
        {ticket.user_id ? ` — assigned to ${ticket.user_id}` : ''}
      </p>

      {error && <div className="error-banner">{error}</div>}

      {ticket.state === TicketState.pending ? (
        <button className="primary-button" onClick={handleAcquire} disabled={submitting}>
          {submitting ? 'Acquiring…' : 'Acquire ticket'}
        </button>
      ) : (
        <>
          <label>
            Category
            <select value={category} onChange={(e) => setCategory(e.target.value as Category)}>
              {Object.values(Category).map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label>
            Priority
            <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
              {Object.values(Priority).map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label>
            Suggested answer
            <textarea
              rows={6}
              value={updatedText}
              onChange={(e) => setUpdatedText(e.target.value)}
            />
          </label>

          <label>
            Next state
            <select value={targetState} onChange={(e) => setTargetState(e.target.value as TicketState)}>
              {legalNextStates(ticket.state).map((value) => (
                <option key={value} value={value}>
                  {value === ticket.state ? `${value} (no change)` : value}
                </option>
              ))}
            </select>
          </label>

          <button className="primary-button" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit'}
          </button>
        </>
      )}
    </div>
  );
}
