/**
 * Custom hook for managing tickets state and operations.
 */

import { useState, useEffect, useCallback } from 'react';
import type { Ticket, TicketFilter, TicketUpdateRequest } from '../types/api';
import { apiClient } from '../api/client';

const CURRENT_USER_ID = 'agent-001';

export interface UseTicketsReturn {
  tickets: Ticket[];
  selectedTicket: Ticket | null;
  filters: TicketFilter;
  loading: boolean;
  error: string | null;
  setFilters: (filter: TicketFilter) => void;
  setSelectedTicket: (ticket: Ticket | null) => void;
  acquireTicket: (ticketId: string) => Promise<void>;
  updateTicket: (update: TicketUpdateRequest) => Promise<void>;
  resetState: () => void;
  refreshTickets: () => Promise<void>;
}

export const useTickets = (): UseTicketsReturn => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [filters, setFilters] = useState<TicketFilter>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getTickets({
        category: filters.category,
        priority: filters.priority,
        state: filters.state,
      });
      setTickets(response.tickets);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tickets');
      console.error('Error fetching tickets:', err);
    } finally {
      setLoading(false);
    }
  }, [filters.category, filters.priority, filters.state]);

  const acquireTicket = useCallback(async (ticketId: string) => {
    if (!selectedTicket) return;
    
    setLoading(true);
    setError(null);
    try {
      await apiClient.updateTicket({
        ticket_id: ticketId,
        user_id: CURRENT_USER_ID,
        state: 'reviewed',
      });
      // Refresh the list and update selected ticket
      await fetchTickets();
      setSelectedTicket(prev => prev ? { ...prev, userId: CURRENT_USER_ID, state: 'reviewed' } : null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to acquire ticket');
      console.error('Error acquiring ticket:', err);
    } finally {
      setLoading(false);
    }
  }, [fetchTickets, selectedTicket]);

  const updateTicket = useCallback(async (update: TicketUpdateRequest) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.updateTicket(update);
      await fetchTickets();
      // Update selected ticket if it matches
      if (selectedTicket && selectedTicket.id === update.ticket_id) {
        setSelectedTicket(prev => {
          if (!prev) return null;
          return {
            ...prev,
            userId: update.user_id || prev.userId,
            state: update.state || prev.state,
            updatedText: update.updated_text || prev.updatedText,
          };
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update ticket');
      console.error('Error updating ticket:', err);
    } finally {
      setLoading(false);
    }
  }, [fetchTickets, selectedTicket]);

  const resetState = useCallback(() => {
    setSelectedTicket(null);
    setFilters({});
    setError(null);
  }, []);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  return {
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
    refreshTickets: fetchTickets,
  };
};

export default useTickets;
