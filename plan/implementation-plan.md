# Plan — Customer Ticket Triage Demonstrator

## Context

`specs/specs.md` and `specs/hld.mmd` describe a small internal tool: support
agents see a list of free-text tickets, get an AI-drafted classification
(category/priority) and suggested answer (AI is mocked, not a real LLM), then
acquire, edit and progress a ticket through a 4-state FSM to closure. The
repository is currently greenfield — only the `.claude`/`.vibe` orchestration
config and `specs/` exist; no backend or frontend code exists yet. (A prior
implementation of this exact app existed earlier in this repo's history and
was deleted; it is used below only as a style/convention reference, not as a
requirement source — the binding decisions below supersede it.)

Before planning, four ambiguities were resolved with the stakeholder:

1. **Demo data**: the `scope` skill currently says "build 20 Pokemons" —
   confirmed stale copy-paste artifact. Corrected to **20 mock support
   tickets**, seeded at backend startup.
2. **FSM ↔ UI mapping**: `Acquire` is a dedicated action = `pending→reviewed`
   **and** assigns the ticket to the hardcoded demo user. All further
   transitions (`reviewed→processing`, `processing→closed`, and legal
   self-loops) are chosen from a list of legal next-states on the ticket
   detail view and applied via `Submit`.
3. **Identity**: no auth anywhere. The acting user is a single hardcoded demo
   user id (e.g. `agent-1`), from `.env` — never supplied by the client.
4. **Ticket creation**: `POST /backend/api/triage` is the ticket-creation
   entry point (classifies + drafts + creates a `pending` ticket). The same
   logic seeds 20 tickets internally at startup from canned raw texts.

**Correction applied to the design-agent draft**: the draft introduced a 5th
endpoint, `POST /backend/api/acquire`. specs.md's Technical Requirements
section lists exactly 4 endpoints (`/triage`, `/tickets`, `/update`,
`/filter`) as a closed list — adding a 5th is unrequested scope. Instead,
**`Acquire` is just a client call to `POST /backend/api/update` with
`target_state: "reviewed"`**; the backend auto-assigns the hardcoded demo
user whenever it commits a `pending→reviewed` transition. This keeps the API
surface exactly as specified while preserving the distinct `Acquire`
vs. `Submit` UX the stakeholder asked for.

Two minor non-blocking assumptions (stated, not asked, per project rules):
- Health endpoint path: `GET /backend/health`.
- "Basic project configuration" = env-driven `Settings` object + CORS, not an
  extra endpoint.

---

## Part 1 — File organization

Correct the stale scope text first, in both copies (they're currently
identical):
- `.claude/skills/scope/SKILL.md`
- `.vibe/skills/scope/SKILL.md`

`- Data creation for a demo : build 20 Pokemons` → `- Data creation for a
demo : build 20 support tickets`

Create:

```
sdlc/
├── .env.example                     # single root env template (see vars below)
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, lifespan seeding, CORS, router mounting
│   │   ├── config.py                # pydantic-settings Settings (reads root ../.env)
│   │   ├── models.py                # enums + Ticket + request/response DTOs
│   │   ├── fsm.py                   # ALLOWED_TRANSITIONS, is_transition_allowed, legal_next_states
│   │   ├── mock_ai.py                # MockAIResult + classify_and_draft() — swappable for a real LLM later
│   │   ├── store.py                  # TicketStore: in-memory dict + asyncio.Lock
│   │   ├── service.py                # create_ticket_from_text() shared by /triage and startup seeding
│   │   ├── seed_data.py              # SEED_TICKET_TEXTS: 20 canned raw ticket texts
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py             # GET /backend/health
│   │       └── tickets.py            # /triage, /tickets, /filter, /update
│   └── tests/
│       ├── unit/
│       │   ├── test_fsm.py
│       │   ├── test_mock_ai.py
│       │   ├── test_store_concurrency.py
│       │   └── test_service.py
│       └── api/
│           ├── test_health_api.py
│           ├── test_triage_api.py
│           └── test_tickets_flow_api.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── orval.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── fsm.ts                    # client-side mirror of legal_next_states, UX-only
│   │   ├── hooks/useTickets.ts
│   │   ├── components/
│   │   │   ├── TicketList/{TicketList,TicketRow}.tsx
│   │   │   ├── FilterBar/FilterBar.tsx
│   │   │   └── TicketDetail/TicketDetail.tsx
│   │   └── api/
│   │       ├── generated/            # Orval-owned, never hand-edited
│   │       └── http-client.ts        # axios mutator, baseURL resolution
│   └── tests/integration/api-client.integration.ts
├── scripts/
│   ├── start_app.sh
│   ├── stop_app.sh
│   ├── kill_server.sh
│   ├── run_unit_tests.sh
│   ├── run_backend_api_tests.sh
│   └── run_frontend_backend_integration_tests.sh
└── (existing: .claude/, .vibe/, specs/, doc/, CLAUDE.md, README.md)
```

