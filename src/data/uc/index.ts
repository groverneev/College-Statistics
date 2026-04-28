import { UCYearData } from "./types";
import { uc2025 } from "./2025";

export * from "./types";

// Year-keyed map — add future years here
export const ucDataByYear: Record<number, UCYearData> = {
  2025: uc2025,
};

export const availableUCYears = Object.keys(ucDataByYear)
  .map(Number)
  .sort((a, b) => b - a);

export const latestUCYear = availableUCYears[0];
