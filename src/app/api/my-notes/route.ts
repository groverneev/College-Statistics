import { NextResponse } from "next/server";
import {
  getAuthenticatedUserId,
  invalidNoteBodyResponse,
  invalidSchoolSlugResponse,
  isValidNoteBody,
  isValidSchoolSlug,
  revalidateNotes,
  unauthorizedResponse,
} from "@/app/api/my-notes/shared";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const notes = await prisma.schoolNote.findMany({
    where: { userId },
    select: { schoolSlug: true, body: true, updatedAt: true },
    orderBy: { updatedAt: "desc" },
  });

  return NextResponse.json(notes);
}

export async function POST(req: Request) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const { schoolSlug, body } = await req.json();
  if (!isValidSchoolSlug(schoolSlug)) {
    return invalidSchoolSlugResponse();
  }
  if (!isValidNoteBody(body)) {
    return invalidNoteBodyResponse();
  }

  const trimmed = body.trim();
  const note = await prisma.schoolNote.upsert({
    where: { userId_schoolSlug: { userId, schoolSlug } },
    update: { body: trimmed },
    create: { userId, schoolSlug, body: trimmed },
    select: { schoolSlug: true, body: true, updatedAt: true },
  });

  revalidateNotes(userId);
  return NextResponse.json(note);
}