`.env.example` (root, single source of truth, read by both backend and
frontend via `envDir`):

```
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=5173
CORS_ORIGIN=http://localhost:5173
DEMO_USER_ID=agent-1
API_BASE_URL=http://127.0.0.1:8000
```

`backend/pyproject.toml`: `fastapi`, `pydantic`, `pydantic-settings`,
`uvicorn[standard]`; dev group: `pytest`, `pytest-asyncio`, `httpx2`. Explicit
`[tool.setuptools.packages.find]` for the `app` package. No
`requirements.txt`.

`frontend/package.json`: `react`, `react-dom`, `axios`; dev:
`typescript`, `vite`, `@vitejs/plugin-react`, `orval`, `tsx`. Scripts:
`dev`, `build`, `api:generate`, `test:api-integration`. pnpm as package
manager (nothing pre-existing forces npm/yarn).

---

## Part 2 — Backend implementation

Routers carry their full literal path so OpenAPI (and later Orval) already
match the spec exactly: `health.router = APIRouter(prefix="/backend")`,
`tickets.router = APIRouter(prefix="/backend/api")`.

**`models.py`**: `Category`, `Priority`, `TicketState` enums (`str, Enum`).
`Ticket` — domain record **and** `response_model` (`extra="forbid",
validate_assignment=True`): `id`, `user_id: str | None`, `priority`,
`category`, `updated_text: str`, `state`. Request DTOs (`extra="forbid",
frozen=True`): `TriageRequest{ticket_text: str, min_length=1,
max_length=4000}`, `FilterRequest{category|priority|state|user_id: ... |
None}` (AND-combined, all optional), `UpdateRequest{ticket_id: str,
target_state: TicketState, category|priority: ... | None,
updated_text: str | None}` — deliberately **no `user_id` field**: identity is
never client-supplied. `TicketListResponse{tickets: list[Ticket]}`.
`HealthResponse{status: Literal["ok"]}`.

**`fsm.py`**: `ALLOWED_TRANSITIONS: dict[TicketState, frozenset[TicketState]]`
encoding the 3 real transitions + 4 self-loops from specs.md.
`is_transition_allowed(current, target) -> bool`,
`legal_next_states(current) -> frozenset[TicketState]`. Single source of
truth enforced server-side on every `/update` call — the frontend's picker is
UX only and never trusted.

**`mock_ai.py`**: `MockAIResult{category, priority, draft_text}`
(`extra="forbid", frozen=True`), `classify_and_draft(ticket_text: str) ->
MockAIResult` — deterministic keyword heuristic (not random, so unit tests
are reproducible); output validated through the Pydantic model before use
(never trust generated structure blindly, even mocked). Isolated so a real
LLM call could later replace the body without touching routers/FSM.

**`store.py`**: `TicketStore` — `dict[str, Ticket]` + one `asyncio.Lock`
guarding the whole store. Methods: `add`, `list_all`, `filter`,
`apply_update(ticket_id, target_state, **edits)`. `apply_update` does the
full check (ticket exists, transition legal) → mutate (apply edits, set
state, and if `current == pending and target == reviewed: user_id =
settings.demo_user_id`) → commit, all inside `async with self._lock`.
Raises `TicketNotFoundError` / `InvalidTransitionError`, mapped to 404/409 in
the router.

*Concurrency primitive*: one store-wide lock rather than per-ticket locks.
At this scale (20 tickets, a handful of demo agents) a per-ticket lock dict
would add its own race (dict creation under concurrent `/triage` calls) for
no real benefit; a single lock gives a trivially-correct atomic
check→mutate→commit section. This is the invariant that matters: two
concurrent `/update` calls racing to acquire the same pending ticket must
result in exactly one success.

**`service.py`**: `create_ticket_from_text(store, text)` — runs
`classify_and_draft`, builds a `pending` `Ticket` with `user_id=None`, calls
`store.add`. Used by both `POST /triage` and startup seeding (no duplicated
creation logic).

