import { Suspense } from "react";

function LoginForm({
  searchParams,
}: {
  searchParams: { from?: string; error?: string };
}) {
  const from = typeof searchParams.from === "string" ? searchParams.from : "/";
  const hasError = searchParams.error === "1";

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <form
        action="/api/login"
        method="POST"
        className="w-full max-w-sm rounded-2xl bg-card p-6 shadow-xl"
      >
        <h1 className="mb-1 text-xl font-semibold text-accent">Planner</h1>
        <p className="mb-6 text-sm text-ink/60">Enter your password to continue.</p>

        <input type="hidden" name="from" value={from} />
        <input
          type="password"
          name="password"
          autoFocus
          required
          placeholder="Password"
          className="w-full rounded-lg border border-white/10 bg-bg px-4 py-3 text-ink outline-none focus:border-accent"
        />

        {hasError && (
          <p className="mt-3 text-sm text-appt">Incorrect password. Try again.</p>
        )}

        <button
          type="submit"
          className="mt-5 w-full rounded-lg bg-accent py-3 font-semibold text-bg transition hover:opacity-90"
        >
          Unlock
        </button>
      </form>
    </main>
  );
}

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ from?: string; error?: string }>;
}) {
  const params = await searchParams;
  return (
    <Suspense>
      <LoginForm searchParams={params} />
    </Suspense>
  );
}
