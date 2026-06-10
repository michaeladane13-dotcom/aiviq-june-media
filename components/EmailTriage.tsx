"use client";

import { useEffect, useState } from "react";
import Card from "./Card";

type Bucket = "action" | "appointments" | "unsubscribe" | "junk";

interface Mail {
  id: string;
  sender: string;
  subject: string;
  bucket: Bucket;
}

interface Payload {
  configured: boolean;
  mails: Mail[];
  error?: string;
  fetchedAt: number;
}

const GROUPS: { key: Bucket; label: string; accent: string }[] = [
  { key: "action", label: "Needs action", accent: "text-accent" },
  { key: "appointments", label: "Appointments / reminders", accent: "text-appt" },
  { key: "unsubscribe", label: "Unsubscribe candidates", accent: "text-shift" },
  { key: "junk", label: "Likely junk", accent: "text-ink/40" },
];

function fmtRefreshed(ts: number): string {
  return `Last refreshed ${new Date(ts).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  })}`;
}

export default function EmailTriage() {
  const [data, setData] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/gmail")
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card
      title="Email Triage — Last 7 Days"
      subtitle={data ? fmtRefreshed(data.fetchedAt) : undefined}
    >
      {loading && <p className="text-sm text-ink/40">Loading…</p>}

      {!loading && data && !data.configured && (
        <p className="text-sm text-ink/40">Gmail not connected yet.</p>
      )}

      {!loading && data?.error && (
        <p className="text-sm text-appt">{data.error}</p>
      )}

      {!loading && data?.configured && !data.error && data.mails.length === 0 && (
        <p className="text-sm text-ink/40">Inbox is clear.</p>
      )}

      {!loading && data?.configured && !data.error && data.mails.length > 0 && (
        <div className="space-y-4">
          {GROUPS.map((g) => {
            const items = data.mails.filter((m) => m.bucket === g.key);
            if (items.length === 0) return null;
            return (
              <div key={g.key}>
                <h3 className={`mb-1.5 text-[11px] font-semibold uppercase tracking-wide ${g.accent}`}>
                  {g.label} · {items.length}
                </h3>
                <ul className="space-y-1.5">
                  {items.map((m) => (
                    <li key={m.id} className="rounded-lg bg-bg px-3 py-2">
                      <div className="truncate text-sm text-ink">{m.subject}</div>
                      <div className="truncate text-[11px] text-ink/50">
                        {m.sender}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
