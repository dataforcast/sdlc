# Ticket Processing Frontend

This is the frontend application for the Ticket Processing system, built with React, TypeScript, and Vite.

## Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Generate API client from backend OpenAPI schema
# First, make sure backend is running on port 8000
npm run generate

# Start development server
npm run dev

# Access the application
# http://localhost:5173

# Build for production
npm run build
```

## Features

- **Ticket List**: Display all tickets in a scrollable list with 1 row per ticket
- **Filtering**: Filter tickets by category, priority, and state
- **Ticket Detail**: Select a ticket to view full details including:
  - Ticket metadata (category, priority, state, assigned user)
  - Original request text
  - AI assistance with generated suggestions
  - Response textarea for agent input
  - State transition controls
- **Ticket Acquisition**: Agents can acquire tickets to work on them
- **State Management**: Full FSM-compliant state transitions
- **Reset**: Reset UI state to start fresh

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── TicketList/  # Ticket list and row components
│   │   ├── TicketDetail/# Full ticket view and editing
│   │   ├── FilterControls/ # Filter dropdown controls
│   │   └── ActionButtons/ # UI action buttons
│   ├── hooks/           # Custom React hooks
│   │   └── useTickets.ts # Main ticket management hook
│   ├── types/           # TypeScript type definitions
│   │   └── api.ts       # API types matching backend
│   ├── api/            # API client configuration
│   │   └── client.ts   # HTTP client for backend API
│   ├── App.tsx         # Main application component
│   ├── App.css         # Main application styles
│   └── main.tsx        # Application entry point
├── package.json         # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration
├── vite.config.ts      # Vite configuration with proxy
└── orval.config.js     # Orval API client generator config
```

## API Integration

The frontend communicates with the backend API at `/backend/` by default. The Vite development server is configured with a proxy to forward `/backend/*` requests to `http://localhost:8000`.

### API Client

A simple HTTP client is provided in `src/api/client.ts` with methods for:
- `getTickets()` - List tickets with optional filters
- `filterTickets()` - POST filter request
- `updateTicket()` - Update ticket state, user, or text
- `triageTicket()` - Classify ticket text using AI
- `healthCheck()` - Verify backend is running

### Orval Integration (Optional)

For better type safety, you can generate a TypeScript client from the backend's OpenAPI schema using Orval:

```bash
npm run generate
```

This creates generated types and client in `src/api/generated/`.

## User Journeys

1. **View Tickets**: Tickets are automatically loaded and displayed in a list
2. **Filter Tickets**: Use dropdown controls to filter by category, priority, or state
3. **Select Ticket**: Click on any ticket to view its full details
4. **Acquire Ticket**: Click "Acquire Ticket" to assign it to yourself (transitions to reviewed state)
5. **Update State**: Use the state dropdown to change the ticket state (following FSM rules)
6. **Add Response**: Enter text in the response area and click "Save Response"
7. **Reset**: Click "Reset View" to clear selection and filters

## Dependencies

- React 18.2.0+
- TypeScript 5.0.0+
- Vite 4.0.0+
- @tanstack/react-query 5.0.0+
- Orval 6.0.0+ (optional, for API client generation)
