import { describe, expect, test } from "bun:test";
import { allSchools, SCHOOL_METADATA, schoolCards } from "@/data/schools";

describe("school metadata", () => {
  test("every school has a metadata entry with state and control", () => {
    for (const school of allSchools) {
      const metadata = SCHOOL_METADATA[school.slug];
      expect(metadata, school.slug).toBeDefined();
      expect(metadata.state, school.slug).toMatch(/^[A-Z]{2}$/);
      expect(["public", "private"], school.slug).toContain(metadata.control);
    }
  });

  test("every school produces a card summary", () => {
    expect(schoolCards.length).toBe(allSchools.length);
  });
});
