import { Category } from "@prisma/client";
import { getServerSession } from "next-auth";
import { revalidateTag } from "next/cache";
import { NextResponse } from "next/server";
import { availableSchoolSlugs } from "@/data/schools";
import { authOptions } from "@/lib/auth";

const VALID_CATEGORIES = new Set(Object.values(Category));
const VALID_SCHOOL_SLUGS = new Set(availableSchoolSlugs);

export async function getAuthenticatedUserId(): Promise<string | null> {
  const session = await getServerSession(authOptions);
  return session?.user?.id ?? null;
}

export function unauthorizedResponse() {
  return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
}

export function invalidCategoryResponse() {
  return NextResponse.json({ error: "Invalid category" }, { status: 400 });
}

export function invalidSchoolSlugResponse() {
  return NextResponse.json({ error: "Invalid schoolSlug" }, { status: 400 });
}

export function isValidCategory(category: unknown): category is Category {
  return typeof category === "string" && VALID_CATEGORIES.has(category as Category);
}

export function isValidSchoolSlug(schoolSlug: unknown): schoolSlug is string {
  return typeof schoolSlug === "string" && VALID_SCHOOL_SLUGS.has(schoolSlug);
}

export function revalidateSavedSchools(userId: string) {
  revalidateTag(`saved-schools-${userId}`, { expire: 0 });
}
