# IMPLEMENTATION PLAN: Customer Ticket Processing Application

---

## **Context Summary**
- **Objective**: Build an internal application helping support agents classify incoming free-text requests and draft AI-generated answers
- **Architecture**: Monorepository with Frontend (React+TypeScript+Vite) → Backend (FastAPI) → Core Business Logic
- **Key Principle**: ALL business logic resides in the backend

---

---

# **PART 1: Setup the File Organization**

## **1.1 Repository Structure**
```
sdlc-2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── tickets.py   # Ticket CRUD endpoints
│   │   │   │   ├── triage.py    # AI classification endpoint
│   │   │   │   └── filter.py    # Filter endpoint
│   │   │   └── models/
│   │   │       ├── request.py   # Pydantic request models
│   │   │       └── response.py  # Pydantic response models
│   │   ├── core/
│   │   │   ├── models/
│   │   │   │   └── ticket.py    # Domain models (Ticket, Category, Priority, State enums)
│   │   │   ├── services/
│   │   │   │   ├── ticket_service.py  # Business logic
│   │   │   │   └── ai_service.py     # AI integration
│   │   │   └── fsm/
│   │   │       └── state_machine.py  # FSM implementation
│   │   └── config.py
│   ├── pyproject.toml
│   └── tests/
│       ├── test_api.py
│       └── test_core.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TicketList/
│   │   │   │   ├── TicketList.tsx
│   │   │   │   └── TicketRow.tsx
│   │   │   ├── TicketDetail/
│   │   │   │   └── TicketDetail.tsx
│   │   │   ├── FilterControls/
│   │   │   │   └── FilterControls.tsx
│   │   │   └── ActionButtons/
│   │   │       └── ActionButtons.tsx
│   │   ├── hooks/
│   │   │   └── useTickets.ts
│   │   ├── types/
│   │   │   └── api.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── App.tsx
│   │   └── App.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── orval.config.js
│
├── specs/
│   ├── specs.md
│   └── hld.mmd
├── plan/
│   └── implementation-plan.md
└── .gitignore
```

## **1.2 Configuration Files**
| File | Purpose |
|------|---------|
| `backend/pyproject.toml` | Python project config and dependencies |
| `frontend/package.json` | Frontend dependencies |
| `frontend/tsconfig.json` | TypeScript config |
| `frontend/vite.config.ts` | Vite config with proxy |
| `frontend/orval.config.js` | Orval API client config |
| `.gitignore` | Exclude node_modules, __pycache__, venv |

## **1.3 Deliverables**
- [ ] Complete directory structure created
- [ ] Configuration files for backend and frontend
- [ ] Git repository initialized

---

---

# **PART 2: Make Backend Implementation**

## **2.1 Core Domain Models** (`backend/app/core/models/ticket.py`)
```python
from dataclasses import dataclass
from enum import Enum

class Category(str, Enum): BILLING, TECHNICAL, ACCOUNT, OTHER
class Priority(str, Enum): LOW, MEDIUM, HIGH
class State(str, Enum): PENDING, REVIEWED, PROCESSING, CLOSED

@dataclass
class Ticket:
    id: str, user_id: Optional[str], priority: Priority
    category: Category, text: str, updated_text: Optional[str]
    state: State = State.PENDING
```

## **2.2 FSM Implementation** (`backend/app/core/fsm/state_machine.py`)
```python
ALLOWED_TRANSITIONS = {
    State.PENDING: {State.PENDING, State.REVIEWED},
    State.REVIEWED: {State.REVIEWED, State.PROCESSING},
    State.PROCESSING: {State.PROCESSING, State.CLOSED},
    State.CLOSED: {State.CLOSED},
}

def validate_transition(current: State, new: State) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())
```

## **2.3 API Models** (`backend/app/api/models/`)
- **Request**: `TicketFilterRequest`, `TicketUpdateRequest`, `TriageRequest`
- **Response**: `TicketResponse`, `TicketListResponse`, `TriageResponse`, `HealthResponse`

