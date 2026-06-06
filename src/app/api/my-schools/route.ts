import { Category } from "@prisma/client";
import { NextResponse } from "next/server";
import {
  getAuthenticatedUserId,
  invalidCategoryResponse,
  invalidSchoolSlugResponse,
  isValidCategory,
  isValidSchoolSlug,
  revalidateSavedSchools,
  unauthorizedResponse,
} from "@/app/api/my-schools/shared";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const saved = await prisma.savedSchool.findMany({
    where: { userId },
    select: { schoolSlug: true, category: true },
    orderBy: { savedAt: "desc" },
  });

  return NextResponse.json(saved);
}

export async function POST(req: Request) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const { schoolSlug, category } = await req.json();
  if (!isValidSchoolSlug(schoolSlug)) {
    return invalidSchoolSlugResponse();
  }

  const resolvedCategory = category ?? Category.UNDECIDED;
  if (!isValidCategory(resolvedCategory)) {
    return invalidCategoryResponse();
  }

  const saved = await prisma.savedSchool.upsert({
    where: {
      userId_schoolSlug: {
        userId,
        schoolSlug,
      },
    },
    update: { category: resolvedCategory },
    create: {
      userId,
      schoolSlug,
      category: resolvedCategory,
    },
  });

  revalidateSavedSchools(userId);
  return NextResponse.json(saved);
}
