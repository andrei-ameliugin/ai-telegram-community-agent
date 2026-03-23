# Approval Workflow

This document defines the approval system used for human-in-the-loop
actions via Telegram admin chat.

The approval system is a core part of the platform and must be
implemented consistently.

## Overview

Some actions require moderator approval.

Two execution paths exist:

### Automatic

decision -\> action

### Approval-based

decision -\> approval request -\> admin chat -\> action

Approval is optional and determined by policy and decision logic.

## Core Concept

Approval is NOT tied to Telegram UI.

Telegram admin chat is only an interface.

The source of truth is the ApprovalRequest entity stored in the
database.

## ApprovalRequest Entity

Represents a pending action that requires human approval.

### Fields

    id: UUID

    status: "pending" | "approved" | "rejected" | "expired"

    action_type: string
    # e.g. "ban_user", "reject_join", "delete_message"

    payload: JSON
    # data required to execute the action
    # example: { "user_id": 123, "chat_id": -100... }

    reason: string
    # why this action was proposed

    context: JSON
    # optional additional info for display/logging

    created_at: timestamp
    resolved_at: timestamp | null

    requested_by: "system" | "engine_name"

    resolved_by_user_id: int | null
    # telegram user id of admin

    resolution: string | null
    # e.g. "approve", "reject"

    correlation_id: string
    # links to original event / decision

    version: int
    # optional, for future schema evolution

## Lifecycle

### 1. Creation

-   engine produces decision with requires_approval = true
-   system creates ApprovalRequest
-   status = pending
-   action is NOT executed

### 2. Admin Notification

Bot sends a message to admin chat.

Message must include:

- short description of action
- reason
- key context (user, chat, etc.)
- buttons (inline keyboard)

### 3. Admin Action

Admin clicks a button.
This generates a Telegram callback query.

### 4. Validation

System MUST:
	- load ApprovalRequest by id
	- verify status == pending
	- verify user_id is authorized admin
	- validate callback action

If any check fails -> reject

### 5. Execution

If approved:
	- execute stored action using payload

If rejected:
	- mark as rejected
	- do NOT execute action


### 6. Finalization

- update status
- set resolved_at
- store resolved_by_user_id
- log event

## Callback Data Format
Callback data must NOT encode business logic directly.

It must reference ApprovalRequest.

Format:
    appr:<approval_id>:<action>

Examples:

    appr:8f3a...:approve
    appr:8f3a...:reject
    appr:8f3a...:ban

## Rules for Callback Data

- must be short (Telegram limit)
- must not contain sensitive data
- must not contain raw payload
- must always reference approval_id
- action must be validated server-side

## Admin Authorization

Before processing callback:
	- verify user_id is in admin list
	- do not trust chat membership alone
	- do not trust UI visibility    

## Idempotency

Approval handling must be idempotent.

If:
	- same callback is received twice
	- request already resolved

Then:
	- do NOT execute action again
	- return safe response

## Action Execution

Actions must be executed using stored payload only.

Do NOT:
	- recompute action from callback data
	- trust callback data as source of truth

## Message Format (Admin Chat)

Example:

    Proposed action: Ban user

    User: @username (id: 123)
    Chat: Main Chat

    Reason:
        Spam detected (links + repetition)

    Actions:
        [Ban] [Reject]

## Button Mapping Example

    [Ban] -> appr:<id>:Ban
    [Reject]  -> appr:<id>:Reject

## Logging

Each step must be logged:
	- approval request created
	- message sent to admin chat
	- callback received
	- validation result
	- execution result
	- final status

## Future Extensions

This system can support:
	- multiple action options (not only approve/reject)
	- escalation flows
	- multi-admin approval
	- admin commands (pause bot, change policy, etc.)

## Constraints

-   approval must remain optional
-   admin chat must not be required for all actions
-   callback must not bypass validation