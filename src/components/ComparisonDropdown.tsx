"use client";

import { useRouter } from "next/navigation";
import { SCHOOL_COLORS } from "@/lib/types";

interface ComparisonDropdownProps {
  currentSchool: string;
  availableSchools: string[];
}

export default function ComparisonDropdown({
  currentSchool,
  availableSchools,
}: ComparisonDropdownProps) {
  const router = useRouter();

  const otherSchools = availableSchools.filter(
    (s) => s.toLowerCase() !== currentSchool.toLowerCase()
  );

  const handleCompare = (school: string) => {
    if (school) {
      router.push(`/compare?schools=${currentSchool.toLowerCase()},${school.toLowerCase()}`);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="compare-select" className="text-sm text-gray-600 dark:text-gray-300">
        Compare with:
      </label>
      <select
        id="compare-select"
        defaultValue=""
        onChange={(e) => handleCompare(e.target.value)}
        className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="" disabled>
          Select a school...
        </option>
        {otherSchools.map((school) => (
          <option key={school} value={school}>
            {school.charAt(0).toUpperCase() + school.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
}
