import { and, eq } from "drizzle-orm";
import { NextResponse } from "next/server";
import { z } from "zod";
import {
  badRequestResponse,
  categorySchema,
  getAuthenticatedUserId,
  readJson,
  schoolSlugSchema,
  unauthorizedResponse,
} from "@/app/api/my-schools/shared";
import { db } from "@/db";
import { savedSchools } from "@/db/schema";

const updateSchema = z.object({ category: categorySchema });

export async function PATCH(req: Request, { params }: { params: Promise<{ slug: string }> }) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const slug = schoolSlugSchema.safeParse((await params).slug);
  if (!slug.success) {
    return badRequestResponse(slug.error);
  }
  const body = updateSchema.safeParse(await readJson(req));
  if (!body.success) {
    return badRequestResponse(body.error);
  }

  const [updated] = await db
    .update(savedSchools)
    .set({ category: body.data.category })
    .where(and(eq(savedSchools.userId, userId), eq(savedSchools.schoolSlug, slug.data)))
    .returning({ schoolSlug: savedSchools.schoolSlug, category: savedSchools.category });

  if (!updated) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  return NextResponse.json(updated);
}

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
    .delete(savedSchools)
    .where(and(eq(savedSchools.userId, userId), eq(savedSchools.schoolSlug, slug.data)));

  return NextResponse.json({ success: true });
}
