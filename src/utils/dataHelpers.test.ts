import { describe, expect, test } from "bun:test";
import type { SchoolData, YearData } from "@/lib/types";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  getLatestYear,
  getLatestYearData,
  getSchoolYearRange,
  getSortedYears,
} from "@/utils/dataHelpers";

const year = (applied: number): YearData => ({
  admissions: { applied },
  testScores: {},
  demographics: { enrollment: {}, byRace: {} },
  costs: {},
  financialAid: {},
});

const school: SchoolData = {
  name: "Example College",
  slug: "example",
  years: { "2023-2024": year(2), "2021-2022": year(1), "2024-2025": year(3) },
};

describe("year helpers", () => {
  test("sorts years and finds the latest", () => {
    expect(getSortedYears(school)).toEqual(["2021-2022", "2023-2024", "2024-2025"]);
    expect(getLatestYear(school)).toBe("2024-2025");
    expect(getLatestYearData(school)?.admissions.applied).toBe(3);
    expect(getSchoolYearRange(school)).toBe("2021-2025");
  });

  test("handles a school with no years", () => {
    const empty = { ...school, years: {} };
    expect(getLatestYear(empty)).toBeNull();
    expect(getLatestYearData(empty)).toBeNull();
    expect(getSchoolYearRange(empty)).toBeNull();
  });
});

describe("formatters", () => {
  test("format finite numbers", () => {
    expect(formatNumber(12345)).toBe("12,345");
    expect(formatPercent(0.0567)).toBe("5.7%");
    expect(formatCurrency(85000.4)).toBe("$85,000");
  });

  test("render missing values as a dash", () => {
    for (const value of [undefined, null, Number.NaN, Number.POSITIVE_INFINITY]) {
      expect(formatNumber(value)).toBe("—");
      expect(formatPercent(value)).toBe("—");
      expect(formatCurrency(value)).toBe("—");
    }
  });
});
