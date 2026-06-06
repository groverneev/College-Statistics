import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";
import { Category } from "@prisma/client";
import { revalidateTag } from "next/cache";

const VALID_CATEGORIES = Object.values(Category) as string[];

// PATCH /api/my-schools/[slug] — update category
export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { slug } = await params;
  const { category } = await req.json();

  if (!VALID_CATEGORIES.includes(category)) {
    return NextResponse.json({ error: "Invalid category" }, { status: 400 });
  }

  const updated = await prisma.savedSchool.update({
    where: {
      userId_schoolSlug: {
        userId: session.user.id,
        schoolSlug: slug,
      },
    },
    data: { category: category as Category },
  });

  revalidateTag(`saved-schools-${session.user.id}`, { expire: 0 });
  return NextResponse.json(updated);
}

// DELETE /api/my-schools/[slug] — remove a saved school
export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { slug } = await params;

  await prisma.savedSchool.delete({
    where: {
      userId_schoolSlug: {
        userId: session.user.id,
        schoolSlug: slug,
      },
    },
  });

  revalidateTag(`saved-schools-${session.user.id}`, { expire: 0 });
  return NextResponse.json({ success: true });
}
