import Link from "next/link";
import SaveSchoolButton from "@/components/SaveSchoolButton";
import type { SchoolCardData } from "@/data/schools";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";

interface SchoolCardProps {
  school: SchoolCardData;
  showSaveButton?: boolean;
}

export default function SchoolCard({ school, showSaveButton = false }: SchoolCardProps) {
  const { color } = school;

  return (
    <div className="relative">
      {showSaveButton && (
        <div className="absolute top-3 right-3 z-10">
          <SaveSchoolButton schoolSlug={school.slug} schoolName={school.name} variant="icon" />
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
            {school.yearCount} years of data ({school.yearRange})
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-gray-800">
                {formatPercent(school.acceptanceRate)}
              </div>
              <div className="text-xs text-gray-500">Acceptance Rate</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-800">
                {formatNumber(school.enrolled)}
              </div>
              <div className="text-xs text-gray-500">Class Size</div>
            </div>
            {school.satP25 !== null && school.satP75 !== null && (
              <div>
                <div className="text-lg font-semibold text-gray-700">
                  {school.satP25}-{school.satP75}
                </div>
                <div className="text-xs text-gray-500">SAT Range</div>
              </div>
            )}
            <div>
              <div className="text-lg font-semibold text-gray-700">
                {school.totalCOA !== null ? `$${(school.totalCOA / 1000).toFixed(0)}k` : "-"}
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
}
