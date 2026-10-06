import { Category, Priority, TicketState } from '../../api/generated/models';

interface FilterBarProps {
  category: string;
  priority: string;
  state: string;
  onCategoryChange: (value: string) => void;
  onPriorityChange: (value: string) => void;
  onStateChange: (value: string) => void;
  onApply: () => void;
  onClear: () => void;
}

export function FilterBar({
  category,
  priority,
  state,
  onCategoryChange,
  onPriorityChange,
  onStateChange,
  onApply,
  onClear,
}: FilterBarProps) {
  return (
    <div className="filter-bar">
      <select value={category} onChange={(e) => onCategoryChange(e.target.value)}>
        <option value="">All categories</option>
        {Object.values(Category).map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>

      <select value={priority} onChange={(e) => onPriorityChange(e.target.value)}>
        <option value="">All priorities</option>
        {Object.values(Priority).map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>

      <select value={state} onChange={(e) => onStateChange(e.target.value)}>
        <option value="">All states</option>
        {Object.values(TicketState).map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>

      <button className="secondary-button" onClick={onApply}>
        Apply filters
      </button>
      <button className="secondary-button" onClick={onClear}>
        Clear filters
      </button>
    </div>
  );
}
