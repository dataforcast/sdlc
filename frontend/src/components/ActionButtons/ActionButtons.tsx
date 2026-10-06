/**
 * ActionButtons component - provides action buttons for the UI.
 */

import React from 'react';
import type { Ticket } from '../../types/api';

interface Props {
  onReset: () => void;
  selectedTicket: Ticket | null;
  isProcessing: boolean;
}

export const ActionButtons: React.FC<Props> = ({ onReset, selectedTicket, isProcessing }) => {
  return (
    <div className="action-buttons" data-testid="action-buttons">
      <button
        onClick={onReset}
        disabled={!selectedTicket || isProcessing}
        className="btn btn-secondary"
        data-testid="reset-button"
      >
        Reset View
      </button>
    </div>
  );
};

export default ActionButtons;
