"use client";

import Link from "next/link";
import { SchoolData } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import {
  AdmissionsTrendChart,
  TestScoresTrendChart,
  CostsTrendChart,
  FinancialAidTrendChart,
  DemographicsTrendChart,
} from "@/components/charts";

interface SchoolPageClientProps {
  schoolData: SchoolData;
  schoolColor: string;
  availableSchools: string[];
}

export default function SchoolPageClient({
  schoolData,
  schoolColor,
}: SchoolPageClientProps) {
  const years = Object.keys(schoolData.years).sort();
  const latestYear = years[years.length - 1];
  const latestData = schoolData.years[latestYear];
  const yearRange = `${years[0].split("-")[0]}-${years[years.length - 1].split("-")[1]}`;

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Header Banner */}
      <div
        className="py-10 px-4 text-center text-white"
        style={{
          background: `linear-gradient(135deg, ${schoolColor} 0%, ${schoolColor}dd 100%)`,
        }}
      >
        <Link
          href="/"
          className="inline-flex items-center text-white/80 hover:text-white text-sm mb-4 transition-colors"
        >
          <svg
            className="w-4 h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Schools
        </Link>
        <h1 className="text-3xl md:text-4xl font-bold mb-2">
          {schoolData.name}
        </h1>
        <p className="text-white/80 text-sm md:text-base">
          Admissions Data Dashboard | Common Data Set {yearRange}
        </p>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8 -mt-4">
        {/* Key Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="stat-card">
            <div className="label">Total Applications</div>
            <div className="value">{formatNumber(latestData.admissions.applied)}</div>
            <div className="subtext">{latestYear}</div>
          </div>
          <div className="stat-card">
            <div className="label">Acceptance Rate</div>
            <div className="value">{formatPercent(latestData.admissions.acceptanceRate)}</div>
            <div className="subtext">{latestYear}</div>
          </div>
          <div className="stat-card">
            <div className="label">Enrolled Students</div>
            <div className="value">{formatNumber(latestData.admissions.enrolled)}</div>
            <div className="subtext">{latestYear}</div>
          </div>
          <div className="stat-card">
            <div className="label">SAT Middle 50%</div>
            <div className="value">
              {latestData.testScores.sat
                ? `${latestData.testScores.sat.composite.p25}-${latestData.testScores.sat.composite.p75}`
                : "N/A"}
            </div>
            <div className="subtext">{latestYear}</div>
          </div>
        </div>

        {/* Charts */}
        <div className="space-y-6">
          <AdmissionsTrendChart
            yearData={schoolData.years}
            schoolColor={schoolColor}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TestScoresTrendChart
              yearData={schoolData.years}
              schoolColor={schoolColor}
            />
            <FinancialAidTrendChart
              yearData={schoolData.years}
              schoolColor={schoolColor}
            />
          </div>

          <CostsTrendChart
            yearData={schoolData.years}
            schoolColor={schoolColor}
          />

          <DemographicsTrendChart
            yearData={schoolData.years}
            schoolColor={schoolColor}
          />
        </div>
      </div>
    </div>
  );
}
