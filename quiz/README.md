# Chaya — "Which Spirit Guide Is Trying to Reach You?" Quiz Funnel

A self-contained lead-capture quiz for **Chaya The Medium**. Visitors answer 5
questions, enter their email to unlock their result, and are added to Chaya's
**Newsletter** group in MailerLite. The existing *Welcome Email – Newsletter
Signup* automation then fires.

## How it's wired

- **File:** `quiz/index.html` — no build step, no dependencies, just HTML/CSS/JS.
- **MailerLite account:** `2234262` (chayamclarnon@gmail.com / Chaya The Medium)
- **Embedded form:** `189681380338173838` (group: Newsletter `188125167474443364`)
- On email submit the page posts `email`, `name`, and `quiz_result` to the
  MailerLite public form endpoint, then reveals the on-screen result + a
  "Book Your Personal Reading" CTA.
- Four results: **The Ancestor**, **The Protector**, **The Teacher**, **The Messenger**.

> Note: the form currently uses **double opt-in** (MailerLite default). New
> subscribers get a confirmation email before the welcome message. Switch to
> single opt-in in the MailerLite form settings if you want zero-friction
> signups from paid traffic.

## Getting it live

### Option A — Embed on chayathemedium.org (recommended)
Create a new page (e.g. `/spirit-guide-quiz`) and drop this into a Custom
HTML / Embed / Code block:

```html
<iframe src="https://YOUR-HOST/quiz/index.html"
        style="width:100%;min-height:760px;border:0" loading="lazy"></iframe>
```

…or paste the full contents of `index.html` directly into a code block if the
site builder allows raw HTML pages.

### Option B — Free hosting (no website edits)
Host `quiz/index.html` on GitHub Pages / Netlify / Cloudflare Pages and point
the ad straight at that URL.

## The paid funnel
Meta/IG ad (Chaya page `319309021256227`, pixel `850247007020793`,
ad account `act_2925675017682500`) → quiz page → email → Newsletter group →
welcome sequence → reading offer. Suggested start: **$5/day**.
