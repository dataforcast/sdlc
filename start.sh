#!/bin/bash

# Start script for Ticket Processing Application
# This script starts both backend and frontend in development mode

echo "========================================="
echo "  Ticket Processing Application"
echo "========================================="
echo ""

# Check if we should start backend
START_BACKEND=${1:-true}
START_FRONTEND=${2:-true}

# Load environment variables from .env file (single source of truth)
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Set defaults if not defined in .env
BACKEND_PORT=${BACKEND_PORT:-8010}
FRONTEND_PORT=${FRONTEND_PORT:-5173}
VITE_PORT=${VITE_PORT:-$FRONTEND_PORT}
VITE_BACKEND_URL=${VITE_BACKEND_URL:-"http://localhost:${BACKEND_PORT}"}
VITE_API_BASE_URL=${VITE_API_BASE_URL:-"/backend"}

# Export environment variables
export BACKEND_PORT
export FRONTEND_PORT
export VITE_PORT
export VITE_BACKEND_URL
export VITE_API_BASE_URL

# Backend
if [ "$START_BACKEND" = true ]; then
  echo "Starting backend server on port ${BACKEND_PORT}..."
  cd backend
  source venv/bin/activate
  # Add the project root to PYTHONPATH so 'backend' module can be found
  export PYTHONPATH="$PYTHONPATH:.."
  uvicorn app.main:app --reload --port ${BACKEND_PORT} &
  BACKEND_PID=$!
  cd ..
  echo "Backend PID: $BACKEND_PID"
  echo "Backend available at: http://localhost:${BACKEND_PORT}"
  echo "API docs: http://localhost:${BACKEND_PORT}/docs"
  echo ""
fi

# Wait for backend to start
sleep 3

# Frontend
if [ "$START_FRONTEND" = true ]; then
  echo "Starting frontend server on port ${FRONTEND_PORT}..."
  cd frontend
  npm run dev &
  FRONTEND_PID=$!
  cd ..
  echo "Frontend PID: $FRONTEND_PID"
  echo "Frontend available at: http://localhost:${FRONTEND_PORT}"
  echo ""
fi

echo "========================================="
echo "  Application is running!"
echo "========================================="
echo ""
echo "Backend:  http://localhost:${BACKEND_PORT}"
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Trap Ctrl+C to kill all processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for all background processes
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
