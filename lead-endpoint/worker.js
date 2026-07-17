/**
 * Lead endpoint for danielpsychicartist.space
 *
 * A tiny Cloudflare Worker that receives the email form POST from the site,
 * stores the contact in a Resend audience, and redirects to the thank-you
 * page. Free tier is more than enough for lead-gen traffic.
 *
 * Deploy (one time):
 *   1. Create a Resend account for Daniel (resend.com), add an Audience,
 *      and create an API key.
 *   2. In the Cloudflare dashboard: Workers & Pages > Create Worker,
 *      paste this file, then add two secrets under Settings > Variables:
 *        RESEND_API_KEY      the Resend API key
 *        RESEND_AUDIENCE_ID  the Audience ID from Resend
 *   3. Copy the worker URL (e.g. https://daniel-leads.xxxx.workers.dev)
 *      into FORM_ACTION in docs/index.html and docs/free.html.
 *
 * Sending the actual free MP3 email is done in Resend with an automation or
 * a welcome email on the Audience, so this worker only needs to store the
 * contact.
 */

const SITE = "https://danielpsychicartist.space";
const THANKS_URL = SITE + "/thanks.html";

export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": SITE,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: cors });
    }

    let email = "";
    const type = request.headers.get("content-type") || "";
    try {
      if (type.includes("application/json")) {
        email = (await request.json()).email || "";
      } else {
        email = (await request.formData()).get("email") || "";
      }
    } catch (_) {
      return new Response("Bad request", { status: 400, headers: cors });
    }

    email = String(email).trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
      return new Response("Invalid email", { status: 400, headers: cors });
    }

    const res = await fetch(
      `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, unsubscribed: false }),
      }
    );

    // 409 means the contact already exists, which is still a success for us.
    if (!res.ok && res.status !== 409) {
      return new Response("Something went wrong, please try again.", {
        status: 502,
        headers: cors,
      });
    }

    return Response.redirect(THANKS_URL, 303);
  },
};
