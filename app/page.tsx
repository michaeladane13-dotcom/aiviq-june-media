import { parseExtraShiftDays, shiftDayIndices } from "@/lib/shifts";
import ShiftSchedule from "@/components/ShiftSchedule";
import UpcomingEvents from "@/components/UpcomingEvents";
import EmailTriage from "@/components/EmailTriage";
import QuickReminders from "@/components/QuickReminders";

export const dynamic = "force-dynamic";

export default function DashboardPage() {
  const extra = parseExtraShiftDays(process.env.EXTRA_SHIFT_DAYS);
  const shiftDays = shiftDayIndices(extra);

  return (
    <main className="mx-auto w-full max-w-xl px-4 pb-16 pt-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-accent">Planner</h1>
          <p className="text-sm text-ink/50">Your week at a glance</p>
        </div>
        <form action="/api/logout" method="POST">
          <button
            type="submit"
            className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-ink/60 transition hover:text-ink"
          >
            Lock
          </button>
        </form>
      </header>

      <div className="space-y-5">
        <ShiftSchedule shiftDays={shiftDays} />
        <UpcomingEvents />
        <EmailTriage />
        <QuickReminders />
      </div>
    </main>
  );
}
