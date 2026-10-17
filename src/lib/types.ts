import type { z } from "zod";
import type {
  admissionsFactorImportance,
  schoolDataSchema,
  yearDataSchema,
} from "@/lib/schoolSchema";

export type SchoolData = z.infer<typeof schoolDataSchema>;
export type SchoolProfile = NonNullable<SchoolData["profile"]>;
export type AdmissionsFactorImportance = z.infer<typeof admissionsFactorImportance>;
export type AdmissionsFactorsData = NonNullable<SchoolProfile["admissionsFactors"]>;
export type YearData = z.infer<typeof yearDataSchema>;
export type AdmissionsData = YearData["admissions"];
export type TestScoresData = YearData["testScores"];
export type DemographicsData = YearData["demographics"];
export type CostsData = YearData["costs"];
export type FinancialAidData = YearData["financialAid"];
