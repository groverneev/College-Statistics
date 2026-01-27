"use client";

import { useSearchParams } from "next/navigation";
import { useState, useEffect, Suspense } from "react";
import { SchoolData, SCHOOL_COLORS, YearData } from "@/lib/types";
import { getLatestYear, formatNumber, formatPercent, formatCurrency } from "@/utils/dataHelpers";
import { YearSelector } from "@/components";

// Import school data
import brownData from "@/data/schools/brown.json";
import caltechData from "@/data/schools/caltech.json";
import dartmouthData from "@/data/schools/dartmouth.json";
import harvardData from "@/data/schools/harvard.json";
import princetonData from "@/data/schools/princeton.json";
import stanfordData from "@/data/schools/stanford.json";
import upennData from "@/data/schools/upenn.json";
import yaleData from "@/data/schools/yale.json";

const schoolDataMap: Record<string, SchoolData> = {
  brown: brownData as SchoolData,
  caltech: caltechData as SchoolData,
  dartmouth: dartmouthData as SchoolData,
  harvard: harvardData as SchoolData,
  princeton: princetonData as SchoolData,
  stanford: stanfordData as SchoolData,
  upenn: upennData as SchoolData,
  yale: yaleData as SchoolData,
};

function CompareContent() {
  const searchParams = useSearchParams();
  const schoolsParam = searchParams.get("schools");

  const [selectedYear, setSelectedYear] = useState<string>("");

  const schoolSlugs = schoolsParam?.split(",").filter(Boolean) || [];
  const schools = schoolSlugs
    .map((slug) => schoolDataMap[slug.toLowerCase()])
    .filter(Boolean);

  // Get common years across all schools
  const commonYears = schools.length > 0
    ? Object.keys(schools[0].years).filter((year) =>
        schools.every((s) => s.years[year])
      )
    : [];

  useEffect(() => {
    if (commonYears.length > 0 && !selectedYear) {
      setSelectedYear(commonYears.sort().reverse()[0]);
    }
  }, [commonYears, selectedYear]);

  if (schools.length === 0) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Compare Schools
        </h1>
        <p className="text-gray-500 mb-6">
          Select schools to compare from the dropdown below.
        </p>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <p className="text-center text-gray-500">
            Use the school pages to start a comparison, or add schools to the URL:
            <br />
            <code className="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded mt-2 inline-block">
              /compare?schools=brown,harvard
            </code>
          </p>
        </div>
      </div>
    );
  }

  const yearData: Record<string, YearData> = {};
  schools.forEach((school) => {
    if (selectedYear && school.years[selectedYear]) {
      yearData[school.slug] = school.years[selectedYear];
    }
  });

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
            Compare Schools
          </h1>
          <p className="text-gray-500">
            {schools.map((s) => s.name).join(" vs ")}
          </p>
        </div>
        {commonYears.length > 0 && (
          <YearSelector
            years={commonYears}
            selectedYear={selectedYear}
            onChange={setSelectedYear}
          />
        )}
      </div>

      {/* Comparison Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Metric
              </th>
              {schools.map((school) => (
                <th
                  key={school.slug}
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                  style={{ color: SCHOOL_COLORS[school.slug] }}
                >
                  {school.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {/* Admissions Section */}
            <tr className="bg-gray-50 dark:bg-gray-700">
              <td colSpan={schools.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Admissions
              </td>
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Applications</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatNumber(yearData[school.slug].admissions.applied) : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Acceptance Rate</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatPercent(yearData[school.slug].admissions.acceptanceRate) : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Class Size</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatNumber(yearData[school.slug].admissions.enrolled) : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Yield</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatPercent(yearData[school.slug].admissions.yield) : "-"}
                </td>
              ))}
            </tr>

            {/* Test Scores Section */}
            <tr className="bg-gray-50 dark:bg-gray-700">
              <td colSpan={schools.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Test Scores
              </td>
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">SAT Range (25-75%)</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug]?.testScores.sat
                    ? `${yearData[school.slug].testScores.sat!.composite.p25}-${yearData[school.slug].testScores.sat!.composite.p75}`
                    : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">ACT Range (25-75%)</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug]?.testScores.act
                    ? `${yearData[school.slug].testScores.act!.composite.p25}-${yearData[school.slug].testScores.act!.composite.p75}`
                    : "-"}
                </td>
              ))}
            </tr>

            {/* Costs Section */}
            <tr className="bg-gray-50 dark:bg-gray-700">
              <td colSpan={schools.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Costs
              </td>
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Tuition</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatCurrency(yearData[school.slug].costs.tuition) : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Total COA</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatCurrency(yearData[school.slug].costs.totalCOA) : "-"}
                </td>
              ))}
            </tr>

            {/* Financial Aid Section */}
            <tr className="bg-gray-50 dark:bg-gray-700">
              <td colSpan={schools.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Financial Aid
              </td>
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">% Receiving Aid</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatPercent(yearData[school.slug].financialAid.percentReceivingAid) : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Avg Aid Package</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatCurrency(yearData[school.slug].financialAid.averageAidPackage) : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">% Need Fully Met</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatPercent(yearData[school.slug].financialAid.percentNeedFullyMet) : "-"}
                </td>
              ))}
            </tr>

            {/* Demographics Section */}
            <tr className="bg-gray-50 dark:bg-gray-700">
              <td colSpan={schools.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                Demographics
              </td>
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-gray-600 dark:text-gray-300">Undergrad Enrollment</td>
              {schools.map((school) => (
                <td key={school.slug} className="px-6 py-3 text-sm font-medium">
                  {yearData[school.slug] ? formatNumber(yearData[school.slug].demographics.enrollment.undergraduate) : "-"}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CompareContent />
    </Suspense>
  );
}
