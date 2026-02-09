import Link from "next/link";
import { SchoolData, SCHOOL_COLORS } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import SearchBar from "@/components/SearchBar";

// Import school data
import brownData from "@/data/schools/brown.json";
import caltechData from "@/data/schools/caltech.json";
import cornellData from "@/data/schools/cornell.json";
import dartmouthData from "@/data/schools/dartmouth.json";
import harvardData from "@/data/schools/harvard.json";
import princetonData from "@/data/schools/princeton.json";
import stanfordData from "@/data/schools/stanford.json";
import uclaData from "@/data/schools/ucla.json";
import upennData from "@/data/schools/upenn.json";
import yaleData from "@/data/schools/yale.json";
import columbiaData from "@/data/schools/columbia.json";
import mitData from "@/data/schools/mit.json";

const schools: SchoolData[] = [
  brownData as SchoolData,
  caltechData as SchoolData,
  columbiaData as SchoolData,
  cornellData as SchoolData,
  dartmouthData as SchoolData,
  harvardData as SchoolData,
  princetonData as SchoolData,
  stanfordData as SchoolData,
  uclaData as SchoolData,
  upennData as SchoolData,
  yaleData as SchoolData,
  mitData as SchoolData,
];

// Prepare search data
const searchableSchools = schools.map((school) => {
  const years = Object.keys(school.years).sort();
  const latestYear = years[years.length - 1];
  const latestData = school.years[latestYear];
  return {
    name: school.name,
    slug: school.slug,
    acceptanceRate: latestData.admissions.acceptanceRate,
  };
});

export default function HomePage() {
  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 px-4 text-center text-white">
        <h1 className="text-4xl md:text-5xl font-bold mb-3">
          College Statistics
        </h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto mb-8">
          Explore and compare Common Data Set metrics across top universities.
          View historical trends in admissions, test scores, costs, and more.
        </p>

        {/* Search Bar */}
        <SearchBar schools={searchableSchools} />
      </div>

      {/* School Grid */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">
          Featured Schools
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schools.map((school) => {
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
                      <div className="text-xs text-gray-500">
                        Acceptance Rate
                      </div>
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

        {schools.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No school data available yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
