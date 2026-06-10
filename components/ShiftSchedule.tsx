"use client";

import { useMemo } from "react";
import Card from "./Card";

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function ShiftSchedule({ shiftDays }: { shiftDays: number[] }) {
  const { week, nextShiftLabel, todayIdx } = useMemo(() => {
    const shiftSet = new Set(shiftDays);
    const today = new Date();
    const todayIdx = today.getDay();

    // Build a 7-day strip starting today.
    const week = Array.from({ length: 7 }, (_, offset) => {
      const d = new Date(today);
      d.setDate(today.getDate() + offset);
      const dow = d.getDay();
      return {
        offset,
        dow,
        label: DAY_LABELS[dow],
        dateNum: d.getDate(),
        isShift: shiftSet.has(dow),
        isToday: offset === 0,
      };
    });

    // "Next shift in X days" — look forward up to 7 days.
    let nextShiftLabel = "No shifts scheduled this week";
    for (let i = 0; i < 7; i++) {
      if (shiftSet.has((todayIdx + i) % 7)) {
        if (i === 0) nextShiftLabel = "You're on shift today";
        else if (i === 1) nextShiftLabel = "Next shift tomorrow";
        else nextShiftLabel = `Next shift in ${i} days`;
        break;
      }
    }

    return { week, nextShiftLabel, todayIdx };
  }, [shiftDays]);

  return (
    <Card title="This Week — Shifts">
      <p className="mb-4 text-sm text-accent">{nextShiftLabel}</p>
      <div className="grid grid-cols-7 gap-1.5">
        {week.map((d) => (
          <div
            key={d.offset}
            className={[
              "flex flex-col items-center rounded-lg py-2 text-center",
              d.isShift ? "bg-shift text-ink" : "bg-bg text-ink/40",
              d.isToday ? "ring-2 ring-accent" : "",
            ].join(" ")}
          >
            <span className="text-[10px] font-medium uppercase">{d.label}</span>
            <span className="font-mono text-sm">{d.dateNum}</span>
            <span className="mt-1 text-[9px] uppercase tracking-wide">
              {d.isShift ? "Shift" : "Off"}
            </span>
          </div>
        ))}
      </div>
      <p className="mt-3 text-[11px] text-ink/40">
        Sun/Mon/Tue are fixed night shifts. Extra days set via{" "}
        <span className="font-mono">EXTRA_SHIFT_DAYS</span>.
      </p>
    </Card>
  );
}
