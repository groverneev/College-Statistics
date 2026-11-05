import type { SchoolData, YearData } from "@/lib/types";

export function getSortedYears(school: SchoolData): string[] {
  return Object.keys(school.years).sort();
}

export function getLatestYear(school: SchoolData): string | null {
  const years = getSortedYears(school);
  return years.length > 0 ? years[years.length - 1] : null;
}

export function getLatestYearData(school: SchoolData): YearData | null {
  const latestYear = getLatestYear(school);
  return latestYear ? (school.years[latestYear] ?? null) : null;
}

export function getSchoolYearRange(school: SchoolData): string | null {
  const years = getSortedYears(school);
  if (years.length === 0) {
    return null;
  }

  const firstYear = years[0];
  const latestYear = years[years.length - 1];
  return `${firstYear.split("-")[0]}-${latestYear.split("-")[1]}`;
}

/**
 * Newest year whose data yields a value, so a figure the latest form left blank falls back
 * to the most recent year that reported it instead of rendering an empty placeholder.
 */
export function latestReported<T>(
  yearData: Record<string, YearData>,
  pick: (data: YearData) => T | null | undefined,
): { year: string; value: T } | null {
  const years = Object.keys(yearData).sort().reverse();
  for (const year of years) {
    const value = pick(yearData[year]);
    if (
      value !== null &&
      value !== undefined &&
      !(typeof value === "number" && !Number.isFinite(value))
    ) {
      return { year, value };
    }
  }
  return null;
}

export function formatNumber(num: number | null | undefined): string {
  if (typeof num !== "number" || !Number.isFinite(num)) return "-";
  return new Intl.NumberFormat("en-US").format(num);
}

export function formatPercent(num: number | null | undefined): string {
  if (typeof num !== "number" || !Number.isFinite(num)) return "-";
  return `${(num * 100).toFixed(1)}%`;
}

export function formatCurrency(num: number | null | undefined): string {
  if (typeof num !== "number" || !Number.isFinite(num)) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(num);
}
