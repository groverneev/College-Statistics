import { NextResponse } from "next/server";
import {
  getInternationalPreviewToken,
  INTERNATIONAL_PREVIEW_COOKIE,
  INTERNATIONAL_PREVIEW_MAX_AGE,
  matchesInternationalPreviewPassword,
} from "@/lib/internationalPreview";

export async function POST(request: Request) {
  const expectedPassword = process.env.REPORTER_PREVIEW_PASSWORD;
  if (!expectedPassword) {
    return NextResponse.json(
      { error: "Preview access is not configured." },
      { status: 503 },
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Enter the preview password." }, { status: 400 });
  }

  const suppliedPassword =
    typeof body === "object" && body !== null && "password" in body
      ? (body as { password?: unknown }).password
      : null;

  if (
    typeof suppliedPassword !== "string" ||
    !matchesInternationalPreviewPassword(suppliedPassword, expectedPassword)
  ) {
    return NextResponse.json({ error: "That password is not correct." }, { status: 401 });
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set({
    name: INTERNATIONAL_PREVIEW_COOKIE,
    value: getInternationalPreviewToken(expectedPassword),
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: INTERNATIONAL_PREVIEW_MAX_AGE,
    path: "/",
  });
  return response;
}
