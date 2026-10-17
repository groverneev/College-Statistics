import { desc, eq } from "drizzle-orm";
import { NextResponse } from "next/server";
import { z } from "zod";
import {
  badRequestResponse,
  getAuthenticatedUserId,
  readJson,
  schoolSlugSchema,
  unauthorizedResponse,
} from "@/app/api/my-schools/shared";
import { db } from "@/db";
import { schoolNotes } from "@/db/schema";

const MAX_NOTE_LENGTH = 5000;

const saveNoteSchema = z.object({
  schoolSlug: schoolSlugSchema,
  body: z.string().max(MAX_NOTE_LENGTH).trim().min(1),
});

const noteColumns = {
  schoolSlug: schoolNotes.schoolSlug,
  body: schoolNotes.body,
  updatedAt: schoolNotes.updatedAt,
};

export async function GET() {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const notes = await db
    .select(noteColumns)
    .from(schoolNotes)
    .where(eq(schoolNotes.userId, userId))
    .orderBy(desc(schoolNotes.updatedAt));

  return NextResponse.json(notes);
}

export async function POST(req: Request) {
  const userId = await getAuthenticatedUserId();
  if (!userId) {
    return unauthorizedResponse();
  }

  const parsed = saveNoteSchema.safeParse(await readJson(req));
  if (!parsed.success) {
    return badRequestResponse(parsed.error);
  }

  const { schoolSlug, body } = parsed.data;
  const [note] = await db
    .insert(schoolNotes)
    .values({ userId, schoolSlug, body })
    .onConflictDoUpdate({
      target: [schoolNotes.userId, schoolNotes.schoolSlug],
      set: { body, updatedAt: new Date() },
    })
    .returning(noteColumns);

  return NextResponse.json(note);
}
