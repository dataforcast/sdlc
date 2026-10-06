---
name: dod
description: >
  Use before declaring a feature complete or preparing the final demo.
  Validate the current Definition of Done and project-specific acceptance
  criteria against the implemented user journey. Re-read after requirement
  or scope changes.
---

# Definition of done

A feature is done when:

- The requested user journey works end to end;
- Request/response contracts are coherent;
- The main failure path is handled;
- Relevant tests/checks pass;
  - All unit tests passed successfully
  - All backend tests passed successfully
  - All integration tests passed successfully
- No obvious secret/security issue remains;
- The solution is ready to demonstrate.

# Acceptance criteria
Acceptance criteria validate the implementation along with intents into specifications

## Checking against intents
Check intents from specification and ensure that :
- All unit tests reflect parts of intents
- All backend tests reflect use cases scenario
## Shell script
- Write a shell script `./scripts/start_app.sh` for launching both frontend + backend
- Write a shell script `./scripts/stop_app.sh` for halting both frontend + backend
## Checking against skills
- Check that implementation is compliant with all requirements contained into `SKILL.md` files

# Important
- Do not spend time polishing non-essential architecture while the main journey is incomplete.