**`seed_data.py`**: `SEED_TICKET_TEXTS` — 20 varied canned raw texts spanning
billing/technical/account/other and varying urgency.

**Endpoints** (`routers/tickets.py`):

| Method | Path | Request | Response | Errors |
|---|---|---|---|---|
| POST | `/backend/api/triage` | `TriageRequest` | `Ticket` (pending) | 422 |
| GET | `/backend/api/tickets` | — | `TicketListResponse` | — |
| POST | `/backend/api/filter` | `FilterRequest` | `TicketListResponse` | 422 |
| POST | `/backend/api/update` | `UpdateRequest` | `Ticket` | 404, 409, 422 |

`GET /backend/health` → `HealthResponse`.

**`main.py`**: `lifespan` creates `TicketStore` on `app.state.store`, seeds
20 tickets via `create_ticket_from_text` over `SEED_TICKET_TEXTS`;
`CORSMiddleware` allowing `settings.cors_origin`; mounts both routers.
`Depends(get_store)` reads `request.app.state.store` (not a bare module
singleton — keeps test-created app instances isolated).

**`config.py`**: `Settings(BaseSettings)` — `backend_host`, `backend_port`,
`frontend_port`, `cors_origin`, `demo_user_id`; `env_file="../.env"`,
`extra="ignore"`.

**Backend tests**:
- Unit (`backend/tests/unit/`, no server): FSM — every allowed/illegal
  transition incl. self-loops, `closed` terminal; mock AI — keyword
  classification, urgency→high, blank text rejected; store concurrency —
  `asyncio.gather(store.apply_update(id, REVIEWED), store.apply_update(id,
  REVIEWED))` on the same pending ticket: exactly one success (state
  becomes `reviewed`, `user_id` set), the other raises
  `InvalidTransitionError`; service — `create_ticket_from_text` yields
  `pending`/`user_id=None`/populated fields.
- API (`backend/tests/api/`, real server via `httpx2.AsyncClient`): health
  200; triage creates + 422 on blank text; full flow — `GET /tickets`
  returns 20 seeded, `POST /filter`, `POST /update` to `reviewed` (acquire)
  assigns `user_id` + 409 on illegal re-apply from `closed`,
  `reviewed→processing→closed`, 404 unknown ticket, 409 on an illegal jump
  (`pending→processing` directly).

---

## Part 3 — Frontend implementation

`App.tsx` owns `tickets`, `selectedTicketId`, `filters` via plain
`useState`/`useEffect` (no state library — scope is small, avoid an
unapproved dependency). Renders `FilterBar`, `TicketList`, `TicketDetail`,
and a `Reset` control.

- `hooks/useTickets.ts` — wraps generated `getTickets` / `filterTickets`
  calls, exposes `{ tickets, status, error, refetch(filters?) }`.
- `FilterBar` — controlled selects for category/priority/state; `Apply` →
  `refetch(filters)`; `Clear` → `refetch()`. Pure presentation.
- `TicketList`/`TicketRow` — one row per ticket; click selects; explicit
  loading/empty states.
- `TicketDetail` — two modes based on `ticket.state`:
  - `pending`: an **Acquire** button → calls generated `update` with
    `{ ticket_id, target_state: 'reviewed' }`; refresh ticket + list on
    success.
  - otherwise: `legalNextStates(ticket.state)` from `src/fsm.ts` renders a
    target-state picker (including the self-loop, labeled "No change"),
    plus editable `category`/`priority`/`updated_text`, plus **Submit** →
    calls generated `update` with the chosen fields. A 409 from the backend
    (its independent re-validation) surfaces as an inline error.
- `Reset` — local-only: clears `filters`/`selectedTicketId`, re-triggers
  `GET /tickets`. No backend call needed (matches specs.md's listed use
  case, which names no reset endpoint).

`src/fsm.ts` — client-side mirror of `legal_next_states` for UX only
(backend remains authoritative); `TicketState` type is imported from the
Orval-generated models, not redefined, to avoid a parallel contract.

Loading/error/empty states are handled centrally: every async action exposes
`status`/`error`; errors show an inline banner with the backend's `detail`
message rather than being swallowed.

`orval.config.ts`: `input.target` = `${API_BASE_URL}/openapi.json`,
`output.mode: 'single'`, `client: 'axios-functions'`, target
`src/api/generated/client.ts` + `models/`, `override.mutator` pointing at
`src/api/http-client.ts`. After generation, inspect actual exported
function names before writing imports — do not assume them.

