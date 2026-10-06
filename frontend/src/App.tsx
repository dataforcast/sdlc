/**
 * Main App component - integrates all components and provides the user interface.
 */

import React from 'react';
import { useTickets } from './hooks/useTickets';
import { TicketList } from './components/TicketList';
import { TicketDetail } from './components/TicketDetail';
import { FilterControls } from './components/FilterControls';
import { ActionButtons } from './components/ActionButtons';
import type { State } from './types/api';
import './App.css';

const CURRENT_USER_ID = 'agent-001';

export const App: React.FC = () => {
  const {
    tickets,
    selectedTicket,
    filters,
    loading,
    error,
    setFilters,
    setSelectedTicket,
    acquireTicket,
    updateTicket,
    resetState,
  } = useTickets();

  const handleAcquire = async () => {
    if (selectedTicket) {
      await acquireTicket(selectedTicket.id);
    }
  };

  const handleUpdate = async (updatedText: string) => {
    if (selectedTicket) {
      await updateTicket({
        ticket_id: selectedTicket.id,
        updated_text: updatedText,
        user_id: CURRENT_USER_ID,
      });
    }
  };

  const handleStateChange = async (newState: State) => {
    if (selectedTicket) {
      await updateTicket({
        ticket_id: selectedTicket.id,
        state: newState,
        user_id: CURRENT_USER_ID,
      });
    }
  };

  const canAcquire = selectedTicket?.userId !== CURRENT_USER_ID &&
                    selectedTicket?.state !== 'closed';

  return (
    <div className="app" data-testid="app">
      <header className="app-header" data-testid="app-header">
        <h1>🎫 Ticket Processing</h1>
        <p className="subtitle">Support Agent Dashboard</p>
      </header>

      <main className="app-main" data-testid="app-main">
        {error && (
          <div className="error-banner" data-testid="error-banner">
            {error}
            <button onClick={() => window.location.reload()} className="btn btn-small">
              Retry
            </button>
          </div>
        )}

        <div className="controls-row" data-testid="controls-row">
          <FilterControls
            filters={filters}
            onFilterChange={setFilters}
          />
          <ActionButtons
            onReset={resetState}
            selectedTicket={selectedTicket}
            isProcessing={loading}
          />
        </div>

        {loading && !tickets.length ? (
          <div className="loading" data-testid="loading">
            <div className="spinner"></div>
            <p>Loading tickets...</p>
          </div>
        ) : (
          <div className="content-row" data-testid="content-row">
            <div className="ticket-list-container" data-testid="ticket-list-container">
              <TicketList
                tickets={tickets}
                onSelect={setSelectedTicket}
                selectedId={selectedTicket?.id}
              />
            </div>

            {selectedTicket && (
              <div className="ticket-detail-container" data-testid="ticket-detail-container">
                <TicketDetail
                  ticket={selectedTicket}
                  onAcquire={handleAcquire}
                  onUpdate={handleUpdate}
                  onStateChange={handleStateChange}
                  canAcquire={canAcquire}
                  isProcessing={loading}
                />
              </div>
            )}
          </div>
        )}

        {!selectedTicket && tickets.length > 0 && (
          <div className="hint" data-testid="hint">
            Select a ticket from the list to view and process it.
          </div>
        )}
      </main>

      <footer className="app-footer" data-testid="app-footer">
        <p>Ticket Processing Application v1.0.0</p>
      </footer>
    </div>
  );
};

export default App;
