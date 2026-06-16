# Inbox triage automation

Two pieces working together:

| File | Runs | Does |
|------|------|------|
| `routines/inbox-triage.md` | Background Routine, 4–5×/day | Marks Stripe/PayPal/Manus **payment receipts** as read; flags **issues** and **appointments** into one digest draft in your inbox. Takes no risky actions. |
| `.claude/commands/triage.md` (`/triage`) | You, on demand | Walks you through the flagged items, asks yes/no, creates calendar reminders, drafts replies, files threads. |

## How it splits the work
A Routine runs **unattended**, so it can't wait for you to tap "yes." So the routine
does only the safe, no-questions work and writes everything that needs a decision
into a single **digest draft** (your "one place," readable on your phone). When you've
got a minute, open Claude and run **`/triage`** to approve the yes/no items — that's
where reminders and replies actually happen.

## One-time setup
1. **Connect Superhuman** to your Claude account (Settings → Connectors), so the
   routine can read/triage your mail.
2. **Create the Routine** at <https://claude.ai/code/routines> (or `/schedule` in the
   Claude Code CLI):
   - **Repository:** this repo (`aiviq-june-media`), branch `claude/code-routines-access-oklzmb`
     (or wherever this lands after merge).
   - **Connectors:** Superhuman.
   - **Prompt:** paste the contents of `routines/inbox-triage.md`, or simply:
     *"Follow the instructions in `routines/inbox-triage.md`."*
   - **Schedule:** pick 4–5 times across your day (e.g. 08:00, 12:00, 15:00, 18:00,
     21:00 in your timezone).
3. That's it. The routine keeps your inbox tidy; you run `/triage` to approve the rest.

## The rules it follows
- **Stripe / PayPal / Manus + payment/receipt** → auto **mark read** (+ `Receipts`
  label if it exists). No asking.
- **Stripe / PayPal / Manus + an issue** (failed, dispute, action required, …) →
  **left unread and flagged** with options. Never silently hidden.
- **Appointments** (Jane App, Calendly, clinics, "your booking", etc.) → flagged with
  a proposed **iPhone reminder** (created on your yes during `/triage`).
- **Anything else important** → flagged under "Needs you."

## Phone notifications
You get push notifications on your phone from this in two ways:
1. **Each routine run** — when the Routine finishes, the Claude app sends its usual
   completion notification to your phone (same as your other routines). The routine
   ends with a one-line summary (e.g. *"Triage: 3 need you (2 issues, 1 appt)"*) so
   the notification is actually useful at a glance. Tap it to open the digest.
2. **At appointment time** — each reminder you approve in `/triage` is a real
   **Apple Reminder** with an alarm, which fires a Reminders notification on your
   iPhone at the time you set (it syncs from this Mac via iCloud).

## iPhone reminders — how it works
"iPhone reminder" = a genuine entry in the Apple **Reminders** app (not a calendar
event). `/triage` creates it with the local helper `bin/add_reminder` (a small
EventKit CLI in this repo), because the Reminders AppleScript bridge hangs on
macOS 26. The reminder lands in your default Reminders list with an alarm at the
appointment time and syncs to your iPhone through iCloud.

**One-time setup:** the first time, macOS needs Reminders access granted to Claude
— System Settings > Privacy & Security > Reminders > enable **Claude**. If
`bin/add_reminder` ever prints `DENIED`, that toggle is why. Rebuild the helper
after edits with `swiftc -O bin/add_reminder.swift -o bin/add_reminder`.

## Tuning
Edit `routines/inbox-triage.md` to change which senders auto-file, add more
auto-read senders (newsletters, order confirmations), or change the digest layout.
The routine picks up the new instructions on its next run.
