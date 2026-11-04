import { describe, expect, test } from "bun:test";
import { EMPTY_FILTERS, type Filters, matchesFilters } from "@/components/SortableSchools";
import type { SchoolCardData } from "@/data/schools";

const school: SchoolCardData = {
  slug: "example",
  name: "Example University",
  color: "#000000",
  yearCount: 5,
  yearRange: "2020-2025",
  acceptanceRate: 0.12,
  enrolled: 2500,
  yieldRate: 0.5,
  satP25: 1400,
  satP50: 1480,
  satP75: 1550,
  totalCOA: 88_000,
  state: "MA",
  control: "private",
};

const withFilters = (overrides: Partial<Filters>): Filters => ({ ...EMPTY_FILTERS, ...overrides });

describe("matchesFilters", () => {
  test("no filters matches everything", () => {
    expect(matchesFilters(school, EMPTY_FILTERS)).toBe(true);
  });

  test("control and region", () => {
    expect(matchesFilters(school, withFilters({ control: ["private"] }))).toBe(true);
    expect(matchesFilters(school, withFilters({ control: ["public"] }))).toBe(false);
    expect(matchesFilters(school, withFilters({ region: ["northeast"] }))).toBe(true);
    expect(matchesFilters(school, withFilters({ region: ["west", "south"] }))).toBe(false);
  });

  test("range buckets are lower-inclusive and OR'd within a group", () => {
    expect(matchesFilters(school, withFilters({ acceptance: ["10-25"] }))).toBe(true);
    expect(matchesFilters(school, withFilters({ acceptance: ["lt10"] }))).toBe(false);
    expect(matchesFilters(school, withFilters({ acceptance: ["lt10", "10-25"] }))).toBe(true);
    expect(matchesFilters(school, withFilters({ cost: ["60-95k"] }))).toBe(true);
    expect(matchesFilters({ ...school, totalCOA: 95_000 }, withFilters({ cost: ["gt95k"] }))).toBe(
      true,
    );
  });

  test("groups are AND'd and missing values never match a range", () => {
    expect(matchesFilters(school, withFilters({ control: ["private"], size: ["gt6k"] }))).toBe(
      false,
    );
    expect(matchesFilters({ ...school, totalCOA: null }, withFilters({ cost: ["lt30k"] }))).toBe(
      false,
    );
  });
});
