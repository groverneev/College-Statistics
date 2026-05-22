import { UCYearData } from "./types";
import { uc2025 } from "./2025";
import { uc2024 } from "./2024";

export * from "./types";

// Year-keyed map — add future years here
export const ucDataByYear: Record<number, UCYearData> = {
  2025: uc2025,
  2024: uc2024,
};

export const availableUCYears = Object.keys(ucDataByYear)
  .map(Number)
  .sort((a, b) => b - a);

export const latestUCYear = availableUCYears[0];
