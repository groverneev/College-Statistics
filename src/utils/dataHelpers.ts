import { SchoolData, YearData } from "@/lib/types";

export function getSortedYears(school: SchoolData): string[] {
  return Object.keys(school.years).sort();
}

export function getLatestYear(school: SchoolData): string | null {
  const years = getSortedYears(school);
  return years.length > 0 ? years[years.length - 1] : null;
}

export function getLatestYearData(school: SchoolData): YearData | null {
  const latestYear = getLatestYear(school);
  return latestYear ? school.years[latestYear] ?? null : null;
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

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

export function formatPercent(num: number): string {
  return `${(num * 100).toFixed(1)}%`;
}

export function formatCurrency(num: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(num);
}
