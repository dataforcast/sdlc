---
name: testing
description: >
  Use when defining, implementing, running, or reviewing tests and validation
  checks. Organize testing into three explicit levels: backend unit tests,
  running-backend API tests, and frontend/backend integration tests.
  Prioritize core behavior, API contracts, important failure paths, edge cases,
  and concurrency invariants over arbitrary coverage targets.
user-invocable: true
---

# 1. Testing strategy

Tests MUST protect the behavior most likely to break.

Do NOT optimize for an arbitrary coverage percentage unless the brief explicitly
requires one.

Prioritize:

1. core backend behavior;
2. backend API request/response contracts;
3. important failure cases;
4. functional edge cases;
5. concurrency invariants when concurrency is part of the scenario;
6. frontend/backend API integration;
7. critical frontend behavior only when required by the exercise.

Prefer focused tests that can be executed quickly during development and during
a live coding interview.

The project testing strategy is divided into three levels:

```text
Level 1 — Unit tests
    ↓
backend modules in isolation

Level 2 — Backend API tests
    ↓
running backend server
    ↓
HTTP API

Level 3 — Frontend / backend integration tests
    ↓
running backend server
    ↓
frontend API client
    ↓
HTTP API
```

Each test level MUST have a dedicated shell script under:

```text
scripts/
```

with an explicit and self-explanatory name.


# 2. Required test scripts

Prefer the following naming convention:

```text
scripts/
├── run_unit_tests.sh
├── run_backend_api_tests.sh
└── run_frontend_backend_integration_tests.sh
└── kill_server.sh  <- killing server PID allowing to reload script without the change of the port 

```
**No hard-coded** variables into shell scripts. All variables to be extracted from `.env` file.

If the repository already has an established naming convention, preserve it.

The intent of each script MUST remain immediately understandable from its name.

Do NOT create one generic script whose behavior depends on undocumented
arguments when three explicit scripts provide clearer intent.


# 3. Level 1 — Backend unit tests

## 3.1 Purpose

Unit tests validate backend modules independently from the running HTTP server.

Typical targets include:

```text
domain logic
services
state machines
parsers
validators
repositories with test doubles
utility functions
business rules
concurrency-sensitive components
```

Unit tests SHOULD be fast and deterministic.


## 3.2 Server independence

Unit tests MUST NOT require the backend server to be started.

They should exercise Python modules directly.

For example:

```python
async def test_ticket_can_be_acquired():
    service = TicketService(...)

    result = await service.acquire("ticket-1")

    assert result.status == "processing"
```


# 4. Unit test priorities

For each important backend behavior, test:

- expected behavior;
- significant invalid input;
- important boundary condition;
- state transition when applicable;
- relevant business invariant.

Avoid writing many trivial tests that provide little confidence.


# 5. Concurrency unit tests

If a backend component is expected to handle concurrent operations, a
sequential test is NOT sufficient.

The test MUST schedule competing operations concurrently.

For example:

```python
results = await asyncio.gather(
    service.acquire(ticket_id),
    service.acquire(ticket_id),
)
```

or use:

```python
asyncio.TaskGroup
```

when appropriate.

Validate the actual concurrency invariant.

Examples:

```text
only one worker can acquire a ticket

shared state never enters an invalid state

duplicate concurrent requests do not create duplicate resources

a semaphore actually limits access to a critical section
```

Do NOT claim concurrency safety based only on sequential tests.


# 6. Running unit tests

Unit tests MUST be runnable through:

```bash
./scripts/run_unit_tests.sh
```

The script SHOULD reuse the project environment and dependency-management
strategy already present in the repository.

For a project using `uv`, for example:

```bash
#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

uv run pytest backend/tests/unit
```

Adapt test paths and commands to the actual repository.

Do NOT introduce a second Python environment manager solely for testing.


# 7. Level 2 — Backend API tests

## 7.1 Purpose

Backend API tests validate the real HTTP interface exposed by the backend.

Unlike unit tests, they MUST start the backend server.

The test boundary is:

```text
API test client
    ↓
HTTP
    ↓
running backend server
    ↓
FastAPI routes
    ↓
backend implementation
```

These tests validate the backend API independently from the frontend.


# 8. Backend API test workflow

The backend API test script MUST perform:

