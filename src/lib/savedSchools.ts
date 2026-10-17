import { cache } from "react";
import { unstable_cache } from "next/cache";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export const getSession = cache(() => getServerSession(authOptions));

export function getSavedSchoolsForUser(userId: string) {
  return unstable_cache(
    () =>
      prisma.savedSchool.findMany({
        where: { userId },
        select: { schoolSlug: true, category: true },
      }),
    [`saved-schools-${userId}`],
    { tags: [`saved-schools-${userId}`] }
  )();
}
