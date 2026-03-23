# Security Guidelines (for Claude)

This document defines security constraints that MUST be followed when generating or modifying code in this project.

It focuses only on code-level behavior and decisions relevant to a polling-based Telegram backend with admin chat interaction.

## Core Rules - IMPORTANT

- Never expose secrets in code, logs, or responses
- Always treat external input as untrusted
- Never trust model output without validation
- Prefer safe defaults (deny over allow)
- Avoid implicit behavior in security-sensitive logic

## Secrets Handling

- Use environment variables for all secrets
- Never hardcode:
  - API keys
  - bot tokens
  - passwords
  - DSNs
- Never log secrets
- Never include secrets in exceptions or debug output

## Input Validation

All external input must be validated.

Includes:
- Telegram updates received via polling
- user messages
- callback data
- join request data
- admin or external payloads

Rules:
- validate type and structure
- enforce reasonable length limits
- reject malformed input early
- do not rely on Telegram or client behavior as sufficient validation

## Telegram Polling Safety

Polling is the current transport model.

Rules:
- keep polling logic separate from business logic
- treat all fetched updates as untrusted until validated
- track update offsets safely
- avoid duplicate processing
- handle retries and failures explicitly
- do not create unbounded polling loops without backoff or error handling
- do not let transport failures corrupt application state

## Database Safety

- Always use parameterized queries
- Never build SQL via string concatenation
- Do not expose sensitive internal fields unless required
- Keep write operations explicit and auditable for risky actions

## Authorization

- Always enforce access control on backend
- Never rely on UI-level restrictions
- Explicitly check permissions for sensitive actions

Sensitive actions include:
- bans
- moderation overrides
- approval decisions
- configuration changes
- admin control actions

## Admin Chat Safety

Some actions are executed through admin chat approval or moderator interaction.

Requirements:
- approval via admin chat must apply only to actions marked as requiring approval or to explicit admin control actions
- always verify that callback user_id belongs to an authorized admin or moderator
- callback actions must be validated against stored approval requests or known control commands
- never trust callback data without validation
- never allow callbacks to bypass policy or authorization checks
- callback data must not contain sensitive secrets
- admin chat visibility is not a security boundary by itself

## Rate Limiting & Abuse Safety

- Consider rate limiting for all abuse-prone or externally triggered logic
- Avoid unbounded loops, queries, or retries
- Prevent easy abuse of:
  - AI-triggered flows
  - join flows
  - message-triggered logic
  - polling retry behavior
  - admin-triggered action loops

## AI-Specific Constraints

- Do not treat LLM output as trusted
- Validate or constrain model-generated decisions
- Do not allow assistant to operate outside defined scope
- Avoid sending unnecessary sensitive data to external AI APIs
- Apply deterministic guards before executing risky AI-informed actions

## Logging

- Log critical actions:
  - moderation decisions
  - bans
  - approvals
  - approval rejections
  - admin-triggered control actions
- Use structured logging where possible
- Never log secrets or sensitive tokens
- Do not log full raw Telegram payloads unless explicitly needed and safely filtered

## File Handling (if applicable)

- Validate file type, not only extension
- Enforce file size limits
- Reject unexpected formats
- Treat imported KB files as untrusted until validated

## Dependency Usage

- Do not introduce new dependencies unless necessary
- Prefer standard library or existing project dependencies
- If adding a library, ensure it is justified and relevant

## Final Check

Before implementing or modifying code, ensure:

- input is validated
- secrets are not exposed
- queries are safe
- authorization is enforced
- risky operations are controlled
- duplicate update handling is considered
- admin callbacks are authorized and validated
- no obvious abuse vectors exist