```text
1. Start backend services
        ↓
2. Wait until backend is ready
        ↓
3. Run backend API tests
        ↓
4. Stop backend services
```

The complete workflow MUST be executable through:

```bash
./scripts/run_backend_api_tests.sh
```


# 9. Start the real backend

Use the repository's existing backend startup mechanism.

Examples include:

```bash
uv run uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000
```

or:

```bash
./scripts/start_backend.sh
```

when such a script already exists.

Do NOT create Docker, Kubernetes, or additional orchestration solely to execute
these tests unless the project already requires them.


# 10. Backend readiness

Do NOT use an arbitrary fixed delay such as:

```bash
sleep 5
```

as the primary readiness mechanism.

Poll a deterministic readiness endpoint.

Prefer:

```text
GET /health
```

when available.

Otherwise, for FastAPI:

```text
GET /openapi.json
```

is acceptable for determining that the HTTP application is ready.

Example:

```bash
until curl --fail --silent \
    http://127.0.0.1:8000/openapi.json > /dev/null
do
    sleep 0.2
done
```

The readiness loop MUST have a bounded timeout.

A failed backend startup MUST cause the test script to fail rather than wait
forever.


# 11. Backend API tests

Backend API tests SHOULD use an HTTP client such as `httpx` when already
available in the project.

Example:

```python
async def test_get_ticket():
    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:8000",
    ) as client:

        response = await client.get("/api/tickets/ticket-1")

    assert response.status_code == 200

    payload = response.json()

    assert payload["id"] == "ticket-1"
```

These tests MAY call HTTP directly because their purpose is specifically to
validate the backend HTTP API.


# 12. Backend API contract validation

Backend API tests SHOULD validate representative aspects of the contract:

- HTTP method;
- route path;
- path parameters;
- query parameters;
- request body;
- response status;
- response body;
- validation errors;
- relevant headers when required;
- significant error cases.

When useful, validate a complete API flow rather than isolated endpoints.

For example:

```text
create
    ↓
read
    ↓
update
    ↓
verify resulting state
```


# 13. Backend API negative tests

Include important failure cases when they materially protect the contract.

Examples:

```text
invalid input            → 422
unknown resource         → 404
conflicting state        → 409
unauthorized request     → 401 / 403
```

Use the behavior actually specified by the application.

Do NOT invent error semantics merely to satisfy a testing template.


# 14. Backend API process cleanup

The backend process MUST be stopped even when tests fail.

Use a shell cleanup trap.

Example:

```bash
#!/usr/bin/env bash

set -euo pipefail

BACKEND_PID=""

cleanup() {
    if [[ -n "${BACKEND_PID}" ]]; then
        kill "${BACKEND_PID}" 2>/dev/null || true
        wait "${BACKEND_PID}" 2>/dev/null || true
    fi
}

trap cleanup EXIT
```

Do not leave stale backend processes after test execution.


# 15. Level 3 — Frontend / backend integration tests

## 15.1 Purpose

Integration tests validate that the frontend API client correctly communicates
with the running backend.

The test boundary is:

```text
TypeScript integration test
        ↓
frontend/api/client.ts
        ↓
Orval-generated client if applicable
        ↓
HTTP
        ↓
running backend server
```

The objective is NOT to test React rendering.

The objective is to validate the real contract between the frontend API layer
and the backend.


# 16. Integration test workflow

The integration test script MUST execute:

```text
1. Start backend services
        ↓
2. Wait until backend is ready
        ↓
3. Launch TypeScript integration client
        ↓
4. Call backend through frontend/api/client.ts
        ↓
5. Validate responses and behavior
        ↓
6. Stop backend services
```

The complete workflow MUST be executable through:

```bash
./scripts/run_frontend_backend_integration_tests.sh
```


# 17. Use the real frontend API module

The TypeScript integration test MUST import the API module used by the frontend
application.

For example:

```ts
import {
  acquireTicket,
  getTicket,
} from '../../api/client';
```

Adapt imports to the actual repository.

Do NOT bypass:

```text
frontend/api/client.ts
```

by writing parallel test-only calls with:

```ts
fetch(...)
```

or:

```ts
axios(...)
```

when the application itself uses the API client module.

Otherwise the test would validate only the backend and would fail to detect
frontend API integration problems.


