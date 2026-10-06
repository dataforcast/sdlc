---
name: frontend-requirements
description: >
  Use when implementing or reviewing a React and TypeScript frontend,
  including API access, generated OpenAPI types, frontend state handling,
  component responsibilities, runtime errors, and backend/frontend contract
  consistency.
---

> This skill is intended to auto-trigger by context (e.g., when implementing or reviewing
> React/TypeScript frontend code); it is not meant to be invoked ad hoc by name.

# 1. Frontend --- React / TypeScript

------------------------------------------------------------------------

## 1.1 General rules

When the starter uses React + TypeScript:

-   follow its existing tooling (Vite if not provided);
-   keep components focused on presentation and interaction;
-   centralize backend calls in an API/client module;
-   model loading, success, empty, and error states explicitly;
-   avoid `any` when a useful type is available.

------------------------------------------------------------------------

## 1.2 Backend/frontend contract

Maintain this invariant:

``` text
Pydantic models
    ↓
FastAPI endpoints + response_model
    ↓
OpenAPI
    ↓
TypeScript types/client
    ↓
Frontend API layer
    ↓
React components
```

Do not independently maintain two divergent definitions of the same API
contract.

When practical within the current scope:

-   generate TypeScript types/client from `/openapi.json`;
-   use generated types in the frontend.

If code generation would consume disproportionate implementation time, derive
the minimum frontend type needed from the OpenAPI contract, explicitly
note the trade-off, and keep the API layer centralized. Do not pretend
compile-time TypeScript typing validates runtime JSON.

Use runtime validation (for example Zod) only when justified by the
scenario or external/untrusted responses.
------------------------------------------------------------------------

## 1.3 Error handling

The frontend API layer should:

-   check non-2xx responses;
-   map expected API errors into useful UI states;
-   avoid silently swallowing malformed responses;
-   present a usable error message to the user.

------------------------------------------------------------------------
