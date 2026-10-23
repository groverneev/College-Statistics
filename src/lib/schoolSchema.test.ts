import { expect, test } from "bun:test";
import { schoolDataSchema } from "@/lib/schoolSchema";

const base = {
  name: "Example College",
  slug: "example",
  years: {
    "2024-2025": {
      admissions: { applied: 100, admitted: 10, acceptanceRate: 0.1 },
      testScores: {},
      demographics: { enrollment: {}, byRace: {} },
      costs: {},
      financialAid: {},
    },
  },
};

test("accepts a well-formed school", () => {
  expect(schoolDataSchema.safeParse(base).success).toBe(true);
});

test("rejects rates outside 0-1", () => {
  const bad = structuredClone(base);
  bad.years["2024-2025"].admissions.acceptanceRate = 10;
  expect(schoolDataSchema.safeParse(bad).success).toBe(false);
});

test("rejects unknown fields", () => {
  const bad = structuredClone(base);
  Object.assign(bad.years["2024-2025"].admissions, { acceptRate: 0.1 });
  expect(schoolDataSchema.safeParse(bad).success).toBe(false);
});

test("rejects malformed year keys", () => {
  const bad = { ...base, years: { "2024": base.years["2024-2025"] } };
  expect(schoolDataSchema.safeParse(bad).success).toBe(false);
});

test("preserves attribution for supplemental historical data", () => {
  const sources = [
    {
      kind: "ipeds" as const,
      label: "NCES IPEDS",
      url: "https://nces.ed.gov/ipeds/",
      years: ["2024-2025"],
      notes: "Fall enrollment and admissions.",
    },
  ];
  const result = schoolDataSchema.parse({ ...base, profile: { sources } });
  expect(result.profile?.sources).toEqual(sources);
});

test("rejects source attribution without valid years or URLs", () => {
  const source = { kind: "ipeds", label: "NCES IPEDS", url: "not a URL", years: ["2024"] };
  expect(schoolDataSchema.safeParse({ ...base, profile: { sources: [source] } }).success).toBe(
    false,
  );
  expect(
    schoolDataSchema.safeParse({
      ...base,
      profile: { sources: [{ ...source, url: "https://nces.ed.gov/ipeds/", years: [] }] },
    }).success,
  ).toBe(false);
});
