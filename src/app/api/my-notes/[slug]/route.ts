import { and, eq } from "drizzle-orm";
import { NextResponse } from "next/server";
import {
  badRequestResponse,
  getAuthenticatedUserId,
  schoolSlugSchema,
  unauthorizedResponse,
} from "@/app/api/my-schools/shared";
import { db } from "@/db";
import { schoolNotes } from "@/db/schema";

export async function DELETE(_req: Request, { params }: { params: Promise<{ slug: string }> }) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const slug = schoolSlugSchema.safeParse((await params).slug);
  if (!slug.success) {
    return badRequestResponse(slug.error);
  }

  await db
    .delete(schoolNotes)
    .where(and(eq(schoolNotes.userId, userId), eq(schoolNotes.schoolSlug, slug.data)));

  return NextResponse.json({ success: true });
}
