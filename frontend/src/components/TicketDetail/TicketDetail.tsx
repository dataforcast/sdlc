/**
 * TicketDetail component - displays full details of a selected ticket.
 */

import React, { useState } from 'react';
import type { Ticket, State } from '../../types/api';

interface Props {
  ticket: Ticket;
  onAcquire: () => void;
  onUpdate: (updatedText: string) => void;
  onStateChange: (newState: State) => void;
  canAcquire: boolean;
  isProcessing: boolean;
}

export const TicketDetail: React.FC<Props> = ({
  ticket,
  onAcquire,
  onUpdate,
  onStateChange,
  canAcquire,
  isProcessing,
}) => {
  const [updatedText, setUpdatedText] = useState(ticket.updatedText || '');
  const [aiSuggestion, setAiSuggestion] = useState<string>('');

  const handleUseAISuggestion = () => {
    setUpdatedText(aiSuggestion);
  };

  const handleTriage = async () => {
    // In a production implementation, this would call the triage endpoint
    // For now, we'll just set a mock suggestion
    setAiSuggestion(`Suggested response for ticket "${ticket.text.substring(0, 50)}..."`);
  };

  const handleSave = () => {
    onUpdate(updatedText);
  };

  return (
    <div className="ticket-detail" data-testid="ticket-detail">
      <div className="ticket-detail-header">
        <h2>Ticket #{ticket.id}</h2>
        <div className="ticket-actions-header">
          {canAcquire && (
            <button
              onClick={onAcquire}
              disabled={isProcessing}
              className="btn btn-acquire"
              data-testid="acquire-button"
            >
              {isProcessing ? 'Acquiring...' : 'Acquire Ticket'}
            </button>
          )}
        </div>
      </div>

      <div className="ticket-metadata" data-testid="ticket-metadata">
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">Category:</span>
            <span className="value">{ticket.category}</span>
          </div>
          <div className="metadata-item">
            <span className="label">Priority:</span>
            <span className={`value priority-${ticket.priority}`}>{ticket.priority}</span>
          </div>
          <div className="metadata-item">
            <span className="label">State:</span>
            <span className={`value state-${ticket.state}`}>{ticket.state}</span>
          </div>
          {ticket.userId && (
            <div className="metadata-item">
              <span className="label">Assigned to:</span>
              <span className="value">{ticket.userId}</span>
            </div>
          )}
        </div>
      </div>

      <div className="ticket-section">
        <h3>Original Request</h3>
        <div className="ticket-text" data-testid="ticket-text">{ticket.text}</div>
      </div>

      <div className="ticket-section">
        <h3>AI Assistance</h3>
        <button onClick={handleTriage} className="btn btn-secondary" data-testid="triage-button">
          Generate AI Response
        </button>
        {aiSuggestion && (
          <div className="ai-suggestion" data-testid="ai-suggestion">
            <p>{aiSuggestion}</p>
            <button onClick={handleUseAISuggestion} className="btn btn-small" data-testid="use-suggestion-button">
              Use this response
            </button>
          </div>
        )}
      </div>

      <div className="ticket-section">
        <h3>Response</h3>
        <textarea
          value={updatedText}
          onChange={(e) => setUpdatedText(e.target.value)}
          placeholder="Enter your response or use AI-generated suggestion..."
          className="response-textarea"
          data-testid="response-textarea"
        />
      </div>

      <div className="ticket-actions">
        <button
          onClick={handleSave}
          disabled={isProcessing}
          className="btn btn-primary"
          data-testid="save-button"
        >
          {isProcessing ? 'Saving...' : 'Save Response'}
        </button>

        <div className="state-selector">
          <span>Change State:</span>
          <select
            value={ticket.state}
            onChange={(e) => onStateChange(e.target.value as State)}
            disabled={isProcessing || !ticket.userId}
            className="state-select"
            data-testid="state-select"
          >
            <option value="pending">Pending</option>
            <option value="reviewed">Reviewed</option>
            <option value="processing">Processing</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;
