---
name: security-config
description: >
  Use when implementing or reviewing configuration, secrets, user inputs,
  LLM outputs, SQL, URLs, file paths, authentication, or authorization.
  Apply the security checklist before considering the solution complete.
---

# 1. Configuration and secrets

-   Never hard-code real secrets.
-   Use environment variables for API keys, tokens, password... and environment-specific
    configuration.
-   Provide placeholders in .env file for environment variables. Do not hard-code any env. variable such as server port, URL...

------------------------------------------------------------------------

# 2. Security checklist

**Security fixes take priority over cosmetic improvements**.

Before considering the solution complete, check the relevant items:

- Validate user input;
- Apply Pydantic validation on application borders
- Never commit or print API keys/secrets;
- Keep secrets in environment variables;
- Do not expose secrets to the frontend;
- Do not trust LLM-generated structured data without validation;
- Do not execute LLM-generated shell/code/SQL directly;
- Parameterize database queries;
- Constrain arbitrary URLs/file paths when they can reach privileged resources;
- Apply authentication/authorization if explicitly required by the requirements.

**IMPORTANT**
- Check that all external dependencies have not been hallucinated for avoiding `slopsquatting`
------------------------------------------------------------------------
