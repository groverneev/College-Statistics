import Link from "next/link";
import { SchoolData, SCHOOL_COLORS } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import SearchBar from "@/components/SearchBar";
import SaveSchoolButton from "@/components/SaveSchoolButton";
import { allSchools, searchableSchools } from "@/data/schools";

export default function BrowseSchoolsPage() {
  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-12 px-4 text-center text-white">
        <h1 className="text-3xl md:text-4xl font-bold mb-3">Browse Schools</h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto mb-6">
          Explore Common Data Set metrics across top universities.
        </p>
        <SearchBar schools={searchableSchools} />
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">
          All Schools ({allSchools.length})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allSchools.map((school: SchoolData) => {
            const years = Object.keys(school.years).sort();
            const latestYear = years[years.length - 1];
            const latestData = school.years[latestYear];
            const color = SCHOOL_COLORS[school.slug] || "#4B5563";

            return (
              <div key={school.slug} className="relative">
                {/* Save button */}
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
                    style={{ borderTopColor: color }}
                  >
                    <h3
                      className="text-xl font-semibold mb-1 pr-8"
                      style={{ color }}
                    >
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
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
