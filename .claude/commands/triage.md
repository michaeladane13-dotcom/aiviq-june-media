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
On yes, create the reminder as a calendar event with a popup alert:
- `create_or_update_event` with the extracted title, `start`/`end`, the user's
  timezone, and `reminders: [{ method: "popup", minutes: 60 }]` (offer to add a
  day-before popup too: `{ method: "popup", minutes: 1440 }`).
- Confirm the exact date/time back to the user before creating. If the time is
  unclear, ask rather than guess.
- Note: this fires a notification on the iPhone via the Calendar app. (We can't
  write to the Apple Reminders app — no connector for it.)

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
- Confirm dates/times before creating any calendar event.
- If the user says "do them all," still echo the list of actions you're about to
  take and get one confirmation before applying.