## **2.4 Service Layer** (`backend/app/core/services/`)
- **TicketService**: CRUD operations, FSM validation, filtering
- **AIService**: Mock triage implementation (classify + generate response)

## **2.5 API Endpoints** (`backend/app/api/endpoints/`)
- `GET /backend/api/tickets` - List tickets with optional filters
- `POST /backend/api/filter` - Filter tickets
- `POST /backend/api/update` - Update ticket with FSM validation
- `POST /backend/api/triage` - AI classification
- `GET /backend/health` - Health check

## **2.6 Main Application** (`backend/app/main.py`)
FastAPI app with all routers included and sample data initialization.

## **2.7 Tests** (`backend/tests/`)
- Unit tests for FSM transitions
- Unit tests for service layer
- API tests using TestClient

## **2.8 Deliverables**
- [ ] Domain models with enums
- [ ] FSM implementation
- [ ] Service layer (TicketService, AIService)
- [ ] REST API endpoints
- [ ] Health endpoint
- [ ] Pydantic models
- [ ] Backend tests
- [ ] OpenAPI schema (auto-generated)

---

---

# **PART 3: Make Frontend Implementation**

## **3.1 Type Definitions** (`frontend/src/types/api.ts`)
TypeScript types matching backend models (Ticket, Category, Priority, State, etc.)

## **3.2 API Client** (`frontend/src/api/client.ts`)
Orval-generated client from OpenAPI schema.

## **3.3 Custom Hooks** (`frontend/src/hooks/useTickets.ts`)
- `useTickets()` hook for managing tickets, filters, selection, loading, errors
- Methods: `fetchTickets`, `acquireTicket`, `updateTicket`, `filterTickets`, `resetState`

## **3.4 Components**

### **TicketList & TicketRow** (`frontend/src/components/TicketList/`)
- Display list of tickets with 1 row per ticket
- Show priority, category, state, text
- Highlight selected ticket

### **TicketDetail** (`frontend/src/components/TicketDetail/`)
- Full ticket display
- AI assistance button
- Response textarea
- State selector
- Acquire/Save buttons

### **FilterControls** (`frontend/src/components/FilterControls/`)
- Dropdown filters for category, priority, state
- Clear filters button

### **ActionButtons** (`frontend/src/components/ActionButtons/`)
- Reset UI state button

## **3.5 Main App** (`frontend/src/App.tsx`)
- Integrates all components
- Implements all user journeys
- Handles loading/error states

## **3.6 Styling** (`frontend/src/App.css`)
- Responsive layout (list + detail side-by-side)
- Color coding for priority/state
- Loading spinner
- Error banners

## **3.7 Deliverables**
- [ ] TypeScript types
- [ ] Orval API client
- [ ] Custom hooks
- [ ] Component library
- [ ] Main App component
- [ ] CSS styling
- [ ] Loading/error handling

---

---

# **PART 4: Make Backend/Frontend Integration**

## **4.1 Contract Flow**
```
Backend Pydantic Models → FastAPI Endpoints → OpenAPI Schema → 
Orval TypeScript Client → Frontend Components
```

## **4.2 OpenAPI Generation**
Backend automatically generates OpenAPI at `/backend/openapi.json`

## **4.3 Orval Configuration** (`frontend/orval.config.js`)
Generates TypeScript client from OpenAPI schema.

## **4.4 Integration Testing**
- Manual end-to-end testing of all user journeys
- Validate FSM transitions work across layers
- Verify type safety between backend/frontend

## **4.5 Development Workflow**
```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run generate && npm run dev

# Tests
cd backend && pytest
```

