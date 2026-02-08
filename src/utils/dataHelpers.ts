import { SchoolData, YearData } from "@/lib/types";

export function getLatestYear(school: SchoolData): string | null {
  const years = Object.keys(school.years).sort().reverse();
  return years.length > 0 ? years[0] : null;
}

export function getYearData(
  school: SchoolData,
  year: string
): YearData | null {
  return school.years[year] || null;
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

export function getAvailableSchools(): string[] {
  // This will be populated dynamically based on available JSON files
  return ["brown", "harvard", "yale", "princeton", "cornell", "dartmouth", "upenn", "stanford", "caltech", "ucla", "columbia"];
}

export function calculateAcceptanceRate(admitted: number, applied: number): number {
  return applied > 0 ? admitted / applied : 0;
}

export function calculateYield(enrolled: number, admitted: number): number {
  return admitted > 0 ? enrolled / admitted : 0;
}
