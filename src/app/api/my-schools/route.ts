import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";
import { Category } from "@prisma/client";
import { revalidateTag } from "next/cache";
import { availableSchoolSlugs } from "@/data/schools";

const VALID_CATEGORIES = Object.values(Category) as string[];

// GET /api/my-schools — fetch the logged-in user's saved schools
export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const saved = await prisma.savedSchool.findMany({
    where: { userId: session.user.id },
    select: { schoolSlug: true, category: true },
    orderBy: { savedAt: "desc" },
  });

  return NextResponse.json(saved);
}

// POST /api/my-schools — save a school
export async function POST(req: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { schoolSlug, category } = await req.json();

  if (!schoolSlug || !availableSchoolSlugs.includes(schoolSlug)) {
    return NextResponse.json({ error: "Invalid schoolSlug" }, { status: 400 });
  }

  const resolvedCategory: Category = category ?? Category.UNDECIDED;
  if (!VALID_CATEGORIES.includes(resolvedCategory)) {
    return NextResponse.json({ error: "Invalid category" }, { status: 400 });
  }

  const saved = await prisma.savedSchool.upsert({
    where: {
      userId_schoolSlug: {
        userId: session.user.id,
        schoolSlug,
      },
    },
    update: { category: resolvedCategory },
    create: {
      userId: session.user.id,
      schoolSlug,
      category: resolvedCategory,
    },
  });

  revalidateTag(`saved-schools-${session.user.id}`, { expire: 0 });
  return NextResponse.json(saved);
}
