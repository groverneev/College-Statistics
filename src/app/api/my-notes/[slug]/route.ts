import { NextResponse } from "next/server";
import {
  getAuthenticatedUserId,
  invalidSchoolSlugResponse,
  isValidSchoolSlug,
  revalidateNotes,
  unauthorizedResponse,
} from "@/app/api/my-notes/shared";
import { prisma } from "@/lib/prisma";

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

  await prisma.schoolNote.deleteMany({
    where: { userId, schoolSlug: slug },
  });

  revalidateNotes(userId);
  return NextResponse.json({ success: true });
}
