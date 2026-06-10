"use client";

import { useEffect, useState } from "react";
import Card from "./Card";

interface Reminder {
  id: string;
  text: string;
  date?: string;
  done: boolean;
}

const STORAGE_KEY = "planner.reminders.v1";

export default function QuickReminders() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [text, setText] = useState("");
  const [date, setDate] = useState("");
  const [hydrated, setHydrated] = useState(false);

  // Load from localStorage once on mount.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setReminders(JSON.parse(raw));
    } catch {
      /* ignore corrupt storage */
    }
    setHydrated(true);
  }, []);

  // Persist whenever the list changes (after initial hydration).
  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reminders));
  }, [reminders, hydrated]);

  function add(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    setReminders((prev) => [
      { id: crypto.randomUUID(), text: trimmed, date: date || undefined, done: false },
      ...prev,
    ]);
    setText("");
    setDate("");
  }

  function toggle(id: string) {
    setReminders((prev) =>
      prev.map((r) => (r.id === id ? { ...r, done: !r.done } : r))
    );
  }

  function remove(id: string) {
    setReminders((prev) => prev.filter((r) => r.id !== id));
  }

  return (
    <Card title="Quick Reminders">
      <form onSubmit={add} className="mb-3 flex flex-col gap-2 sm:flex-row">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a reminder…"
          className="flex-1 rounded-lg border border-white/10 bg-bg px-3 py-2 text-sm text-ink outline-none focus:border-accent"
        />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="rounded-lg border border-white/10 bg-bg px-3 py-2 text-sm text-ink/70 outline-none focus:border-accent"
        />
        <button
          type="submit"
          className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-bg transition hover:opacity-90"
        >
          Add
        </button>
      </form>

      {hydrated && reminders.length === 0 && (
        <p className="text-sm text-ink/40">No reminders yet.</p>
      )}

      <ul className="space-y-1.5">
        {reminders.map((r) => (
          <li
            key={r.id}
            className="flex items-center gap-3 rounded-lg bg-bg px-3 py-2"
          >
            <input
              type="checkbox"
              checked={r.done}
              onChange={() => toggle(r.id)}
              className="h-4 w-4 shrink-0 accent-accent"
            />
            <div className="min-w-0 flex-1">
              <div
                className={[
                  "truncate text-sm",
                  r.done ? "text-ink/30 line-through" : "text-ink",
                ].join(" ")}
              >
                {r.text}
              </div>
              {r.date && (
                <div className="font-mono text-[11px] text-ink/40">{r.date}</div>
              )}
            </div>
            <button
              onClick={() => remove(r.id)}
              aria-label="Delete reminder"
              className="shrink-0 text-ink/30 transition hover:text-appt"
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </Card>
  );
}
