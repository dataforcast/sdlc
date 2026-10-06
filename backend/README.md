# Ticket Processing Backend

This is the backend API for the Ticket Processing Application, built with FastAPI.

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Run the application
uvicorn app.main:app --reload --port 8000

# Access the API
- Health check: http://localhost:8000/backend/health
- API docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

# Run tests
pytest
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/backend/health` | Health check endpoint |
| GET | `/backend/api/tickets` | List all tickets with optional filters |
| POST | `/backend/api/filter` | Filter tickets by criteria |
| POST | `/backend/api/update` | Update a ticket (state, user, text) |
| POST | `/backend/api/triage` | Classify ticket text using AI |

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application entry point
│   ├── api/
│   │   └── endpoints/    # API endpoint modules
│   │   └── models/       # Pydantic request/response models
│   └── core/
│       ├── models/       # Domain models
│       ├── services/     # Business logic services
│       └── fsm/          # Finite State Machine implementation
├── pyproject.toml       # Project configuration and dependencies
└── tests/               # Test suite
```

## Business Logic

All business logic is implemented in the backend, following these principles:

### Ticket States (FSM)
- `pending` → `reviewed` → `processing` → `closed`
- All states can self-transition (e.g., `pending` → `pending`)
- Invalid transitions are rejected with a 400 error

### Ticket Model
- `id`: Unique identifier
- `user_id`: Assigned agent ID
- `priority`: low, medium, high
- `category`: billing, technical, account, other
- `text`: Original ticket text
- `updated_text`: AI-generated or agent response
- `state`: Current state in lifecycle

## Dependencies

- FastAPI 0.104.0+
- Pydantic 2.5.0+
- Uvicorn 0.24.0+
- pytest 7.4.0+ (for development)
- httpx 0.25.0+ (for testing)
