import { useState } from 'react';
import { FilterBar } from './components/FilterBar/FilterBar';
import { TicketList } from './components/TicketList/TicketList';
import { TicketDetail } from './components/TicketDetail/TicketDetail';
import { useTickets } from './hooks/useTickets';
import { Category, Priority, TicketState } from './api/generated/models';

export default function App() {
  const { tickets, status, error, refetch } = useTickets();
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [state, setState] = useState('');

  const selectedTicket = tickets.find((ticket) => ticket.id === selectedTicketId) ?? null;

  function handleReset() {
    setSelectedTicketId(null);
    setCategory('');
    setPriority('');
    setState('');
    void refetch();
  }

  function handleApplyFilters() {
    void refetch({
      category: category ? (category as Category) : undefined,
      priority: priority ? (priority as Priority) : undefined,
      state: state ? (state as TicketState) : undefined,
    });
  }

  function handleClearFilters() {
    setCategory('');
    setPriority('');
    setState('');
    void refetch();
  }

  function handleUpdated() {
    void refetch();
  }

  return (
    <div className="app">
      <div className="app-header">
        <h1>Ticket Triage</h1>
        <button className="secondary-button" onClick={handleReset}>
          Reset
        </button>
      </div>

      <FilterBar
        category={category}
        priority={priority}
        state={state}
        onCategoryChange={setCategory}
        onPriorityChange={setPriority}
        onStateChange={setState}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
      />

      <div className="layout">
        <div className="panel">
          <TicketList
            tickets={tickets}
            status={status}
            error={error}
            selectedTicketId={selectedTicketId}
            onSelect={setSelectedTicketId}
          />
        </div>

        <TicketDetail ticket={selectedTicket} onUpdated={handleUpdated} />
      </div>
    </div>
  );
}
