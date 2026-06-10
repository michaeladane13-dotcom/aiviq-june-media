import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE, deriveToken } from "@/lib/auth";

// Paths that never require the password gate.
const PUBLIC_PATHS = ["/login", "/api/login", "/api/logout"];

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const password = process.env.DASHBOARD_PASSWORD;

  // If no password is configured the gate is effectively disabled so the
  // owner can still get in (e.g. before secrets are set in Vercel).
  if (!password) {
    return NextResponse.next();
  }

  const expected = await deriveToken(password);
  const token = req.cookies.get(SESSION_COOKIE)?.value;

  if (token && token === expected) {
    return NextResponse.next();
  }

  const loginUrl = req.nextUrl.clone();
  loginUrl.pathname = "/login";
  loginUrl.searchParams.set("from", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  // Protect everything except Next internals and static assets.
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
