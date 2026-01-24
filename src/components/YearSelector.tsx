"use client";

interface YearSelectorProps {
  years: string[];
  selectedYear: string;
  onChange: (year: string) => void;
}

export default function YearSelector({
  years,
  selectedYear,
  onChange,
}: YearSelectorProps) {
  const sortedYears = [...years].sort().reverse();

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="year-select" className="text-sm text-gray-600 dark:text-gray-300">
        Academic Year:
      </label>
      <select
        id="year-select"
        value={selectedYear}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {sortedYears.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>
    </div>
  );
}
