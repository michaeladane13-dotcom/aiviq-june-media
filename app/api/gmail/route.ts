import { NextResponse } from "next/server";
import { google, gmail_v1 } from "googleapis";
import { getOAuthClient, cached } from "@/lib/google";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Bucket = "action" | "appointments" | "unsubscribe" | "junk";

interface TriagedMail {
  id: string;
  sender: string;
  subject: string;
  bucket: Bucket;
}

const APPT_WORDS = [
  "confirmation",
  "confirmed",
  "booking",
  "booked",
  "appointment",
  "reminder",
  "scheduled",
  "receipt",
  "reservation",
  "your order",
];

const ACTION_WORDS = [
  "action required",
  "please",
  "urgent",
  "response needed",
  "reply",
  "overdue",
  "payment due",
  "invoice",
  "rsvp",
  "?",
];

function headerValue(headers: gmail_v1.Schema$MessagePartHeader[], name: string): string {
  const h = headers.find((x) => (x.name ?? "").toLowerCase() === name.toLowerCase());
  return h?.value ?? "";
}

function classify(
  subject: string,
  labelIds: string[],
  hasUnsubscribe: boolean
): Bucket {
  const subj = subject.toLowerCase();
  const labels = new Set(labelIds);

  // Spam is junk, full stop.
  if (labels.has("SPAM")) return "junk";

  // Booking / reminder style confirmations.
  if (APPT_WORDS.some((w) => subj.includes(w))) return "appointments";

  // Newsletters & marketing: promotions label or a List-Unsubscribe header.
  if (labels.has("CATEGORY_PROMOTIONS") || hasUnsubscribe) return "unsubscribe";

  // Things that look like they want a reply or decision.
  if (ACTION_WORDS.some((w) => subj.includes(w))) return "action";

  // Automated updates / forums with nothing actionable -> low priority.
  if (labels.has("CATEGORY_UPDATES") || labels.has("CATEGORY_FORUMS")) {
    return "junk";
  }

  // Personal / primary inbox mail that didn't match anything else most
  // likely wants a human response.
  return "action";
}

export async function GET() {
  const auth = getOAuthClient();
  if (!auth) {
    return NextResponse.json({ configured: false, mails: [], fetchedAt: Date.now() });
  }

  try {
    const { data: mails, fetchedAt } = await cached("gmail:7d", async () => {
      const gmail = google.gmail({ version: "v1", auth });

      const list = await gmail.users.messages.list({
        userId: "me",
        q: "newer_than:7d in:inbox",
        maxResults: 40,
      });

      const ids = (list.data.messages ?? []).map((m) => m.id!).filter(Boolean);

      const results = await Promise.all(
        ids.map(async (id) => {
          const msg = await gmail.users.messages.get({
            userId: "me",
            id,
            format: "metadata",
            metadataHeaders: ["From", "Subject", "List-Unsubscribe"],
          });
          const headers = msg.data.payload?.headers ?? [];
          const sender = headerValue(headers, "From");
          const subject = headerValue(headers, "Subject") || "(no subject)";
          const hasUnsubscribe = !!headerValue(headers, "List-Unsubscribe");
          const labelIds = msg.data.labelIds ?? [];
          const bucket = classify(subject, labelIds, hasUnsubscribe);

          // Strip the angle-bracket address, keep the friendly name only.
          const cleanSender = sender.replace(/<[^>]*>/, "").replace(/"/g, "").trim() ||
            sender;

          return { id, sender: cleanSender, subject, bucket } as TriagedMail;
        })
      );

      return results;
    });

    return NextResponse.json({ configured: true, mails, fetchedAt });
  } catch (err) {
    console.error("gmail error", err);
    return NextResponse.json(
      { configured: true, error: "Could not load inbox.", mails: [], fetchedAt: Date.now() },
      { status: 502 }
    );
  }
}
