---
name: git
description: >
  Use before creating a Git commit or when reviewing repository changes.
  Inspect the diff, exclude secrets and generated dependency directories,
  run relevant fast checks, and use a concise conventional commit message.
user-invocable: true
---

# Git discipline

Do not commit unless explicitly requested or useful to the tasks/steps workflow.

Before a commit:

- inspect the diff; 
- ensure no secret or generated dependency directory is included; 
- run the relevant fast checks; 
- use a concise conventional commit message.

Never commit `.env` files containing real values, `.venv/`,
`node_modules/`, or agent-private directives files such as the one into `.vibe` folder.

# Git messages
- Commit messages must be approved by the user before
  committing and pushing
- No `Co-Authored-By` or references to a co-author in
  commit messages
------------------------------------------------------------------------
