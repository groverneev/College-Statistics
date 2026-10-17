import { NextResponse } from "next/server";
import { z } from "zod";
import { availableSchoolSlugs } from "@/data/schools";
import { categoryEnum } from "@/db/schema";
import { getSession } from "@/lib/auth";

export const schoolSlugSchema = z.enum(availableSchoolSlugs as [string, ...string[]]);
export const categorySchema = z.enum(categoryEnum.enumValues);

export async function getAuthenticatedUserId(): Promise<string | null> {
  const session = await getSession();
  return session?.user.id ?? null;
}

export function unauthorizedResponse() {
  return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
}

export function badRequestResponse(error: z.ZodError) {
  return NextResponse.json({ error: z.prettifyError(error) }, { status: 400 });
}

export async function readJson(req: Request): Promise<unknown> {
  try {
    return await req.json();
  } catch {
    return null;
  }
}
