"use client";

import Link from "next/link";
import { useSavedSchools } from "@/components/SavedSchoolsContext";
import { schoolDataMap } from "@/data/schools";

const CATEGORY_COLORS: Record<string, string> = {
  REACH: "#ef4444",
  TARGET: "#f59e0b",
  SAFETY: "#22c55e",
  UNDECIDED: "#9ca3af",
};

export default function HomeSavedSchools() {
  const { isLoggedIn, savedSchools } = useSavedSchools();

  if (!isLoggedIn || savedSchools.length === 0) return null;

  const schools = savedSchools
    .map((saved) => ({
      saved,
      school: schoolDataMap[saved.schoolSlug],
    }))
    .filter((entry) => Boolean(entry.school));

  if (schools.length === 0) return null;

  return (
    <div className="max-w-6xl mx-auto px-4 pt-14">
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="section-label">Your schools</h2>
        <Link
          href="/my-schools"
          className="text-sm font-medium link-dark whitespace-nowrap"
        >
          My Schools &rarr;
        </Link>
      </div>
      <div className="flex flex-wrap gap-2">
        {schools.map(({ saved, school }) => (
          <Link
            key={saved.schoolSlug}
            href={`/${saved.schoolSlug}`}
            className="chip-dark flex items-center gap-2 rounded-full px-3.5 py-1.5 text-sm font-medium"
          >
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{
                background:
                  CATEGORY_COLORS[saved.category] ?? CATEGORY_COLORS.UNDECIDED,
              }}
              aria-hidden
              title={saved.category.toLowerCase()}
            />
            {school.name}
          </Link>
        ))}
      </div>
    </div>
  );
}
