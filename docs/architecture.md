# Architecture

## Overview

This system is a policy-driven backend platform for managing Telegram communities.

It supports:
- multiple bots
- multiple chats
- per-chat behavior configuration
- AI-assisted decision workflows
- optional human-in-the-loop approval via admin chat

The system is event-driven and structured around explicit decision and action models.

Transport (polling or webhook) is treated as an ingestion mechanism and must not affect core logic.

## High-Level Flow

All logic starts with the same pipeline:

1. Telegram update is received (via polling)
2. Update is normalized into a domain event
3. Context is resolved (bot, chat, policy)
4. Event is processed by orchestrator
5. Engines evaluate the event
6. A decision is produced

Then one of two paths is used.

### Automatic path

7. Decision is converted into actions
8. Actions are executed
9. Audit log is written

### Approval path

7. Decision is marked as requiring approval
8. Approval request is created and stored
9. Bot sends approval request to admin chat
10. Admin response is validated
11. Stored action is executed
12. Audit log is written

Approval is optional and policy-driven.

## Transport Model

The system currently uses Telegram polling.

Polling responsibilities:
- fetch updates from Telegram API
- track update offsets
- handle retries and failures
- pass updates into normalization layer

Constraints:
- polling must not contain business logic
- polling must not make decisions
- polling must not access domain or database directly
- polling must not execute actions

The rest of the system must not depend on polling-specific behavior.

Webhook support can be added later as an alternative ingestion mechanism.

## Admin Chat (Control Plane)

The system uses a dedicated Telegram admin chat for optional human-in-the-loop interaction.

This chat acts as the control plane for:
- approval of sensitive actions
- moderator review flows
- moderator notifications
- future bot management commands

Admin chat is used only when policy or control workflows require moderator involvement.

Constraints:
- routine actions must be able to execute without admin chat
- admin chat must not become a mandatory step for all actions
- only authorized users can perform moderator actions
- all admin actions must be auditable
- callback handling must not bypass validation or policy checks

## Core Concepts

### Event

A normalized representation of an external trigger.

Examples:
- message.created
- join_request.created
- approval.resolved
- admin.command.received

Events are transport-agnostic and must not depend on Telegram-specific structures.

### Context

Resolved runtime context for an event.

Includes:
- bot configuration
- chat configuration
- policy profile
- feature flags
- admin permissions when relevant

Context must be constructed before any decision is made.

### Decision

A structured result of evaluating an event.

A decision must not perform side effects.

Typical fields:
- outcome (allow / reject / reply / ignore / review)
- actions (list)
- reasons
- confidence
- requires_approval

### Action

A side-effect to be executed.

Examples:
- delete message
- send reply
- ban user
- request approval
- send admin notification

Actions must:
- be explicit
- be serializable
- be idempotent

Actions are executed only by the execution layer.

### Policy

Defines behavior for a specific bot + chat.

Policy controls:
- enabled features
- moderation rules
- assistant configuration
- approval requirements
- rate limits
- admin interaction requirements

No behavior should be hardcoded per chat.

## Layers

The system is split into clear layers.

### 1. Transport Layer (Telegram)

Includes:
- polling ingestion
- admin callback ingestion
- future webhook ingestion

Responsibilities:
- receive updates
- parse raw payload
- map to domain events

Constraints:
- no business logic
- no DB access
- no decisions

### 2. Application Layer (Orchestrator)

Responsibilities:
- build context
- route events
- call engines
- combine decisions
- trigger actions or approval flow

This is the central coordination layer.

### 3. Domain Layer

Contains:
- events
- decisions
- actions
- policy models
- approval models

Constraints:
- no external dependencies (Telegram, DB, etc.)
- pure logic and structures

### 4. Engines

Encapsulate decision logic.

Examples:
- moderation engine
- join request screening
- marketplace rules
- assistant (RAG)

Constraints:
- no side effects
- return decisions only
- deterministic first, AI only when needed

### 5. Execution Layer

Responsibilities:
- execute actions
- call Telegram API
- ensure idempotency

This is the only layer allowed to perform external side effects.

### 6. Infrastructure Layer

Includes:
- database (PostgreSQL)
- Redis
- vector storage (Qdrant)
- external APIs (OpenAI)

Constraints:
- no business logic
- accessed via services/repositories

## Policy-Driven Behavior

Behavior is defined by:

- bot_id
- chat_id
- policy_profile

The same bot may behave differently in different chats.

Policies must be:
- resolved at runtime
- stored outside code
- modifiable without redeploy

Approval requirements must also be policy-driven.

## Multi-Bot Model

The system supports multiple bots in a single backend.

Each bot:
- has its own token
- can be bound to multiple chats
- uses per-chat policies
- may share or not share admin chat policy depending on configuration

Polling must support multiple bots without mixing their update streams.

## Approval Workflow

Some actions require manual approval.

Flow:
1. decision marks action as requiring approval
2. approval request is stored
3. bot sends message to admin chat
4. admin approves or rejects via Telegram interaction
5. stored action is executed only after valid approval

Constraints:
- approval is optional and policy-driven
- actions that do not require approval must execute directly
- actions must be stored before approval
- execution must be idempotent
- all steps must be auditable

## AI Usage Model

AI is used only where deterministic logic is insufficient.

Allowed:
- ambiguous moderation cases
- classification tasks
- assistant response generation (RAG)

Not allowed:
- replacing simple rules
- general-purpose chatbot behavior

Assistant must be:
- domain-restricted
- retrieval-based
- safe by default

## Key Constraints

- no business logic in transport layer
- no side effects in engines
- no direct Telegram calls outside execution layer
- no hardcoded chat-specific behavior
- no uncontrolled LLM usage
- no coupling between core logic and polling implementation
- no assumption that admin chat is mandatory for all actions

## Design Goals

- clear separation of concerns
- predictable behavior via policies
- safe integration of AI
- extensibility without rewrites
- auditable decision making
- transport-agnostic architecture
- Telegram-native moderator control plane

## Out of Scope (for now)

- admin web UI
- complex multi-step AI agents
- full automation of all moderation decisions
- cross-platform integrations beyond Telegram