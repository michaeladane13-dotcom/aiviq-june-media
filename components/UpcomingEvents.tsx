"use client";

import { useEffect, useState } from "react";
import Card from "./Card";

interface Evt {
  id: string;
  name: string;
  start: string | null;
  allDay: boolean;
  location: string | null;
  isAppointment: boolean;
}

interface Payload {
  configured: boolean;
  events: Evt[];
  error?: string;
  fetchedAt: number;
}

function fmtWhen(start: string | null, allDay: boolean): string {
  if (!start) return "";
  const d = new Date(start);
  const date = d.toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
  if (allDay) return date;
  const time = d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
  return `${date} · ${time}`;
}

function fmtRefreshed(ts: number): string {
  return `Updated ${new Date(ts).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  })}`;
}

export default function UpcomingEvents() {
  const [data, setData] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/calendar")
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card
      title="Upcoming — Next 14 Days"
      subtitle={data ? fmtRefreshed(data.fetchedAt) : undefined}
    >
      {loading && <p className="text-sm text-ink/40">Loading…</p>}

      {!loading && data && !data.configured && (
        <p className="text-sm text-ink/40">
          Google Calendar not connected yet.
        </p>
      )}

      {!loading && data?.error && (
        <p className="text-sm text-appt">{data.error}</p>
      )}

      {!loading && data?.configured && !data.error && data.events.length === 0 && (
        <p className="text-sm text-ink/40">Nothing scheduled.</p>
      )}

      <ul className="space-y-2">
        {data?.events.map((e) => (
          <li
            key={e.id}
            className={[
              "rounded-lg border-l-2 bg-bg px-3 py-2",
              e.isAppointment ? "border-appt" : "border-white/10",
            ].join(" ")}
          >
            <div className="flex items-start justify-between gap-3">
              <span className="text-sm font-medium text-ink">{e.name}</span>
              {e.isAppointment && (
                <span className="shrink-0 rounded bg-appt/30 px-1.5 py-0.5 text-[9px] uppercase tracking-wide text-appt">
                  Appt
                </span>
              )}
            </div>
            <div className="mt-0.5 font-mono text-[11px] text-ink/50">
              {fmtWhen(e.start, e.allDay)}
              {e.location ? ` · ${e.location}` : ""}
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
