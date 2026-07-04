"use client";

import Link from "next/link";
import { useSavedSchools } from "@/components/SavedSchoolsContext";
import { schoolDataMap } from "@/data/schools";
import SchoolCard from "@/components/SchoolCard";

const MAX_PREVIEW = 6;

export default function HomeSavedSchools() {
  const { isLoggedIn, savedSchools } = useSavedSchools();

  if (!isLoggedIn || savedSchools.length === 0) return null;

  const schools = savedSchools
    .map((saved) => schoolDataMap[saved.schoolSlug])
    .filter((school): school is NonNullable<typeof school> => Boolean(school));

  if (schools.length === 0) return null;

  const preview = schools.slice(0, MAX_PREVIEW);

  return (
    <div className="max-w-6xl mx-auto px-4 pt-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">
          Your saved schools
        </h2>
        <Link
          href="/my-schools"
          className="text-sm font-medium text-blue-600 hover:text-blue-700 whitespace-nowrap"
        >
          {schools.length > MAX_PREVIEW
            ? `View all ${schools.length} saved`
            : "Go to My Schools"}{" "}
          &rarr;
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {preview.map((school) => (
          <SchoolCard key={school.slug} school={school} showSaveButton />
        ))}
      </div>
    </div>
  );
}
