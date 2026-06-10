import { NextResponse } from "next/server";
import { google } from "googleapis";
import { getOAuthClient, cached } from "@/lib/google";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const APPT_KEYWORDS = [
  "physio",
  "chiro",
  "massage",
  "doctor",
  "dentist",
  "appointment",
  "meeting",
];

function isAppointment(text: string): boolean {
  const lower = text.toLowerCase();
  return APPT_KEYWORDS.some((k) => lower.includes(k));
}

export async function GET() {
  const auth = getOAuthClient();
  if (!auth) {
    return NextResponse.json({ configured: false, events: [], fetchedAt: Date.now() });
  }

  try {
    const { data: events, fetchedAt } = await cached("calendar:14d", async () => {
      const calendar = google.calendar({ version: "v3", auth });
      const now = new Date();
      const in14 = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);

      const res = await calendar.events.list({
        calendarId: "primary",
        timeMin: now.toISOString(),
        timeMax: in14.toISOString(),
        singleEvents: true,
        orderBy: "startTime",
        maxResults: 50,
      });

      return (res.data.items ?? []).map((e) => {
        const summary = e.summary ?? "(no title)";
        const start = e.start?.dateTime ?? e.start?.date ?? null;
        const allDay = !e.start?.dateTime;
        return {
          id: e.id,
          name: summary,
          start,
          allDay,
          location: e.location ?? null,
          isAppointment: isAppointment(`${summary} ${e.location ?? ""}`),
        };
      });
    });

    return NextResponse.json({ configured: true, events, fetchedAt });
  } catch (err) {
    console.error("calendar error", err);
    return NextResponse.json(
      { configured: true, error: "Could not load calendar.", events: [], fetchedAt: Date.now() },
      { status: 502 }
    );
  }
}
