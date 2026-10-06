---
name: scope
description: >
  Use before planning or modifying the implementation to apply the current
  exercise-specific scope, exclusions, dependency constraints, and explicit
  implementation boundaries. Re-read whenever the interviewer changes or
  clarifies the requirements.
user-invocable: true
---

# SCOPE

- Do not implement tests for the User Interface
- Do not add dependencies except those striclty required for this implementation
- Avoid business logic into front-end unless it is required 
- No hard-coded variables; variables to be located into `.env` file
- Do not use any LLM; Use a mock to simulate the content of the LLM response
- No authentification neither authorization features
- No data persistence into database, "In memory" persistence
- Use `pyproject.toml` as the single source of truth for dependencies; do not maintain `requirements.txt` and remove it if present.
- Data creation for a demo : build 20 Pokemons