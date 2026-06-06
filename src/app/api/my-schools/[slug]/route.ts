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

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const { slug } = await params;
  const { category } = await req.json();

  if (!isValidSchoolSlug(slug)) {
    return invalidSchoolSlugResponse();
  }
  if (!isValidCategory(category)) {
    return invalidCategoryResponse();
  }

  const updated = await prisma.savedSchool.update({
    where: {
      userId_schoolSlug: {
        userId,
        schoolSlug: slug,
      },
    },
    data: { category },
  });

  revalidateSavedSchools(userId);
  return NextResponse.json(updated);
}

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const { slug } = await params;
  if (!isValidSchoolSlug(slug)) {
    return invalidSchoolSlugResponse();
  }

  await prisma.savedSchool.delete({
    where: {
      userId_schoolSlug: {
        userId,
        schoolSlug: slug,
      },
    },
  });

  revalidateSavedSchools(userId);
  return NextResponse.json({ success: true });
}
