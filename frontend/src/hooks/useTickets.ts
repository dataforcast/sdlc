import { useCallback, useEffect, useState } from 'react';
import { filterTickets, listTickets } from '../api/generated/client';
import type { FilterRequest, Ticket } from '../api/generated/models';

type Status = 'idle' | 'loading' | 'success' | 'error';

export interface UseTicketsResult {
  tickets: Ticket[];
  status: Status;
  error: string | null;
  refetch: (filters?: FilterRequest) => Promise<void>;
}

function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { detail?: unknown } } }).response;
    if (response?.data?.detail) {
      return String(response.data.detail);
    }
  }
  return 'Unable to reach the backend. Please try again.';
}

export function useTickets(): UseTicketsResult {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [status, setStatus] = useState<Status>('idle');
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async (filters?: FilterRequest) => {
    setStatus('loading');
    setError(null);
    try {
      const result =
        filters && Object.values(filters).some((value) => value !== undefined)
          ? await filterTickets(filters)
          : await listTickets();
      setTickets(result.tickets);
      setStatus('success');
    } catch (err) {
      setError(extractErrorMessage(err));
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  return { tickets, status, error, refetch };
}
