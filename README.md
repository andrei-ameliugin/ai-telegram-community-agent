# AI Telegram Community Agent

Backend platform for managing Telegram communities using policy-driven automation and AI-assisted decision workflows.

## Overview

This is a multi-bot, multi-chat backend system designed to support community management in Telegram.

The system provides:
- automated moderation
- join request screening
- marketplace rule enforcement
- domain-restricted AI assistant responses
- human approval for sensitive actions
- a dedicated private admin chat for moderator interaction

It is designed to operate as a centralized service that can manage multiple chats with different rules and behavior profiles.

## Key Principles

- policy-driven behavior per bot and chat
- deterministic-first decision making
- AI used only for ambiguous cases
- domain-restricted assistant, not a general-purpose chatbot
- human-in-the-loop for high-risk actions
- transport-agnostic core architecture
- Telegram-native moderator interaction via admin chat

## Transport Model

The system currently uses Telegram polling for update ingestion.

This choice is intentional:
- simpler local development
- easier reuse as a self-hosted GitHub project
- no domain or HTTPS requirement to get started
- lower operational complexity for initial deployment

Polling is treated as an ingestion mechanism only.
Core application and domain logic are designed so webhook support can be added later without changing the main architecture.

## Execution Model

The system supports two execution paths.

### Automatic flow

Used for actions that do not require moderator involvement:

decision -> action

### Approval flow

Used for actions that require moderator approval:

decision -> approval -> admin chat -> action

Whether approval is required depends on policy configuration.

This allows routine actions to remain automatic while routing sensitive operations through moderators.

## Admin Interaction

The system uses a dedicated private Telegram admin chat for moderator interaction.

This chat acts as a control interface for:
- approval of risky moderation actions
- join request review
- moderator notifications
- future bot management operations

The bot sends structured messages to admin chat with context and explicit inline buttons such as:
- approve / reject
- ban / do not ban
- accept / decline

This keeps moderation and operations inside Telegram without requiring a separate admin panel.

## Architecture (high-level)

- Telegram transport layer - polling updates and normalizing them into internal events
- orchestrator - event routing and coordination
- engines - decision logic (moderation, assistant, marketplace rules, join screening)
- actions - side-effect execution
- approval workflow - optional manual validation layer
- admin chat - Telegram-native control plane for moderator interaction
- audit logging - full trace of decisions and actions

## Use Cases

- residential community chats
- marketplace / buy-sell groups
- private gated communities with join screening
- structured community support via assistant

## Status

Early development. Core architecture and initial features are being implemented.

## Planned Stack

- Python 3.11+
- FastAPI
- aiogram
- PostgreSQL
- Redis
- Qdrant
- OpenAI API
- Docker Compose

## Deployment

Designed to run as a single backend service.

Typical setup:
- application service
- PostgreSQL as primary storage
- Redis for cache and ephemeral state
- Qdrant for assistant retrieval
- OpenAI API for AI-assisted decision layers

Can be deployed on a single VPS such as Hetzner using Docker Compose.

## Notes

Polling is acceptable for the intended early-stage deployment model:
- single backend instance
- moderate traffic
- limited operational complexity

If the system later requires more advanced scaling or external ingress patterns, webhook support can be added as an alternative transport layer.