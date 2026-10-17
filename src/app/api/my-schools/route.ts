import { desc, eq } from "drizzle-orm";
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

const saveSchoolSchema = z.object({
  schoolSlug: schoolSlugSchema,
  category: categorySchema.default("UNDECIDED"),
});

export async function GET() {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const saved = await db
    .select({ schoolSlug: savedSchools.schoolSlug, category: savedSchools.category })
    .from(savedSchools)
    .where(eq(savedSchools.userId, userId))
    .orderBy(desc(savedSchools.savedAt));

  return NextResponse.json(saved);
}

export async function POST(req: Request) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const parsed = saveSchoolSchema.safeParse(await readJson(req));
  if (!parsed.success) {
    return badRequestResponse(parsed.error);
  }

  const { schoolSlug, category } = parsed.data;
  const [saved] = await db
    .insert(savedSchools)
    .values({ userId, schoolSlug, category })
    .onConflictDoUpdate({
      target: [savedSchools.userId, savedSchools.schoolSlug],
      set: { category },
    })
    .returning({ schoolSlug: savedSchools.schoolSlug, category: savedSchools.category });

  return NextResponse.json(saved);
}
