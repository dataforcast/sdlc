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

# Backend
if [ "$START_BACKEND" = true ]; then
  echo "Starting backend server on port 8000..."
  cd backend
  source venv/bin/activate
  uvicorn app.main:app --reload --port 8000 &
  BACKEND_PID=$!
  cd ..
  echo "Backend PID: $BACKEND_PID"
  echo "Backend available at: http://localhost:8000"
  echo "API docs: http://localhost:8000/docs"
  echo ""
fi

# Wait for backend to start
sleep 3

# Frontend
if [ "$START_FRONTEND" = true ]; then
  echo "Starting frontend server on port 5173..."
  cd frontend
  npm run dev &
  FRONTEND_PID=$!
  cd ..
  echo "Frontend PID: $FRONTEND_PID"
  echo "Frontend available at: http://localhost:5173"
  echo ""
fi

echo "========================================="
echo "  Application is running!"
echo "========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Trap Ctrl+C to kill all processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for all background processes
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
