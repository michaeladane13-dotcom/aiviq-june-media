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

**Appointments → "Want an iPhone reminder for this?"**
On yes, create a REAL Apple Reminder (syncs to the iPhone via iCloud) using the
local helper. Do NOT create a calendar event — the user wants Reminders.
- Run the compiled helper:
  `~/projects/aiviq-june-media/bin/add_reminder add "<title>" "YYYY-MM-DD HH:MM" "<notes>"`
  e.g. `bin/add_reminder add "Physio appointment" "2026-06-17 14:00" "Jane App booking"`.
  It sets the due date AND an alarm at that time, so the iPhone fires a Reminders
  notification then. Offer a day-before nudge too (a second reminder dated the day before).
- Confirm the exact date/time back to the user before creating. If the time is
  unclear, ask rather than guess.
- The helper uses EventKit (the Reminders AppleScript bridge hangs on macOS 26, so
  we use this signed CLI instead). If it prints `DENIED: no Reminders access`,
  enable Reminders for Claude once in System Settings > Privacy & Security >
  Reminders, then re-run. If the binary is missing, rebuild it:
  `swiftc -O bin/add_reminder.swift -o bin/add_reminder`.

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
- Reminders are real Apple Reminders via `bin/add_reminder` (never calendar events).
- If the user says "do them all," still echo the list of actions you're about to
  take and get one confirmation before applying.
