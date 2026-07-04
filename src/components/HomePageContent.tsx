import Link from "next/link";
import { allSchools } from "@/data/schools";
import { getLatestYearData } from "@/utils/dataHelpers";
import SchoolCard from "@/components/SchoolCard";
import { SchoolData } from "@/lib/types";

const SAMPLE_COUNT = 8;

// Pick a deterministic sample that spans the selectivity range, so the homepage
// preview doesn't read as an all-Ivy list. Schools are sorted by latest
// acceptance rate, then sampled at even intervals across that ordering.
function getSampleSchools(): SchoolData[] {
  const ranked = allSchools
    .map((school) => ({
      school,
      rate: getLatestYearData(school)?.admissions.acceptanceRate ?? null,
    }))
    .filter((entry): entry is { school: SchoolData; rate: number } =>
      entry.rate !== null
    )
    .sort((a, b) => a.rate - b.rate);

  if (ranked.length <= SAMPLE_COUNT) {
    return ranked.map((entry) => entry.school);
  }

  const step = (ranked.length - 1) / (SAMPLE_COUNT - 1);
  const picks: SchoolData[] = [];
  for (let i = 0; i < SAMPLE_COUNT; i++) {
    picks.push(ranked[Math.round(i * step)].school);
  }
  return picks;
}

export default function HomePageContent() {
  const sampleSchools = getSampleSchools();
  const totalSchools = allSchools.length;

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">Sample schools</h2>
        <Link
          href="/schools"
          className="text-sm font-medium text-blue-600 hover:text-blue-700 whitespace-nowrap"
        >
          Browse all {totalSchools}{" "}schools &rarr;
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sampleSchools.map((school) => (
          <SchoolCard key={school.slug} school={school} showSaveButton />
        ))}
      </div>

      <div className="mt-8 text-center">
        <Link
          href="/schools"
          className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-gray-800 text-white font-medium hover:bg-gray-900 transition-colors"
        >
          Browse all {totalSchools} Schools
        </Link>
      </div>
    </div>
  );
}
