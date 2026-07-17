# Master kickoff prompt — paste into a NEW Claude Code session

Paste everything in the block below into a fresh Claude Code session. It builds the
whole inbox-triage project from scratch, commits, pushes, and gives you the routine
setup steps.

```
Build a personal inbox-triage automation in this repo, end to end. Do all of the
following, then stop and give me the routine setup instructions.

CONTEXT
- I triage my personal inbox with the Superhuman connector (email + calendar tools:
  list_threads, get_thread, get_message, query_email_and_calendar, list_labels,
  update_thread, create_or_update_draft, send_draft, create_or_update_event, etc.).
- It runs as a scheduled Routine 4-5x/day (unattended) plus an on-demand /triage
  command I run to approve yes/no actions.
- Rules: Stripe/PayPal/Manus payment receipts -> auto mark READ. Same senders but an
  ISSUE (failed/dispute/action required) -> leave unread and flag with options.
  Appointments (Jane App, Calendly, clinics) -> flag and offer an "iPhone reminder"
  (= a calendar event with a popup alert; the Apple Reminders app is NOT reachable —
  no connector). Everything else important -> flag under "Needs you". One digest
  draft to myself is the single place I review.

CREATE THESE FILES

1) routines/inbox-triage.md — the background routine prompt. It must instruct the
   agent to: only mark_read:true for clearly bucketed payment receipts (never
   archive/trash/star/move in this pass); leave issues + appointments + important
   mail unread; write/refresh ONE digest draft to myself titled "Inbox Triage —
   {date}" with sections ISSUES / APPOINTMENTS / NEEDS YOU / AUTO-FILED, each item
   numbered with suggested options; and end with a single <=12-word summary line for
   the phone notification ("Triage: N need you (X issues, Y appts) · Z auto-filed").
   If a Stripe/PayPal/Manus mail is ambiguous between receipt and issue, treat as
   ISSUE. Do not create calendar events or send mail in this pass.

2) .claude/commands/triage.md — the interactive approval command (with YAML
   frontmatter: description). It loads the latest digest (or rescans unread),
   walks each flagged item one at a time and WAITS for my yes/no, then: for
   appointments creates a calendar event via create_or_update_event with
   reminders [{method:"popup",minutes:60}] (offer a day-before popup too), confirming
   date/time first; for issues/needs-you offers Open / Draft reply (draft only, never
   auto-send) / Mark done / Snooze. Guardrails: never send or trash without an
   explicit yes; confirm all dates before creating events.

3) routines/README.md — short overview table of the two pieces, how the split works
   (routine = safe auto-work + digest; /triage = approvals), the one-time setup
   (connect Superhuman, create routine at claude.ai/code/routines pointing at this
   repo + Superhuman, schedule 4-5x/day), phone-notification behavior, and the
   iPhone-reminder limitation.

THEN
- git add, commit with a clear message, and push to the current branch.
- Open a draft pull request.
- Print: (a) the exact routine prompt to paste, and (b) the 6 setup clicks
  (connect Superhuman at claude.ai/customize/connectors; create routine at
  claude.ai/code/routines; pick repo; pick Superhuman connector; paste prompt;
  schedule 4-5x/day). Remind me that creating the routine + connector is desktop-web
  only, but running /triage works from the Claude phone app afterward.
```

## After the session finishes
Do the 6 desktop clicks it prints. Then use it from your phone: Claude app → /code →
`/triage`.
