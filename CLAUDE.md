## Project

AI Telegram community management platform.

Multi-bot, multi-chat, policy-driven backend with:
- moderation
- join request screening
- marketplace rules
- domain-restricted assistant (RAG)
- approval workflow
- admin chat control plane for moderator interaction

Telegram ingestion uses polling in development and initial production setup.
Core logic must remain transport-agnostic so webhook support can be added later without changing domain or application layers.

See @README.md for full overview, @docs/architecture.md for system design, and @docs/security.md for security requirements.


## Architecture - IMPORTANT

YOU MUST follow these rules:

- Telegram layer is thin (no business logic)
- All logic goes through orchestrator -> engines -> decisions -> actions
- Engines NEVER perform side effects
- Telegram API calls ONLY inside transport/execution layer
- No direct DB access from transport handlers/runners
- Behavior is policy-driven (bot_id + chat_id + policy_profile)
- Do NOT hardcode behavior per chat
- Core logic must not depend on polling-specific implementation details

## Transport Model - IMPORTANT

- Telegram updates are received via polling
- Polling is an ingestion mechanism only
- Polling code must only fetch updates, normalize them, and pass them into application flow
- Do NOT place business logic inside polling loops
- Design transport so webhook ingestion can be added later without changing orchestrators, engines, decisions, or actions

## Admin Interaction Model - IMPORTANT

Human-in-the-loop interaction is implemented via a dedicated private Telegram admin chat.

Admin chat is used only when moderator involvement is required.

Two execution modes must exist:

- automatic flow:
  decision -> action

- approval flow:
  decision -> approval -> admin chat -> action

Whether approval is required must be decided by policy and decision logic, not by transport code.

Admin chat may also be used later for:
- moderator notifications
- operational controls
- bot management commands

Rules:
- Do NOT route all actions through admin chat
- Use admin chat only when approval or moderator interaction is required
- Do NOT place business logic inside admin callback handlers
- Always validate admin identity and callback payload
- Callback handlers must map to stored approval requests or known control actions
- Approval must remain an optional gate before action execution

## LLM Usage - IMPORTANT

- Deterministic logic ALWAYS first
- Use LLM ONLY for:
  - ambiguous moderation
  - join request classification
  - assistant answers (RAG)

Never use LLM for:
- simple rules
- rate limits
- routing logic
- basic policy checks

## Assistant Constraints

- Assistant is domain-restricted
- Must NOT answer outside knowledge base
- If unsure -> decline
- No hallucination
- Retrieval must stay scoped to configured knowledge base

## Approval Rules

- Risky actions may require approval depending on policy
- Typical approval-required actions:
  - bans
  - join rejections
  - low-confidence AI decisions
- Actions must be stored before approval
- Execution must be idempotent
- Actions that do not require approval must execute directly
- Admin chat is the approval interface, not the source of policy decisions
- Approval workflow details are defined in @docs/approval.md

## Code Style

- Python 3.11+
- Use type hints everywhere
- Prefer explicit over magic
- No god classes
- No utils dumping
- Prefer simple, readable abstractions over generic frameworks

## Project Structure

Follow this structure:

- transport (telegram polling, future webhook ingress, execution, admin chat callbacks)
- application (orchestrators, services)
- domain (entities, events, decisions, actions)
- engines (business logic)
- infrastructure (db, redis, qdrant, openai)

Do NOT mix layers.

## Workflow

After any non-trivial change:

- run tests for changed modules (not full suite unless needed)
- ensure imports are clean
- ensure types are correct

Prefer small, isolated changes over large rewrites.

## Development Rules

- Do NOT implement entire system at once
- Work in small vertical slices (end-to-end flows)
- Do NOT add speculative abstractions
- Do NOT introduce new dependencies without reason
- Do NOT build webhook-specific core abstractions yet
- Keep polling implementation production-usable but replaceable

## Development Environment - IMPORTANT

- All development must use a local Python virtual environment (venv)
- Do NOT install dependencies globally
- Assume project is run inside an activated virtual environment

When suggesting commands:
- prefer `python -m venv .venv`
- use `.venv/bin/python` or activated shell
- do not rely on system Python packages

## Security - IMPORTANT

- NEVER expose API keys or secrets in code
- Always use environment variables for secrets
- Always validate and sanitize external input
- Use parameterized queries (no raw SQL string building)
- Treat Telegram updates as untrusted input until validated
- Treat admin callback data as untrusted input until validated
- Do not log secrets or full sensitive payloads

## API & Limits

- Always consider rate limiting for public or abuse-prone logic
- Avoid unbounded operations (loops, queries, API calls)
- Polling loops must handle retries, backoff, and duplicate safety carefully

## Data & Storage

- PostgreSQL = source of truth
- Redis = cache / rate limit / ephemeral state
- Qdrant = vector search only

No business logic in Redis.


## Observability

- Log all decisions (structured)
- Use correlation_id per event/update
- All moderation / approval actions must be auditable
- Polling failures and retry behavior must be observable
- Admin approvals and rejections must be auditable


## Logging

- Log critical actions (moderation, bans, approvals)
- Do NOT log secrets or sensitive data
- Do NOT log raw bot tokens or raw authorization data


## Common Mistakes to Avoid

- putting logic in polling loops
- skipping orchestrator layer
- calling Telegram API from domain/engines
- overusing LLM
- hardcoding chat-specific behavior
- coupling core logic to transport mode
- routing all actions through admin chat
- trusting callback payloads without authorization checks


## Definition of Done

Feature is done when:

- works end-to-end
- follows architecture rules
- minimal tests exist
- no layer violations
- no unnecessary abstractions
- does not couple core logic to polling-specific flow
- does not make admin chat mandatory for actions that should be automatic