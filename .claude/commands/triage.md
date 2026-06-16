---
description: Walk through flagged inbox items and approve actions (reminders, replies, filing)
---

# Interactive inbox triage

This is the approval pass for the inbox-triage routine. The background routine has
already marked payment receipts read and built a digest. Your job: walk the user
through the items that need a yes/no, one at a time, and take the action they approve.

Use the **Superhuman** connector.

## Step 1 — Load the current state
- Open the latest `📥 Inbox Triage` digest draft to see what's flagged, OR re-scan
  live with `list_threads(is_unread: true, limit: 50)` if the draft is stale.
- Briefly tell the user the headline: "X issues, Y appointments, Z need you."

## Step 2 — Go through items one at a time
Present each flagged item as a short numbered line, then ask a direct question and
WAIT for the answer before acting. Don't batch-apply without confirmation.

**Appointments → "Want a phone reminder for this?"**
On yes, create the reminder as a ONE-TIME Claude routine that fires a phone
notification at the chosen time. This is how we do iPhone reminders — no Calendar,
no Reminders-app, no permissions. Use the `create_scheduled_task` tool:
- Confirm the date/time with the user first. Ask when they want the nudge — default
  to 1 hour before the appointment; also offer the day before.
- Call `create_scheduled_task` with:
  - `taskId`: `remind-<short-slug>-<yyyymmddhhmm>` (e.g. `remind-physio-202606171300`)
  - `fireAt`: ISO 8601 of the reminder moment in the user's timezone
    (America/Vancouver = `-07:00` in summer), e.g. `2026-06-17T13:00:00-07:00`
  - `description`: `Appointment reminder: <title>`
  - `prompt`: `Output exactly this one line as your final message (it becomes the
    phone notification): "Reminder: <title> at <appt time> on <date>."` Do nothing
    else.
- A one-time task auto-disables after it fires. For a day-before nudge, create a
  second task at that earlier moment.
- The notification reaches the iPhone via the Claude app when the task fires.

**Issues (Stripe/PayPal/Manus problems) → offer the options.**
For each, offer: *Open it (give the link/summary) / Draft a reply / Mark done /
Leave it.* Take only the chosen action. Use `create_or_update_draft` for replies
(draft only — let the user review and send), `update_thread(mark_done: true)` to
archive when they're done with it.

**Needs-you items → ask how to handle.**
Same menu: reply (draft) / mark done / snooze (leave unread) / star.

## Step 3 — Wrap up
Summarize what you did: reminders created, drafts written, threads filed. Leave any
untouched items in the inbox. Do not send any email unless the user explicitly says
to send it.

## Guardrails
- Never send mail or delete/trash a thread without an explicit yes.
- Confirm dates/times before creating any reminder.
- Reminders are one-time Claude routines (`create_scheduled_task` with `fireAt`)
  that notify the phone — never calendar events, never the Reminders app.
- If the user says "do them all," still echo the list of actions you're about to
  take and get one confirmation before applying.
