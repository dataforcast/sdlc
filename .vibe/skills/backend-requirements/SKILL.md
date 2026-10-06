---
name: backend-requirements
description: >
  Use when implementing or reviewing the Python/FastAPI backend, including
  Pydantic API contracts, asynchronous code, outbound HTTP calls, shared
  mutable state, concurrency, database interactions, and external or AI calls.
user-invocable: false
---

##  Backend --- Python / FastAPI

# 1 General rules

- Use Python 3.12+ syntax. 
- Use explicit typing on public interfaces and important internal
    boundaries. 
- Use Pydantic v2 for API request/response models. 
- Keep business/AI logic separate from HTTP endpoint plumbing when useful. 
- Prefer clear functions/classes and small modules over speculative design
    patterns. 
- Do not introduce ABC/Factory/Strategy/Singleton patterns unless they
    solve an actual problem in the exercise.
- Annotations types for all variables
- Add a small docstring for modules, packages, functions
- Use variable name the reflect the variable usage


# 2 API contracts

The backend is the **canonical source of truth** for API contracts.

For structured endpoints:

-   define explicit Pydantic request/response models;
-   declare FastAPI `response_model` where appropriate;
-   do not expose internal persistence/domain objects directly;
-   let FastAPI generate the OpenAPI contract.
-   On application borders, when an attribute is not mutable add key-word `frozen=True`

**Pydantic V2 Requirements:**

-   Use Pydantic V2 exclusively.
-   Replace `@validator` with `@field_validator(mode='before')` for pre-validators.
-   Replace `class Config:` with `model_config = ConfigDict(...)`.
-   These changes eliminate PydanticDeprecatedSince20 warnings.

Example:

``` python
from datetime import datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    # Closed schema AND no attribute reassignment after creation
    id: str
    name: str


class TicketStatus(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True, # Mutable state, but every assignment remains validated
    )
    status: Literal[
        "pending",
        "in_progress",
        "closed",
    ] = Field(
        default="pending",
        description="Ticket status",
    )

    created_at: datetime = Field(
        ...,
        description="Creation timestamp",
    )


class AnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The API response schema is closed
    answer: str
    ticket_status: TicketStatus
    

@app.post("/answer", response_model=AnswerResponse)
async def answer(request: QuestionRequest) -> AnswerResponse:
    ...    
```

# 3 Dependency Management

-   **Use `pyproject.toml` as the single source of truth for dependencies.**
    Do not maintain a separate `requirements.txt` file; it is redundant.
-   `requirements.txt` files should be removed in favor of `pyproject.toml`
    (PEP 621 standard).
-   For HTTP clients in tests: use `httpx2` instead of `httpx` to avoid
    StarletteDeprecationWarning. Ensure `httpx` is uninstalled when using
    `httpx2` to prevent conflicts.
-   When FastAPI/Starlette show deprecation warnings for `httpx`, replace
    the dependency with `httpx2>=2.13.1,<3` in `pyproject.toml`.
-   **When the backend has multiple top-level packages (`api`, `data`, `models`, `services`, etc.),**
    explicitly configure package discovery in `pyproject.toml` to avoid setuptools errors:
    ```toml
    [tool.setuptools.packages.find]
    where = ["."]
    include = ["api*", "data*", "models*", "services*"]
    ```

# 4 Async and HTTP clients

-   Never use `time.sleep()` in async request paths; use
    `asyncio.sleep()`.
-   Do not call `asyncio.run()` from an already running event loop.
-   Use `httpx2.AsyncClient` for async outbound HTTP means, for HTTP requests emitted from backend side towards another service.
-   Reuse a pooled `AsyncClient` when repeated/high-concurrency calls
    justify it.
-   Manage shared clients with application lifespan/startup-shutdown
    lifecycle.
-   Always define sensible timeouts for external calls.
-   Avoid holding database transactions or locks while awaiting slow
    external/LLM calls.

# 4 Concurrency and shared mutable state

When several requests can mutate the same in-memory state:

-   identify the invariant that must remain atomic;
-   protect the **check → compute/mutate → commit** critical section
    when required;
-   use `asyncio.Lock` for mutual exclusion;
-   use `asyncio.Semaphore` when the goal is to bound concurrent access
    rather than enforce single ownership;
-   do not assume an in-process lock protects state across multiple
    processes/replicas.

For a state machine, preserve state-transition atomicity. Do not add a
semaphore merely because code is asynchronous: choose the primitive from
the invariant.

# 5 External/AI calls

For LLM or other external services:

-   validate inputs before the call;
-   use structured outputs when downstream code depends on structure;
-   validate the returned structure before using it;
-   set explicit timeouts;
-   handle provider/network errors explicitly;
-   avoid unsafe execution of model-generated code, SQL, paths, URLs, or
    commands;
-   retry only when the operation is safe/idempotent or protected by an
    idempotency mechanism.

Do not add circuit breakers, complex retry policies, or observability
stacks unless the scenario benefits from them.

------------------------------------------------------------------------

# 6. CORS
Manage CORS allowing frontend to request backend services avoiding the browser CORS lock