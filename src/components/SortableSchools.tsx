"use client";

import { useState, useRef, useEffect, type ReactNode } from "react";

export interface SchoolSortMetric {
  slug: string;
  name: string;
  acceptanceRate: number | null;
  classSize: number | null;
  satMid: number | null;
  totalCost: number | null;
  yieldRate: number | null;
  yearsOfData: number;
}

export interface SortableSchoolItem {
  slug: string;
  metric: SchoolSortMetric;
  card: ReactNode;
}

interface SortableSchoolsProps {
  items: SortableSchoolItem[];
}

type SortValue =
  | "acceptance"
  | "name"
  | "classSize"
  | "sat"
  | "cost"
  | "yield"
  | "years";

type Direction = "asc" | "desc";

// Each metric has a sensible default direction; the user can reverse it.
const SORT_OPTIONS: { value: SortValue; label: string; defaultDir: Direction }[] = [
  { value: "acceptance", label: "Acceptance rate", defaultDir: "asc" },
  { value: "name", label: "Name", defaultDir: "asc" },
  { value: "classSize", label: "Class size", defaultDir: "desc" },
  { value: "sat", label: "SAT midpoint", defaultDir: "desc" },
  { value: "cost", label: "Total cost", defaultDir: "desc" },
  { value: "yield", label: "Yield", defaultDir: "desc" },
  { value: "years", label: "Years of data", defaultDir: "desc" },
];

// The numeric field each metric sorts on. `name` is handled separately (string).
function numericField(
  metric: SchoolSortMetric,
  sort: SortValue
): number | null {
  switch (sort) {
    case "acceptance":
      return metric.acceptanceRate;
    case "classSize":
      return metric.classSize;
    case "sat":
      return metric.satMid;
    case "cost":
      return metric.totalCost;
    case "yield":
      return metric.yieldRate;
    case "years":
      return metric.yearsOfData;
    default:
      return null;
  }
}

// Numeric compare where a missing value (null) always sorts to the bottom,
// regardless of direction — "no data" should never read as "lowest".
function compareNumeric(
  a: number | null,
  b: number | null,
  dir: Direction
): number {
  if (a === null && b === null) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  return dir === "asc" ? a - b : b - a;
}

function sortItems(
  items: SortableSchoolItem[],
  sort: SortValue,
  dir: Direction
): SortableSchoolItem[] {
  const byNameAsc = (a: SortableSchoolItem, b: SortableSchoolItem) =>
    a.metric.name.localeCompare(b.metric.name);

  const sorted = [...items];
  sorted.sort((a, b) => {
    const primary =
      sort === "name"
        ? dir === "asc"
          ? byNameAsc(a, b)
          : -byNameAsc(a, b)
        : compareNumeric(
            numericField(a.metric, sort),
            numericField(b.metric, sort),
            dir
          );
    // Stable, predictable tie-breaker.
    return primary !== 0 ? primary : byNameAsc(a, b);
  });
  return sorted;
}

export default function SortableSchools({ items }: SortableSchoolsProps) {
  const [sort, setSort] = useState<SortValue>("acceptance");
  const [direction, setDirection] = useState<Direction>("asc");
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const sorted = sortItems(items, sort, direction);
  const activeLabel = SORT_OPTIONS.find((o) => o.value === sort)?.label;

  // Close the popover on outside click or Escape — same pattern as SaveSchoolButton.
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKey);
    };
  }, []);

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">
          All Schools ({items.length})
        </h2>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span className="font-medium">Sort by</span>
          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              aria-haspopup="listbox"
              aria-expanded={open}
              className="flex items-center justify-between gap-2 min-w-[15rem] rounded-lg border border-gray-300 bg-white pl-4 pr-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:border-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400"
            >
              <span>{activeLabel}</span>
              <svg
                className={`w-4 h-4 text-gray-500 transition-transform ${open ? "rotate-180" : ""}`}
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {open && (
              <div
                role="listbox"
                className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-100 p-1.5 z-50"
              >
                {SORT_OPTIONS.map((option) => {
                  const selected = option.value === sort;
                  return (
                    <button
                      key={option.value}
                      type="button"
                      role="option"
                      aria-selected={selected}
                      onClick={() => {
                        setSort(option.value);
                        setDirection(option.defaultDir);
                        setOpen(false);
                      }}
                      className={`w-full text-left px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-between ${
                        selected ? "bg-gray-100 text-gray-900" : "text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      <span>{option.label}</span>
                      {selected && (
                        <svg
                          className="w-3.5 h-3.5 text-blue-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setDirection((d) => (d === "asc" ? "desc" : "asc"))}
            title={`Reverse order (currently ${
              direction === "asc" ? "ascending" : "descending"
            })`}
            aria-label="Reverse sort order"
            className="flex items-center justify-center rounded-lg border border-gray-300 bg-white p-2 shadow-sm transition-colors hover:bg-gray-50 focus:border-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400"
          >
            <svg
              className={`w-4 h-4 text-gray-600 transition-transform ${
                direction === "asc" ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 5v14M19 12l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sorted.map((item) => (
          <div key={item.slug}>{item.card}</div>
        ))}
      </div>
    </>
  );
}
