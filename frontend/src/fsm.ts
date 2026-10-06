import type { TicketState } from './api/generated/models';

// Client-side mirror of backend/app/fsm.py, for UX only (picker options,
// disabling obviously-illegal choices). The backend independently
// re-validates every transition; this list is never authoritative.
export const TICKET_STATE_TRANSITIONS: Record<TicketState, TicketState[]> = {
  pending: ['pending', 'reviewed'],
  reviewed: ['reviewed', 'processing'],
  processing: ['processing', 'closed'],
  closed: ['closed'],
};

export function legalNextStates(state: TicketState): TicketState[] {
  return TICKET_STATE_TRANSITIONS[state];
}
