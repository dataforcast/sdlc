/**
 * FilterControls component - provides filtering controls for tickets.
 */

import React from 'react';
import type { TicketFilter, Category, Priority, State } from '../../types/api';

interface Props {
  filters: TicketFilter;
  onFilterChange: (filter: TicketFilter) => void;
}

const categories: Category[] = ['billing', 'technical', 'account', 'other'];
const priorities: Priority[] = ['low', 'medium', 'high'];
const states: State[] = ['pending', 'reviewed', 'processing', 'closed'];

const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const FilterControls: React.FC<Props> = ({ filters, onFilterChange }) => {
  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as Category;
    onFilterChange({ ...filters, category: value || undefined });
  };

  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as Priority;
    onFilterChange({ ...filters, priority: value || undefined });
  };

  const handleStateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as State;
    onFilterChange({ ...filters, state: value || undefined });
  };

  const handleClear = () => {
    onFilterChange({});
  };

  const hasActiveFilters = Object.keys(filters).length > 0;

  return (
    <div className="filter-controls" data-testid="filter-controls">
      <h3>Filters</h3>
      <div className="filter-group">
        <label htmlFor="category-filter">Category:</label>
        <select
          id="category-filter"
          value={filters.category || ''}
          onChange={handleCategoryChange}
          data-testid="category-filter"
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{capitalizeFirst(cat)}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="priority-filter">Priority:</label>
        <select
          id="priority-filter"
          value={filters.priority || ''}
          onChange={handlePriorityChange}
          data-testid="priority-filter"
        >
          <option value="">All Priorities</option>
          {priorities.map(pri => (
            <option key={pri} value={pri}>{capitalizeFirst(pri)}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="state-filter">State:</label>
        <select
          id="state-filter"
          value={filters.state || ''}
          onChange={handleStateChange}
          data-testid="state-filter"
        >
          <option value="">All States</option>
          {states.map(state => (
            <option key={state} value={state}>{capitalizeFirst(state)}</option>
          ))}
        </select>
      </div>

      {hasActiveFilters && (
        <button onClick={handleClear} className="btn btn-clear" data-testid="clear-filters-button">
          Clear Filters
        </button>
      )}
    </div>
  );
};

export default FilterControls;