# 18. Why the integration test must use the frontend client

The integration test should detect failures such as:

```text
incorrect generated Orval import

incorrect generated operation name

incorrect operation arguments

incorrect API wrapper implementation

wrong Axios configuration

wrong backend base URL

incorrect response.data handling

incorrect serialization

stale generated OpenAPI client

frontend/backend contract mismatch
```

A direct HTTP call from the integration test would bypass many of these
failure modes.


# 19. TypeScript integration test location

A recommended location is:

```text
frontend/tests/integration/api-client.integration.ts
```

or another location compatible with the repository.

Do NOT reorganize an existing frontend test structure solely to match this
example.


# 20. TypeScript integration test

Create a small executable TypeScript client.

Example:

```ts
import assert from 'node:assert/strict';

import {
  acquireTicket,
  getTicket,
} from '../../api/client';

async function main(): Promise<void> {
  const ticketId = `integration-${crypto.randomUUID()}`;

  const acquired = await acquireTicket(ticketId);

  assert.ok(acquired);
  assert.equal(acquired.id, ticketId);

  const ticket = await getTicket(ticketId);

  assert.ok(ticket);
  assert.equal(ticket.id, ticketId);
}

main().catch((error) => {
  console.error(
    'Frontend/backend integration test failed:',
    error,
  );

  process.exit(1);
});
```

Operation names, input parameters, and assertions MUST match the actual API.

Never invent exports.

Inspect the frontend API module and generated client first.


# 21. Integration base URL

The TypeScript test usually runs outside the browser and therefore outside the
Vite development proxy.

Do NOT assume that a browser-relative route such as:

```text
/api
```

will automatically reach the backend.

The frontend API client SHOULD support a configurable backend URL.

For example:

```text
API_BASE_URL=http://127.0.0.1:8000
```

The integration script can then execute:

```bash
API_BASE_URL=http://127.0.0.1:8000 \
npm run test:api-integration
```

or the equivalent command provided by the project's package manager.

Do NOT change production behavior solely to make tests pass.


# 22. Integration test assertions

At least one representative application API flow SHOULD be tested end-to-end.

Prefer a meaningful business operation over a health check.

For example:

```text
acquire ticket
    ↓
read ticket
    ↓
verify state
```

Validate as appropriate:

- request succeeds;
- expected response is returned;
- required fields are present;
- expected values are correct;
- backend state changed correctly;
- API wrapper returns the expected application-level type.


# 23. Integration negative test

When practical, validate at least one significant error path through the
frontend API client.

For example:

```ts
await assert.rejects(
  () => getTicket('unknown-ticket'),
);
```

The purpose is to ensure that backend HTTP failures are correctly propagated or
transformed by the frontend API layer.


# 24. Integration test isolation

Integration tests MUST NOT depend on resources created by previous executions.

Prefer:

```text
unique resource IDs

explicit setup

explicit cleanup

temporary or in-memory test state
```

For example:

```ts
const ticketId = `integration-${crypto.randomUUID()}`;
```

when the API supports client-provided identifiers.


# 25. Integration test runner

A representative shell script is:

```bash
#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

BACKEND_PID=""

cleanup() {
    if [[ -n "${BACKEND_PID}" ]]; then
        kill "${BACKEND_PID}" 2>/dev/null || true
        wait "${BACKEND_PID}" 2>/dev/null || true
    fi
}

trap cleanup EXIT

cd "${ROOT_DIR}"

uv run uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 &

BACKEND_PID=$!

for _ in {1..50}; do
    if curl --fail --silent \
        http://127.0.0.1:8000/openapi.json \
        > /dev/null
    then
        break
    fi

    sleep 0.2
done

curl --fail --silent \
    http://127.0.0.1:8000/openapi.json \
    > /dev/null

cd frontend

API_BASE_URL=http://127.0.0.1:8000 \
npm run test:api-integration
```

This is an example only.

Adapt:

- backend startup command;
- Python package location;
- HTTP port;
- readiness endpoint;
- frontend path;
- environment variables;
- package manager;

to the actual repository.


# 26. Frontend integration test command

If no suitable command exists, expose one in the frontend package scripts.

For example:

```json
{
  "scripts": {
    "test:api-integration":
      "tsx tests/integration/api-client.integration.ts"
  }
}
```