## **4.6 Validation Checklist**
| Check | Backend | Frontend | Integration |
|-------|---------|----------|-------------|
| API endpoints work | ✅ | - | ✅ |
| OpenAPI schema | ✅ | - | ✅ |
| Orval client | - | ✅ | ✅ |
| Types match | ✅ | ✅ | ✅ |
| FSM transitions | ✅ | - | ✅ |
| Filtering | ✅ | ✅ | ✅ |
| Acquisition flow | ✅ | ✅ | ✅ |
| Update flow | ✅ | ✅ | ✅ |
| Reset UI | - | ✅ | ✅ |
| Loading/error | - | ✅ | ✅ |

## **4.7 Deliverables**
- [ ] OpenAPI schema
- [ ] Orval TypeScript client
- [ ] Type safety across layers
- [ ] End-to-end testing
- [ ] Working dev workflow

---

---

# **IMPLEMENTATION ROADMAP**

## **Phase 1: Foundation**
1. Create directory structure
2. Initialize backend (Python) and frontend (Node.js)
3. Create configuration files

## **Phase 2: Backend**
1. Implement domain models and FSM
2. Create service layer
3. Implement API endpoints
4. Write tests

## **Phase 3: Frontend**
1. Define types
2. Set up Orval
3. Create hooks and components
4. Add styling

## **Phase 4: Integration**
1. Generate API client
2. Test end-to-end
3. Validate all requirements

---

---

# **DEPENDENCIES**

## Backend (`backend/pyproject.toml`)
```toml
[project]
name = "ticket-backend"
version = "1.0.0"
description = "Ticket processing backend API"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "python-multipart",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "httpx>=0.25.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

## Frontend (`frontend/package.json`)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.0.0",
    "orval": "^6.0.0"
  }
}
```

---

---

# **ACCEPTANCE CRITERIA ALIGNMENT**

## Functional Requirements
| Requirement | Location | Verification |
|-------------|----------|--------------|
| List tickets (1 row per) | Frontend TicketList | Visual |
| Filter by attributes | Frontend + Backend | E2E test |
| Select ticket displayed | Frontend TicketDetail | Visual |
| Acquire ticket | Frontend + Backend | E2E test |
| Submit updated ticket | Frontend + Backend | E2E test |
| Reset UI state | Frontend | Visual |

## Technical Requirements
| Requirement | Location | Verification |
|-------------|----------|--------------|
| Health endpoint | Backend | API test |
| Business logic in backend | Backend services | Code review |
| FastAPI | Backend | Architecture |
| React + TS + Vite | Frontend | Architecture |

## API Endpoints
| Endpoint | Location | Verification |
|----------|----------|--------------|
| POST /backend/api/triage | Backend triage.py | API test |
| GET /backend/api/tickets | Backend tickets.py | API test |
| POST /backend/api/update | Backend tickets.py | API test |
| POST /backend/api/filter | Backend filter.py | API test |

## Data Model
| Requirement | Location | Verification |
|-------------|----------|--------------|
| Ticket structure | Backend models | Code review |
| Category/Priority/State enums | Backend/Frontend | Code review |

## FSM Transitions
| Transition | Location | Verification |
|------------|----------|--------------|
| pending → reviewed | Backend FSM | Unit test |
| reviewed → processing | Backend FSM | Unit test |
| processing → closed | Backend FSM | Unit test |
| All self-transitions | Backend FSM | Unit test |

---

---

# **NEXT STEPS**

To begin implementation:

```bash
# Create structure
mkdir -p backend/app/api/endpoints backend/app/api/models backend/app/core/models backend/app/core/services backend/app/core/fsm backend/tests
mkdir -p frontend/src/components/TicketList frontend/src/components/TicketDetail frontend/src/components/FilterControls frontend/src/components/ActionButtons frontend/src/hooks frontend/src/types frontend/src/api

# Initialize projects
cd backend && python -m venv venv && source venv/bin/activate && pip install -e .[dev]
cd frontend && npm install
```

Then proceed with Part 2 (Backend Implementation).

---

*Plan generated based on specifications in `./specs/specs.md` and High-Level Design in `./specs/hld.mmd`*
