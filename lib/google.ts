import { google } from "googleapis";

/**
 * Build an OAuth2 client primed with the long-lived refresh token. Returns
 * null when the Google credentials have not been configured yet so callers
 * can render a friendly "not configured" state instead of crashing.
 */
export function getOAuthClient() {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const refreshToken = process.env.GOOGLE_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    return null;
  }

  const client = new google.auth.OAuth2(clientId, clientSecret);
  client.setCredentials({ refresh_token: refreshToken });
  return client;
}

// Simple in-process cache to keep us well under Google rate limits. On
// Vercel this is best-effort (per warm lambda) but avoids hammering the API
// on rapid refreshes. TTL is 30 minutes per the brief.
const TTL_MS = 30 * 60 * 1000;
const store = new Map<string, { ts: number; data: unknown }>();

export async function cached<T>(key: string, fn: () => Promise<T>): Promise<{
  data: T;
  fetchedAt: number;
}> {
  const hit = store.get(key);
  const now = Date.now();
  if (hit && now - hit.ts < TTL_MS) {
    return { data: hit.data as T, fetchedAt: hit.ts };
  }
  const data = await fn();
  store.set(key, { ts: now, data });
  return { data, fetchedAt: now };
}
