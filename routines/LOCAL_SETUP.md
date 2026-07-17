# End-to-end setup — paste into Claude Code on your LAPTOP

Paste the block below into a local Claude Code session (run it from inside the repo,
or it'll clone it). It does everything it can automatically and tells you the one or
two interactive commands you type yourself (`/schedule`, connector auth).

```
Set up my inbox-triage automation end to end on this machine. Work through every step,
do what you can automatically, and STOP at any step that needs me to type an
interactive slash command — tell me exactly what to type, wait, then continue.

STEP 0 — Repo
- If we're not already in the `aiviq-june-media` repo, clone it and cd in. Use branch
  `claude/code-routines-access-oklzmb` (it already contains routines/inbox-triage.md,
  .claude/commands/triage.md, routines/README.md). If those files are missing, create
  them per STEP 1.

STEP 1 — Files (only if missing)
- routines/inbox-triage.md: background routine prompt. Rules: Stripe/PayPal/Manus
  payment receipts -> update_thread(mark_read:true) only (never archive/trash/star/
  move); same senders but an ISSUE (failed/dispute/declined/action required) ->
  leave unread + flag with options; appointments (Jane App, Calendly, clinics) ->
  flag + offer an "iPhone reminder"; everything else important -> flag under
  "Needs you". Write/refresh ONE digest draft to me titled "Inbox Triage — {date}"
  with sections ISSUES / APPOINTMENTS / NEEDS YOU / AUTO-FILED, numbered items with
  suggested options. End with a <=12-word phone-notification summary line
  ("Triage: N need you (X issues, Y appts) · Z auto-filed"). Ambiguous receipt-vs-
  issue -> treat as ISSUE. No calendar events / no sending in this pass.
- .claude/commands/triage.md (YAML frontmatter with description): interactive approval
  command. Loads latest digest or rescans unread, walks each flagged item one at a
  time, WAITS for my yes/no, then: appointments -> create_or_update_event with
  reminders [{method:"popup",minutes:60}] (offer day-before too), confirming date/time
  first; issues/needs-you -> Open / Draft reply (draft only, never auto-send) / Mark
  done / Snooze. Never send or trash without an explicit yes.

STEP 2 — Superhuman MCP connector
- Check `claude mcp list` for a Superhuman server. If it's missing, add it (ask me for
  the Superhuman MCP URL/command if you don't have it) and run any auth/login step.
  Confirm the email+calendar tools (list_threads, update_thread, create_or_update_draft,
  create_or_update_event, etc.) are available before continuing.

STEP 3 — Create the Routine
- Tell me to run `/schedule` and walk me through it (or run it if your version
  supports agent invocation). Configure:
  - Prompt: "Follow the instructions in routines/inbox-triage.md"
  - Repository: this repo
  - Connector: Superhuman
  - Schedule: 4-5 times a day (e.g. 08:00, 12:00, 15:00, 18:00, 21:00 my local time)
  Confirm the routine was created and show me its schedule.

STEP 4 — Commit + push
- git add/commit any new or changed files and push to the current branch. If there's
  no open PR for the branch, open a draft one.

STEP 5 — Verify
- Do a READ-ONLY dry run of routines/inbox-triage.md against my inbox: produce the
  digest but change NOTHING (no mark-read, no drafts). Show me the digest so I can
  confirm the rules look right. Ask before doing a real run.

Then summarize: files created, MCP status, routine schedule, PR link, and how to run
/triage from my phone afterward.
```

## What it can vs can't auto-do locally
- Files, git, commit/push, PR, dry-run triage: fully automatic.
- `/schedule` and connector login are interactive CLI steps — the agent will pause and
  tell you exactly what to type.
- Reminder = calendar event with popup alert (Apple Reminders app isn't reachable).
