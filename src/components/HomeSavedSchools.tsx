"use client";

import Link from "next/link";
import { useSavedSchools } from "@/components/SavedSchoolsContext";
import { schoolDataMap } from "@/data/schools";
import { getLatestYearData, formatPercent } from "@/utils/dataHelpers";

type Category = "REACH" | "TARGET" | "SAFETY" | "UNDECIDED";

const CATEGORY_CONFIG: { value: Category; label: string; color: string }[] = [
  { value: "REACH", label: "Reach", color: "#ef4444" },
  { value: "TARGET", label: "Target", color: "#f59e0b" },
  { value: "SAFETY", label: "Safety", color: "#22c55e" },
  { value: "UNDECIDED", label: "Undecided", color: "#9ca3af" },
];

export default function HomeSavedSchools() {
  const { isLoggedIn, savedSchools } = useSavedSchools();

  if (!isLoggedIn || savedSchools.length === 0) return null;

  return (
    <div className="max-w-6xl mx-auto px-6 sm:px-4 -mt-8 pb-10 sm:pb-12">
      <div className="flex items-baseline justify-between mb-5">
        <h2 className="section-label">Your schools</h2>
        <Link href="/my-schools" className="browse-all-btn">
          My Schools
          <span aria-hidden>&rarr;</span>
        </Link>
      </div>

      <div className="space-y-3">
        {CATEGORY_CONFIG.map(({ value, label, color }) => {
          const schools = savedSchools
            .filter((saved) => saved.category === value)
            .map((saved) => ({ saved, school: schoolDataMap[saved.schoolSlug] }))
            .filter((entry) => Boolean(entry.school));

          if (schools.length === 0) return null;

          return (
            <div
              key={value}
              className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4"
            >
              <div className="flex items-center gap-2 flex-shrink-0 sm:w-28">
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ background: color }}
                  aria-hidden
                />
                <span
                  className="text-xs font-semibold uppercase tracking-wide"
                  style={{ color: "#5a5f66" }}
                >
                  {label}
                </span>
                <span className="text-xs" style={{ color: "#9ca1a8" }}>
                  {schools.length}
                </span>
              </div>

              <div className="flex flex-wrap gap-2">
                {schools.map(({ saved, school }) => {
                  const rate = getLatestYearData(school!)?.admissions.acceptanceRate;
                  return (
                    <Link
                      key={saved.schoolSlug}
                      href={`/${saved.schoolSlug}`}
                      className="chip-dark flex items-center gap-1.5 rounded-full px-3 py-1 text-sm"
                    >
                      {school!.name}
                      {rate !== undefined && (
                        <span style={{ color: "#9ca1a8" }}>
                          {formatPercent(rate)}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
