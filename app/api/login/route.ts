import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE, deriveToken } from "@/lib/auth";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const password = String(form.get("password") ?? "");
  const expected = process.env.DASHBOARD_PASSWORD;

  if (!expected || password !== expected) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("error", "1");
    return NextResponse.redirect(url, { status: 303 });
  }

  const from = form.get("from");
  const dest = req.nextUrl.clone();
  dest.pathname = typeof from === "string" && from.startsWith("/") ? from : "/";
  dest.search = "";

  const res = NextResponse.redirect(dest, { status: 303 });
  res.cookies.set(SESSION_COOKIE, await deriveToken(expected), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 30, // 30 days
  });
  return res;
}
