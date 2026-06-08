# Agent task: add the Spirit Guide quiz to chayathemedium.org

**Repo:** `michaeladane13-dotcom/chaya-the-medium`
**Goal:** Publish the lead-capture quiz at **`https://chayathemedium.org/spirit-guide-quiz/`** so a Meta ad can drive traffic to it and grow Chaya's newsletter.

## What to do

1. Fetch the finished quiz (single self-contained HTML file, no dependencies):
   ```
   https://raw.githubusercontent.com/michaeladane13-dotcom/aiviq-june-media/main/quiz/index.html
   ```
   (If not yet on `main`, use branch `claude/newsletter-signup-strategy-MSqvL`.)

2. Add it as a statically-served page so it resolves at `/spirit-guide-quiz/`:
   - **Next.js / most React setups:** save the file to `public/spirit-guide-quiz/index.html`.
   - **Vite/static:** save to `public/spirit-guide-quiz/index.html` (or wherever `public/` maps to the web root).
   - If the site prefers a real route, you may instead port it to a page component — but the standalone HTML is intentionally framework-agnostic; serving it statically is the low-risk path. Do **not** wrap it in the site's global layout/nav (it's a full-screen funnel page).

3. Verify after deploy:
   - `https://chayathemedium.org/spirit-guide-quiz/` loads, the 5 questions advance, and the email gate reveals a result.
   - A test email submission appears in MailerLite under the **Newsletter** group with the `quiz_result` field populated.

## Already wired (do not change)
- MailerLite account `2234262`, embedded form `189681380338173838`, group **Newsletter** `188125167474443364`.
- The page POSTs `email`, `name`, and `quiz_result` to MailerLite's public form endpoint — no API key or secret is needed client-side.
- The "Book Your Personal Reading" CTA links to `https://chayathemedium.org` — repoint it to the actual booking/reading page if there's a better URL.

## Acceptance
- Clean URL `https://chayathemedium.org/spirit-guide-quiz/` live and mobile-friendly.
- Test signup lands in the Newsletter group with the archetype captured.
- Report the final URL back so the Meta ad can be activated against it.
