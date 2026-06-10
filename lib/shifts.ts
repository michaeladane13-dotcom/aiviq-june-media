// Shift schedule logic, shared between server (env parsing) and client.

export const DAY_CODES = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"] as const;
export type DayCode = (typeof DAY_CODES)[number];

// Sun/Mon/Tue are always night shifts (RainCity Housing).
const FIXED_SHIFT_DAYS: DayCode[] = ["SUN", "MON", "TUE"];

// Extras only ever apply to Wed-Sat.
const ALLOWED_EXTRA_DAYS: DayCode[] = ["WED", "THU", "FRI", "SAT"];

/** Parse the EXTRA_SHIFT_DAYS env var into a validated set of day codes. */
export function parseExtraShiftDays(raw: string | undefined): DayCode[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((s) => s.trim().toUpperCase())
    .filter((s): s is DayCode =>
      (ALLOWED_EXTRA_DAYS as string[]).includes(s)
    );
}

/** Full set of shift day indices (0=Sun..6=Sat) for the active schedule. */
export function shiftDayIndices(extra: DayCode[]): number[] {
  const all = new Set<DayCode>([...FIXED_SHIFT_DAYS, ...extra]);
  return DAY_CODES.map((code, i) => (all.has(code) ? i : -1)).filter(
    (i) => i >= 0
  );
}
