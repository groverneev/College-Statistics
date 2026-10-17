import { unstable_cache } from "next/cache";
import { prisma } from "@/lib/prisma";

export function getNotesForUser(userId: string) {
  return unstable_cache(
    () =>
      prisma.schoolNote.findMany({
        where: { userId },
        select: { schoolSlug: true, body: true, updatedAt: true },
      }),
    [`school-notes-${userId}`],
    { tags: [`school-notes-${userId}`] }
  )();
}
