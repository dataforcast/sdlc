/**
 * API client configuration.
 * 
 * This module provides a simple HTTP client for making requests to the backend API.
 * In production, this should be replaced with the Orval-generated client.
 * 
 * For development, you can generate the Orval client by running:
 *   npm run generate
 * 
 * The generated client will be at: src/api/generated/api.client.ts
 */

import type { 
  TicketListResponse, 
  TicketResponse,
  TriageResponse,
  TicketFilterRequest,
  TicketUpdateRequest 
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/backend';

/**
 * Simple HTTP client for making requests to the backend API.
 * This is a fallback client used before Orval generation.
 */
export const apiClient = {
  /**
   * Get list of tickets with optional filtering.
   */
  async getTickets(params?: { category?: string; priority?: string; state?: string }): Promise<TicketListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.priority) queryParams.append('priority', params.priority);
    if (params?.state) queryParams.append('state', params.state);
    
    const response = await fetch(`${API_BASE_URL}/api/tickets?${queryParams.toString()}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch tickets: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Filter tickets using POST request.
   */
  async filterTickets(filter: TicketFilterRequest): Promise<TicketListResponse> {
    const response = await fetch(`${API_BASE_URL}/api/filter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filter),
    });
    if (!response.ok) {
      throw new Error(`Failed to filter tickets: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Update a ticket.
   */
  async updateTicket(update: TicketUpdateRequest): Promise<TicketResponse> {
    const response = await fetch(`${API_BASE_URL}/api/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(update),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to update ticket: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Triage a ticket text.
   */
  async triageTicket(ticketText: string): Promise<TriageResponse> {
    const response = await fetch(`${API_BASE_URL}/api/triage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticket_text: ticketText }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to triage ticket: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check.
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  },
};

export default apiClient;
