/**
 * API types for the ticket processing application.
 * These types should match the backend Pydantic models.
 */

// Enums matching backend Category, Priority, State
export type Category = 'billing' | 'technical' | 'account' | 'other';
export type Priority = 'low' | 'medium' | 'high';
export type State = 'pending' | 'reviewed' | 'processing' | 'closed';

// Ticket domain model
export interface Ticket {
  id: string;
  userId: string | null;
  priority: Priority;
  category: Category;
  text: string;
  updatedText: string | null;
  state: State;
}

// Request models
export interface TicketFilterRequest {
  category?: Category;
  priority?: Priority;
  state?: State;
}

// Local type for frontend filter state (matches TicketFilterRequest)
export type TicketFilter = {
  category?: Category;
  priority?: Priority;
  state?: State;
};

export interface TicketUpdateRequest {
  ticket_id: string;
  user_id?: string;
  state?: State;
  updated_text?: string;
}

export interface TriageRequest {
  ticketText: string;
}

// Response models
export interface HealthResponse {
  status: string;
  version: string;
}

export interface TicketResponse {
  id: string;
  userId: string | null;
  priority: Priority;
  category: Category;
  text: string;
  updatedText: string | null;
  state: State;
}

export interface TicketListResponse {
  tickets: TicketResponse[];
}

export interface TriageResponse {
  category: Category;
  priority: Priority;
  suggestedAnswer: string;
}

// Error response
export interface ErrorResponse {
  detail: string;
}