`src/api/http-client.ts`: axios instance with `baseURL =
import.meta.env?.VITE_API_BASE_URL ?? process.env.API_BASE_URL ?? ''`
(works both in-browser via Vite and under plain Node/`tsx` for the
integration test).

---

## Part 4 — Backend/frontend integration

**URL composition** (explicit, to avoid path duplication): backend routes
already declare their full literal path (`/backend/api/tickets`, etc.), so
OpenAPI and all generated calls already include `/backend/...`. The Vite
proxy must therefore **not** rewrite:

```ts
// vite.config.ts
server: {
  port: Number(process.env.FRONTEND_PORT ?? 5173),
  proxy: { '/backend': { target: process.env.API_BASE_URL, changeOrigin: true } }, // no rewrite
},
envDir: path.resolve(__dirname, '..'),
```

In the browser, `VITE_API_BASE_URL` is left unset → axios `baseURL=''` →
request to `/backend/api/tickets` → Vite proxy (no rewrite) →
`http://127.0.0.1:8000/backend/api/tickets` → matches the real FastAPI
route. (A rewrite stripping `/backend` here would 404, since the backend
itself still expects that prefix — called out explicitly rather than
assumed away.) Tooling running outside the browser (Orval generation, the
integration test) uses `API_BASE_URL` as a full origin directly.

**Generation workflow**: start backend → `GET /openapi.json` reachable → `cd
frontend && pnpm api:generate` → inspect `src/api/generated/*` (never
hand-edit) → `tsc` typecheck → smoke one call.

**Integration test** (`frontend/tests/integration/api-client.integration.ts`,
run via `tsx`, imports the real generated functions through
`http-client.ts`): `triage(...)` with a `crypto.randomUUID()`-tagged text →
assert `state === 'pending'`; `update(..., target_state: 'reviewed')` →
assert `state === 'reviewed'` and `user_id === DEMO_USER_ID`; `update(...,
'processing')` → assert state; `update(..., 'closed')` → assert state;
negative: `update({ ticket_id: 'unknown', ... })` → `assert.rejects(...)`.

**`scripts/`** (all values sourced from root `.env`, none hard-coded):
- `start_app.sh` — sources `.env`, starts `uv run uvicorn app.main:app
  --app-dir backend --host $BACKEND_HOST --port $BACKEND_PORT` and `(cd
  frontend && pnpm dev -- --port $FRONTEND_PORT)`, both backgrounded, PIDs
  to `.run/*.pid`.
- `stop_app.sh` — reads PID files, `kill` + `wait`, cleans up.
- `kill_server.sh` — frees whatever is bound to `$BACKEND_PORT`.
- `run_unit_tests.sh` — `uv run pytest backend/tests/unit`.
- `run_backend_api_tests.sh` — starts uvicorn in background, polls `GET
  /backend/health` with a bounded timeout, `trap cleanup EXIT`, runs `uv run
  pytest backend/tests/api`.
- `run_frontend_backend_integration_tests.sh` — same start/poll/trap, then
  `cd frontend && API_BASE_URL=http://$BACKEND_HOST:$BACKEND_PORT pnpm run
  test:api-integration`.

---

## Verification

```bash
./scripts/run_unit_tests.sh
./scripts/run_backend_api_tests.sh
./scripts/run_frontend_backend_integration_tests.sh
./scripts/start_app.sh
```

Manual smoke at `http://localhost:$FRONTEND_PORT`: list shows 20 seeded
tickets → filter by category/priority/state → select a ticket → **Acquire**
(`pending→reviewed`, `user_id=agent-1` shown) → edit category/priority/
updated_text → **Submit** `reviewed→processing` → **Submit**
`processing→closed` → **Reset** (filters/selection clear, full list
reloads). Then `./scripts/stop_app.sh`.

After implementation, delegate `backend-reviewer` and `frontend-reviewer`
for focused review of the respective slices, and `quality-reviewer` before
declaring the feature done, per `CLAUDE.md` §9–§11.

### Critical files
`backend/app/store.py`, `backend/app/fsm.py`, `backend/app/routers/tickets.py`,
`backend/app/models.py`, `frontend/orval.config.ts`, `frontend/vite.config.ts`,
`frontend/src/api/http-client.ts`, `scripts/run_backend_api_tests.sh`.
