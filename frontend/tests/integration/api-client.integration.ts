import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { getHealth, triage, updateTicket } from '../../src/api/generated/client';
import { TicketState } from '../../src/api/generated/models';

const DEMO_USER_ID = process.env.DEMO_USER_ID ?? 'agent-1';

async function main(): Promise<void> {
  const health = await getHealth();
  assert.equal(health.status, 'ok');

  const ticketText = `integration-${randomUUID()} cannot access billing invoice, this is urgent`;
  const created = await triage({ ticket_text: ticketText });
  assert.equal(created.state, TicketState.pending);
  assert.equal(created.user_id, null);

  const acquired = await updateTicket({
    ticket_id: created.id,
    target_state: TicketState.reviewed,
  });
  assert.equal(acquired.state, TicketState.reviewed);
  assert.equal(acquired.user_id, DEMO_USER_ID);

  const processing = await updateTicket({
    ticket_id: created.id,
    target_state: TicketState.processing,
  });
  assert.equal(processing.state, TicketState.processing);

  const closed = await updateTicket({
    ticket_id: created.id,
    target_state: TicketState.closed,
  });
  assert.equal(closed.state, TicketState.closed);

  await assert.rejects(() =>
    updateTicket({ ticket_id: 'unknown-ticket', target_state: TicketState.reviewed }),
  );

  console.log('Frontend/backend integration test passed.');
}

main().catch((error) => {
  console.error('Frontend/backend integration test failed:', error);
  process.exit(1);
});
