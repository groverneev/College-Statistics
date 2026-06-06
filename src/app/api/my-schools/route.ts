import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";
import { Category } from "@prisma/client";
import { revalidateTag } from "next/cache";

// GET /api/my-schools — fetch the logged-in user's saved schools
export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const saved = await prisma.savedSchool.findMany({
    where: { userId: session.user.id },
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
  if (!schoolSlug) {
    return NextResponse.json({ error: "schoolSlug is required" }, { status: 400 });
  }

  const saved = await prisma.savedSchool.upsert({
    where: {
      userId_schoolSlug: {
        userId: session.user.id,
        schoolSlug,
      },
    },
    update: { category: category ?? Category.UNDECIDED },
    create: {
      userId: session.user.id,
      schoolSlug,
      category: category ?? Category.UNDECIDED,
    },
  });

  revalidateTag(`saved-schools-${session.user.id}`, { expire: 0 });
  return NextResponse.json(saved);
}
