import { ucDataByYear, availableUCYears } from "@/data/uc/index";
import UCPageClient from "./UCPageClient";

export const metadata = {
  title: "UC Campus Explorer – College Statistics",
  description:
    "Explore UC admissions data by campus and discipline. Compare admit rates, GPA ranges, and yield across all 9 UC campuses for Fall 2025.",
};

export default function UCPage() {
  return (
    <UCPageClient
      dataByYear={ucDataByYear}
      availableYears={availableUCYears}
    />
  );
}
