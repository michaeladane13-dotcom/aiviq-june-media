# Agent task: add the Spirit Guide quiz to chayathemedium.org

**Repo:** `michaeladane13-dotcom/chaya-the-medium`
**Goal:** Publish the lead-capture quiz at **`https://chayathemedium.org/spirit-guide-quiz.html`** so a Meta ad can drive traffic to it and grow Chaya's newsletter.

## Exact steps

```bash
# from the repo root, on a fresh branch
git checkout -b add-spirit-guide-quiz

# pull the finished, self-contained quiz into the static/public dir
curl -fsSL "https://raw.githubusercontent.com/michaeladane13-dotcom/aiviq-june-media/claude/newsletter-signup-strategy-MSqvL/quiz/index.html" \
  -o public/spirit-guide-quiz.html

git add public/spirit-guide-quiz.html
git commit -m "Add Spirit Guide quiz funnel page"
git push -u origin add-spirit-guide-quiz
```

- The file is **one self-contained HTML page** — no imports, no build step, no env vars. It must be served **as-is** (do NOT wrap it in the site's layout/nav; it's a full-screen funnel page).
- **`public/` is correct for Next.js, Vite, and CRA** — files there are served from the web root. Final URL: `https://chayathemedium.org/spirit-guide-quiz.html`.
- If the project's static dir is named differently (`static/`, `assets/`), use that instead and report the resulting URL.
- Want a prettier `/spirit-guide-quiz` URL? Add a host rewrite (`vercel.json` / `netlify.toml`) from `/spirit-guide-quiz` → `/spirit-guide-quiz.html`. Optional.

## Already wired (do not change)
- MailerLite account `2234262`, embedded form `189681380338173838`, group **Newsletter** `188125167474443364`.
- The page POSTs `email`, `name`, and `quiz_result` to MailerLite's public form endpoint — no API key/secret client-side.
- "Book Your Personal Reading" CTA links to `https://chayathemedium.org` — repoint to the real booking page if there's a better URL.

## Verify, then report back
1. `https://chayathemedium.org/spirit-guide-quiz.html` loads on mobile; the 5 questions advance; the email gate reveals a result.
2. A test email shows up in MailerLite under **Newsletter** with the `quiz_result` field populated.
3. Reply with the final live URL so the Meta ad can be switched on.
