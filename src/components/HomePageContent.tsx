"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { SchoolData, SCHOOL_COLORS } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import SaveSchoolButton from "@/components/SaveSchoolButton";
import { useSavedSchools } from "@/components/SavedSchoolsContext";

type Category = "REACH" | "TARGET" | "SAFETY" | "UNDECIDED";

// Curated schools shown on the logged-out homepage (order matters)
const FEATURED_SLUGS = ["stanford", "mit", "harvard"];

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

interface HomePageContentProps {
  allSchools: SchoolData[];
}

export default function HomePageContent({ allSchools }: HomePageContentProps) {
  const { data: session } = useSession();
  const { savedSchools, isLoggedIn } = useSavedSchools();

  const schoolDataMap = Object.fromEntries(
    allSchools.map((s) => [s.slug, s])
  );

  // Logged in (isLoggedIn comes from the server via context, so SSR renders correctly)
  if (isLoggedIn || session) {
    const hasSaved = savedSchools.length > 0;

    return (
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-semibold text-gray-800">
              My Schools
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {hasSaved
                ? `${savedSchools.length} school${savedSchools.length !== 1 ? "s" : ""} saved`
                : "Start building your college list"}
            </p>
          </div>
          <Link
            href="/schools"
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Browse all schools →
          </Link>
        </div>

        {hasSaved ? (
          <div className="space-y-10">
            {CATEGORY_CONFIG.map(({ value, label, borderColor }) => {
              const schoolsInCategory = savedSchools.filter(
                (s) => s.category === value
              );
              if (schoolsInCategory.length === 0) return null;

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
                      if (!school) return null;

                      const years = Object.keys(school.years).sort();
                      const latestYear = years[years.length - 1];
                      const latestData = school.years[latestYear];
                      const schoolColor =
                        SCHOOL_COLORS[school.slug] || "#4B5563";

                      return (
                        <div key={schoolSlug} className="relative">
                          <div className="absolute top-3 right-3 z-10">
                            <SaveSchoolButton
                              schoolSlug={school.slug}
                              schoolName={school.name}
                              variant="icon"
                            />
                          </div>
                          <Link href={`/${school.slug}`}>
                            <div
                              className="card p-6 hover:shadow-lg transition-shadow cursor-pointer border-t-4"
                              style={{ borderTopColor: schoolColor }}
                            >
                              <h3
                                className="text-xl font-semibold mb-1 pr-8"
                                style={{ color: schoolColor }}
                              >
                                {school.name}
                              </h3>
                              <p className="text-sm text-gray-500 mb-4">
                                {years.length} years of data (
                                {years[0].split("-")[0]}-
                                {latestYear.split("-")[1]})
                              </p>
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <div className="text-2xl font-bold text-gray-800">
                                    {formatPercent(
                                      latestData.admissions.acceptanceRate
                                    )}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Acceptance Rate
                                  </div>
                                </div>
                                <div>
                                  <div className="text-2xl font-bold text-gray-800">
                                    {formatNumber(latestData.admissions.enrolled)}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Class Size
                                  </div>
                                </div>
                                {latestData.testScores.sat && (
                                  <div>
                                    <div className="text-lg font-semibold text-gray-700">
                                      {latestData.testScores.sat.composite.p25}-
                                      {latestData.testScores.sat.composite.p75}
                                    </div>
                                    <div className="text-xs text-gray-500">
                                      SAT Range
                                    </div>
                                  </div>
                                )}
                                <div>
                                  <div className="text-lg font-semibold text-gray-700">
                                    $
                                    {(
                                      latestData.costs.totalCOA / 1000
                                    ).toFixed(0)}
                                    k
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Total Cost
                                  </div>
                                </div>
                              </div>
                              <div className="mt-4 pt-4 border-t border-gray-100">
                                <span
                                  className="text-sm font-medium"
                                  style={{ color: schoolColor }}
                                >
                                  View Dashboard &rarr;
                                </span>
                              </div>
                            </div>
                          </Link>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          // Empty state
          <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-gray-200">
            <div className="text-4xl mb-4">🎓</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Your college list is empty
            </h3>
            <p className="text-gray-500 mb-6 max-w-sm mx-auto">
              Browse schools and save them as Reach, Target, or Safety to build
              your list.
            </p>
            <Link
              href="/schools"
              className="inline-flex items-center px-5 py-2.5 bg-gray-800 text-white rounded-lg font-medium text-sm hover:bg-gray-700 transition-colors"
            >
              Browse all schools →
            </Link>
          </div>
        )}
      </div>
    );
  }

  // Logged out — curated featured schools + link to the full list
  const featuredSchools = FEATURED_SLUGS.map((slug) => schoolDataMap[slug]).filter(
    (s): s is SchoolData => Boolean(s)
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">
          Featured Schools
        </h2>
        <Link
          href="/schools"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          Browse all schools →
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featuredSchools.map((school: SchoolData) => {
          const years = Object.keys(school.years).sort();
          const latestYear = years[years.length - 1];
          const latestData = school.years[latestYear];
          const color = SCHOOL_COLORS[school.slug] || "#4B5563";

          return (
            <Link key={school.slug} href={`/${school.slug}`}>
              <div
                className="card p-6 hover:shadow-lg transition-shadow cursor-pointer border-t-4"
                style={{ borderTopColor: color }}
              >
                <h3 className="text-xl font-semibold mb-1" style={{ color }}>
                  {school.name}
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  {years.length} years of data ({years[0].split("-")[0]}-
                  {latestYear.split("-")[1]})
                </p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-2xl font-bold text-gray-800">
                      {formatPercent(latestData.admissions.acceptanceRate)}
                    </div>
                    <div className="text-xs text-gray-500">Acceptance Rate</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-800">
                      {formatNumber(latestData.admissions.enrolled)}
                    </div>
                    <div className="text-xs text-gray-500">Class Size</div>
                  </div>
                  {latestData.testScores.sat && (
                    <div>
                      <div className="text-lg font-semibold text-gray-700">
                        {latestData.testScores.sat.composite.p25}-
                        {latestData.testScores.sat.composite.p75}
                      </div>
                      <div className="text-xs text-gray-500">SAT Range</div>
                    </div>
                  )}
                  <div>
                    <div className="text-lg font-semibold text-gray-700">
                      ${(latestData.costs.totalCOA / 1000).toFixed(0)}k
                    </div>
                    <div className="text-xs text-gray-500">Total Cost</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <span className="text-sm font-medium" style={{ color }}>
                    View Dashboard &rarr;
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
