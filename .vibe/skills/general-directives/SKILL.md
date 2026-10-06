---
name: general-directives
description: >
  Use to apply the baseline operating rules: inspect the starter first, clarify material ambiguities,
  debug before editing, preserve ownership of generated code, process
  progressive instructions, and prioritize a working demonstrable solution.
user-invocable: false
---

# Parent Agent Directives

# 1. Operating principles --- READ FIRST

---

## 1.1 Respect the provided starter

- The provided repository is the starting point and source of truth. 
- Understand current architecture by reviewing the existing structure, dependencies, scripts, conventions and tests before changing architecture.
- Do not replace the starter architecture unless there is a concrete blocking reason. 
- Prefer the smallest coherent change that satisfies the current instruction. 
- Progressive instructions override assumptions made
    earlier.
---
## 1.2 Clarify before implementing when ambiguity matters

Before a significant implementation step:

1.  Restate the requested behavior in 1--3 sentences.
2.  Identify only ambiguities that could materially change the
    implementation.
3.  Ask concise clarification questions when needed. 
4. After any clarification:
      5. Review and update scope if necessary 
      6. Update DoD / acceptance criteria if necessary 
      7. Compare the new requirement with current implementation
      8. Identify the delta 
      9. Implement only that delta
6. Run the narrowest relevant tests
4.  State the proposed minimal implementation plan. 
5.  Ask for agreement for implementation  
6.  Repeat steps 1. to 5. for each step.

Do not block on minor ambiguity: make a reasonable assumption, state it,
and keep moving.

---

## 1.3 Debug before editing

When a test or runtime error occurs:

1.  Read the error literally.
2.  Identify the failing execution path.
3.  State the two most likely root cause.
4.  Propose the smallest fix and a more robust alternative.
5.  Apply it and rerun the narrowest relevant check.

Do not make unrelated refactors while debugging.


---
## 1.4 Maintain ownership of AI-generated code

For every meaningful generated change, be able to explain:

-   what changed;
-   why it is needed;
-   the data/control flow;
-   important trade-offs;
-   failure modes;
-   how it was validated.

Never accept generated code solely because it compiles.

---
## 1.5 Progressive-instruction rule

Instructions may be provided progressively.

After each new instruction:

1.  Compare it with the current implementation;
2.  Identify what changes and what remains valid;
3.  Update the smallest necessary slice;
4.  Rerun the narrowest relevant checks;
5.  Keep the application demonstrable.

Do not prematurely implement speculative future requirements.

------------------------------------------------------------------------

# 2. Required toolchain

Follow the interview environment requirements:

-   Python **3.12+**;
-   `uv` for Python dependency/environment management when compatible
    with the starter;
-   Node.js;
-   `pnpm` for frontend dependency management when compatible with the
    starter;

Do not introduce an alternative package manager without a concrete
reason.

If the starter already defines commands, prefer those commands.


------------------------------------------------------------------------

# 3. Priority order

Time is running out, prioritize:

``` text
working end-to-end flow
> correctness
> security
> API contract
> error handling
> focused tests
> UX clarity
> architecture refinement
> infrastructure / deployment polish
```

The objective is not to produce the largest codebase. The objective is
to deliver, understand, validate, and explain a practical AI-powered
full-stack solution.

------------------------------------------------------------------------
# 4. General Acceptance criteria

Before declaring a feature complete, validate it against the current DoD skill.

# 5 Important
Do not spend time polishing non-essential architecture while the main journey is incomplete.
