// Shared auth helpers. Runs in both edge (middleware) and node (route handlers)
// via the Web Crypto API, which is available in both runtimes on Vercel.

export const SESSION_COOKIE = "planner_session";

/**
 * Derive an opaque session token from the dashboard password so the raw
 * password is never stored in the browser cookie.
 */
export async function deriveToken(password: string): Promise<string> {
  const data = new TextEncoder().encode(`planner:${password}`);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
