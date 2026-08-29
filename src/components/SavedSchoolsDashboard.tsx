"use client";

import Link from "next/link";
import { schoolDataMap } from "@/data/schools";
import SchoolCard from "@/components/SchoolCard";
import { useSavedSchools } from "@/components/SavedSchoolsContext";

type Category = "REACH" | "TARGET" | "SAFETY" | "UNDECIDED";

const CATEGORY_CONFIG: {
  value: Category;
  label: string;
  borderColor: string;
}[] = [
  { value: "REACH", label: "Reach", borderColor: "#ef4444" },
  { value: "TARGET", label: "Target", borderColor: "#f59e0b" },
  { value: "SAFETY", label: "Safety", borderColor: "#22c55e" },
  { value: "UNDECIDED", label: "Undecided", borderColor: "#9ca3af" },
];

export default function SavedSchoolsDashboard() {
  const { savedSchools } = useSavedSchools();
  const hasSaved = savedSchools.length > 0;

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-8">
        <div>
          <h2 className="text-2xl font-semibold text-gray-800">My Schools</h2>
          <p className="text-sm text-gray-500 mt-1">
            {hasSaved
              ? `${savedSchools.length} school${savedSchools.length !== 1 ? "s" : ""} saved`
              : "Start building your college list"}
          </p>
        </div>
        <Link
          href="/schools"
          className="inline-flex min-h-11 items-center text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          Browse all schools &rarr;
        </Link>
      </div>

      {hasSaved ? (
        <div className="space-y-10">
          {CATEGORY_CONFIG.map(({ value, label, borderColor }) => {
            const schoolsInCategory = savedSchools.filter(
              (school) => school.category === value
            );
            if (schoolsInCategory.length === 0) {
              return null;
            }

            return (
              <div key={value}>
                <div
                  className="flex items-baseline space-x-3 mb-4 pl-3 border-l-4"
                  style={{ borderColor }}
                >
                  <span className="text-sm font-semibold uppercase tracking-widest text-gray-700">
                    {label}
                  </span>
                  <span className="text-sm text-gray-400">
                    {schoolsInCategory.length} school
                    {schoolsInCategory.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {schoolsInCategory.map(({ schoolSlug }) => {
                    const school = schoolDataMap[schoolSlug];
                    return school ? (
                      <SchoolCard
                        key={schoolSlug}
                        school={school}
                        showSaveButton
                      />
                    ) : null;
                  })}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-gray-200">
          <div className="text-4xl mb-4" aria-hidden="true">📚</div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Start building your college list
          </h3>
          <p className="text-gray-500 mb-6 max-w-sm mx-auto">
            Browse schools and save them as Reach, Target, or Safety to build
            your list.
          </p>
          <Link
            href="/schools"
            className="inline-flex min-h-11 items-center px-5 py-2.5 bg-gray-800 text-white rounded-lg font-medium text-sm hover:bg-gray-700 transition-colors"
          >
            Browse all schools &rarr;
          </Link>
        </div>
      )}
    </div>
  );
}
