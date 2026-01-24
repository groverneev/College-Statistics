import Link from "next/link";
import { SchoolData, SCHOOL_COLORS } from "@/lib/types";
import { getLatestYear, formatNumber, formatPercent } from "@/utils/dataHelpers";

interface SchoolCardProps {
  school: SchoolData;
}

export default function SchoolCard({ school }: SchoolCardProps) {
  const latestYear = getLatestYear(school);
  const data = latestYear ? school.years[latestYear] : null;
  const color = SCHOOL_COLORS[school.slug] || "#4B5563";

  return (
    <Link href={`/${school.slug}`}>
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border-l-4"
        style={{ borderLeftColor: color }}
      >
        <h2 className="text-xl font-semibold mb-1" style={{ color }}>
          {school.name}
        </h2>
        <p className="text-sm text-gray-500 mb-4">{latestYear}</p>

        {data && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold">
                {formatPercent(data.admissions.acceptanceRate)}
              </div>
              <div className="text-xs text-gray-500">Acceptance Rate</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {formatNumber(data.admissions.enrolled)}
              </div>
              <div className="text-xs text-gray-500">Class Size</div>
            </div>
            {data.testScores.sat && (
              <div>
                <div className="text-lg font-semibold">
                  {data.testScores.sat.composite.p25}-{data.testScores.sat.composite.p75}
                </div>
                <div className="text-xs text-gray-500">SAT Range</div>
              </div>
            )}
            <div>
              <div className="text-lg font-semibold">
                ${(data.costs.totalCOA / 1000).toFixed(0)}k
              </div>
              <div className="text-xs text-gray-500">Total Cost</div>
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
