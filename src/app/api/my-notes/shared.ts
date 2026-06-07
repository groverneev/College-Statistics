import { revalidateTag } from "next/cache";
import { NextResponse } from "next/server";

// Re-export the shared auth + slug helpers so notes routes match the saved-schools pattern.
export {
  getAuthenticatedUserId,
  invalidSchoolSlugResponse,
  isValidSchoolSlug,
  unauthorizedResponse,
} from "@/app/api/my-schools/shared";

export const MAX_NOTE_LENGTH = 5000;

export function invalidNoteBodyResponse() {
  return NextResponse.json(
    { error: `Note must be a non-empty string of at most ${MAX_NOTE_LENGTH} characters` },
    { status: 400 }
  );
}

export function isValidNoteBody(body: unknown): body is string {
  return typeof body === "string" && body.trim().length > 0 && body.length <= MAX_NOTE_LENGTH;
}

export function revalidateNotes(userId: string) {
  revalidateTag(`school-notes-${userId}`, { expire: 0 });
}