Reuse existing tooling.

If the frontend already uses:

```text
Vitest
tsx
Node TypeScript execution
```

do not introduce another test runner unnecessarily.


# 27. Test responsibilities

Keep the three levels conceptually separate.

## Unit tests

```text
Python module
    ↓
Python module
```

No running HTTP server.


## Backend API tests

```text
Python HTTP test client
    ↓
HTTP
    ↓
running backend
```

No frontend client involved.


## Frontend/backend integration tests

```text
TypeScript test
    ↓
frontend/api/client.ts
    ↓
generated client
    ↓
HTTP
    ↓
running backend
```

Do not collapse these three levels into equivalent tests.


# 28. Avoid redundant tests

Do not duplicate exactly the same assertions at all three levels.

Each level should protect a different boundary.

For example:

```text
Unit test
    → state-machine transition is correct

Backend API test
    → POST /tickets/{id}/acquire exposes that behavior correctly

Integration test
    → frontend API client can successfully invoke that operation
```

This gives stronger confidence than repeating the same implementation-level
test three times.


# 29. Failure diagnosis

When a test fails, identify the earliest broken layer.


## Unit test failure

Inspect:

```text
business logic
state management
validation
concurrency
```


## Backend API test failure

Inspect:

```text
backend startup
route
request validation
backend service
response model
HTTP status
```


## Integration test failure

Inspect:

```text
backend readiness
OpenAPI contract
Orval-generated client
frontend/api/client.ts
generated function signature
base URL
Axios configuration
HTTP request
backend response
response extraction
```


# 30. Test environment

Test scripts SHOULD:

- use the dependency management already selected by the project;
- execute from deterministic paths;
- fail immediately when a command fails;
- return a non-zero exit status on test failure;
- clean up processes they started;
- avoid hidden manual setup;
- avoid requiring an IDE to execute tests.

For shell scripts, prefer:

```bash
set -euo pipefail
```

unless there is a concrete reason not to use it.

Do NOT reinstall all dependencies on every test execution unless the project
explicitly requires an isolated environment.

Environment setup and test execution are different concerns.


# 31. Definition of Done — Unit tests

Unit testing is complete when:

- important backend modules are tested directly;
- significant success and failure paths are covered;
- relevant edge cases are covered;
- concurrency is tested with actual concurrent execution when required;
- no backend HTTP server is required;
- tests run through:

```bash
./scripts/run_unit_tests.sh
```


# 32. Definition of Done — Backend API tests

Backend API testing is complete when:

- the real backend server is started automatically;
- readiness is checked deterministically;
- representative API operations are called through HTTP;
- request and response contracts are validated;
- important failure cases are tested;
- backend processes are always cleaned up;
- tests run through:

```bash
./scripts/run_backend_api_tests.sh
```


# 33. Definition of Done — Integration tests

Frontend/backend integration testing is complete when:

- the backend server is started automatically;
- readiness is checked;
- a TypeScript test imports the real frontend API module;
- the test uses `frontend/api/client.ts`;
- the generated client is exercised when applicable;
- at least one representative business API flow reaches the running backend;
- returned values are validated;
- failures return a non-zero exit status;
- backend processes are cleaned up;
- tests run through:

```bash
./scripts/run_frontend_backend_integration_tests.sh
```


# 34. Final validation sequence

Before considering the implementation complete, run:

```bash
./scripts/run_unit_tests.sh

./scripts/run_backend_api_tests.sh

./scripts/run_frontend_backend_integration_tests.sh
```

The expected validation chain is:

```text
backend modules
      ✓
      ↓
backend HTTP API
      ✓
      ↓
frontend API client ↔ backend
      ✓
```

Passing integration tests does NOT make unit tests unnecessary.

Passing unit tests does NOT prove that the HTTP API works.

Passing backend API tests does NOT prove that the frontend client correctly
consumes the API.


# 35. Core invariant

Maintain the following separation:

```text
UNIT
backend module
    ↓
backend module


BACKEND API
HTTP test client
    ↓
running backend


INTEGRATION
TypeScript test
    ↓
frontend/api/client.ts
    ↓
Orval-generated API
    ↓
HTTP
    ↓
running backend
```

Each layer validates a distinct boundary.

Use the simplest test that validates the boundary being tested.