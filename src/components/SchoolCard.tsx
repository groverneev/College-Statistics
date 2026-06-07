import Link from "next/link";
import { getSchoolColor } from "@/data/schools";
import SaveSchoolButton from "@/components/SaveSchoolButton";
import CardNoteIndicator from "@/components/CardNoteIndicator";
import { SchoolData } from "@/lib/types";
import {
  formatNumber,
  formatPercent,
  getLatestYear,
  getLatestYearData,
  getSchoolYearRange,
  getSortedYears,
} from "@/utils/dataHelpers";

interface SchoolCardProps {
  school: SchoolData;
  showSaveButton?: boolean;
}

export default function SchoolCard({
  school,
  showSaveButton = false,
}: SchoolCardProps) {
  const years = getSortedYears(school);
  const latestYear = getLatestYear(school);
  const latestData = getLatestYearData(school);
  const yearRange = getSchoolYearRange(school);
  const color = getSchoolColor(school.slug);

  if (!latestYear || !latestData || !yearRange) {
    return null;
  }

  return (
    <div className="relative">
      {showSaveButton && (
        <div className="absolute top-3 right-3 z-10">
          <SaveSchoolButton
            schoolSlug={school.slug}
            schoolName={school.name}
            variant="icon"
          />
        </div>
      )}

      <Link href={`/${school.slug}`}>
        <div
          className="card p-6 hover:shadow-lg transition-shadow cursor-pointer border-t-4"
          style={{ borderTopColor: color }}
        >
          <h3
            className={`text-xl font-semibold mb-1 ${showSaveButton ? "pr-8" : ""}`}
            style={{ color }}
          >
            {school.name}
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            {years.length} years of data ({yearRange})
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

          <CardNoteIndicator schoolSlug={school.slug} />

          <div className="mt-4 pt-4 border-t border-gray-100">
            <span className="text-sm font-medium" style={{ color }}>
              View Dashboard &rarr;
            </span>
          </div>
        </div>
      </Link>
    </div>
  );
}
