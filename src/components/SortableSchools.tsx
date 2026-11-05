"use client";

import { useEffect, useRef, useState } from "react";
import SchoolCard from "@/components/SchoolCard";
import type { SchoolCardData } from "@/data/schools";

interface SortableSchoolsProps {
  schools: SchoolCardData[];
}

type SortValue = "acceptance" | "name" | "classSize" | "sat" | "cost" | "yield";

type Direction = "asc" | "desc";

const SORT_OPTIONS: {
  value: SortValue;
  label: string;
  defaultDir: Direction;
}[] = [
  { value: "acceptance", label: "Acceptance rate", defaultDir: "asc" },
  { value: "name", label: "Name", defaultDir: "asc" },
  { value: "classSize", label: "Class size", defaultDir: "desc" },
  { value: "sat", label: "SAT midpoint", defaultDir: "desc" },
  { value: "cost", label: "Total cost", defaultDir: "desc" },
  { value: "yield", label: "Yield", defaultDir: "desc" },
];

type Region = "northeast" | "south" | "midwest" | "west";

const REGION_STATES: Record<Region, string[]> = {
  northeast: ["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"],
  south: [
    "DE",
    "DC",
    "FL",
    "GA",
    "MD",
    "NC",
    "SC",
    "VA",
    "WV",
    "AL",
    "KY",
    "MS",
    "TN",
    "AR",
    "LA",
    "OK",
    "TX",
  ],
  midwest: [
    "IL",
    "IN",
    "MI",
    "OH",
    "WI",
    "IA",
    "KS",
    "MN",
    "MO",
    "NE",
    "ND",
    "SD",
  ],
  west: [
    "AZ",
    "CO",
    "ID",
    "MT",
    "NV",
    "NM",
    "UT",
    "WY",
    "AK",
    "CA",
    "HI",
    "OR",
    "WA",
  ],
};

interface RangeOption {
  value: string;
  label: string;
  min?: number;
  max?: number;
}

interface FilterGroup {
  key: "control" | "region" | "acceptance" | "size" | "cost";
  label: string;
  options: RangeOption[];
}

const FILTER_GROUPS: FilterGroup[] = [
  {
    key: "control",
    label: "Type",
    options: [
      { value: "public", label: "Public" },
      { value: "private", label: "Private" },
    ],
  },
  {
    key: "region",
    label: "Region",
    options: [
      { value: "northeast", label: "Northeast" },
      { value: "south", label: "South" },
      { value: "midwest", label: "Midwest" },
      { value: "west", label: "West" },
    ],
  },
  {
    key: "acceptance",
    label: "Acceptance rate",
    options: [
      { value: "lt10", label: "Under 10%", max: 0.1 },
      { value: "10-25", label: "10–25%", min: 0.1, max: 0.25 },
      { value: "25-50", label: "25–50%", min: 0.25, max: 0.5 },
      { value: "gt50", label: "Over 50%", min: 0.5 },
    ],
  },
  {
    key: "size",
    label: "Class size",
    options: [
      { value: "lt1k", label: "Under 1,000", max: 1000 },
      { value: "1k-3k", label: "1,000–3,000", min: 1000, max: 3000 },
      { value: "3k-6k", label: "3,000–6,000", min: 3000, max: 6000 },
      { value: "gt6k", label: "6,000+", min: 6000 },
    ],
  },
  {
    key: "cost",
    label: "Total cost",
    options: [
      { value: "lt30k", label: "Under $30k", max: 30_000 },
      { value: "30-60k", label: "$30k–$60k", min: 30_000, max: 60_000 },
      { value: "60-95k", label: "$60k–$95k", min: 60_000, max: 95_000 },
      { value: "gt95k", label: "$95k+", min: 95_000 },
    ],
  },
];

type FilterKey = FilterGroup["key"];
export type Filters = Record<FilterKey, string[]>;

export const EMPTY_FILTERS: Filters = {
  control: [],
  region: [],
  acceptance: [],
  size: [],
  cost: [],
};

function numericField(school: SchoolCardData, sort: SortValue): number | null {
  switch (sort) {
    case "acceptance":
      return school.acceptanceRate;
    case "classSize":
      return school.enrolled;
    case "sat":
      return school.satP50;
    case "cost":
      return school.totalCOA;
    case "yield":
      return school.yieldRate;
    default:
      return null;
  }
}

function compareNumeric(
  a: number | null,
  b: number | null,
  dir: Direction,
): number {
  if (a === null && b === null) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  return dir === "asc" ? a - b : b - a;
}

function sortSchools(
  schools: SchoolCardData[],
  sort: SortValue,
  dir: Direction,
) {
  const byNameAsc = (a: SchoolCardData, b: SchoolCardData) =>
    a.name.localeCompare(b.name);

  return [...schools].sort((a, b) => {
    const primary =
      sort === "name"
        ? dir === "asc"
          ? byNameAsc(a, b)
          : -byNameAsc(a, b)
        : compareNumeric(numericField(a, sort), numericField(b, sort), dir);
    return primary !== 0 ? primary : byNameAsc(a, b);
  });
}

function inRange(value: number | null, option: RangeOption): boolean {
  if (value === null) return false;
  if (option.min !== undefined && value < option.min) return false;
  if (option.max !== undefined && value >= option.max) return false;
  return true;
}

function groupValue(school: SchoolCardData, key: FilterKey): number | null {
  if (key === "acceptance") return school.acceptanceRate;
  if (key === "size") return school.enrolled;
  if (key === "cost") return school.totalCOA;
  return null;
}

// Options within a group are OR'd together; groups are AND'd.
export function matchesFilters(
  school: SchoolCardData,
  filters: Filters,
): boolean {
  return FILTER_GROUPS.every(({ key, options }) => {
    const selected = filters[key];
    if (selected.length === 0) return true;
    if (key === "control") return selected.includes(school.control);
    if (key === "region") {
      return selected.some((region) =>
        REGION_STATES[region as Region]?.includes(school.state),
      );
    }
    return options
      .filter((option) => selected.includes(option.value))
      .some((option) => inRange(groupValue(school, key), option));
  });
}

function readFiltersFromUrl(): Filters {
  const params = new URLSearchParams(window.location.search);
  const filters: Filters = { ...EMPTY_FILTERS };
  for (const { key, options } of FILTER_GROUPS) {
    const allowed = new Set(options.map((option) => option.value));
    filters[key] = (params.get(key)?.split(",") ?? []).filter((value) =>
      allowed.has(value),
    );
  }
  return filters;
}

function writeFiltersToUrl(filters: Filters) {
  const params = new URLSearchParams(window.location.search);
  for (const { key } of FILTER_GROUPS) {
    if (filters[key].length > 0) params.set(key, filters[key].join(","));
    else params.delete(key);
  }
  const query = params.toString();
  window.history.replaceState(
    null,
    "",
    `${window.location.pathname}${query ? `?${query}` : ""}`,
  );
}

export default function SortableSchools({ schools }: SortableSchoolsProps) {
  const [sort, setSort] = useState<SortValue>("acceptance");
  const [direction, setDirection] = useState<Direction>("asc");
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [open, setOpen] = useState(false);
  const [openFilter, setOpenFilter] = useState<FilterKey | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const activeLabel = SORT_OPTIONS.find((o) => o.value === sort)?.label;
  const activeFilterCount = Object.values(filters).reduce(
    (n, values) => n + values.length,
    0,
  );
  const visible = sortSchools(
    schools.filter((school) => matchesFilters(school, filters)),
    sort,
    direction,
  );

  useEffect(() => {
    setFilters(readFiltersFromUrl());
  }, []);

  function updateFilters(next: Filters) {
    setFilters(next);
    writeFiltersToUrl(next);
  }

  function toggleFilter(key: FilterKey, value: string) {
    const current = filters[key];
    updateFilters({
      ...filters,
      [key]: current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value],
    });
  }

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
      if (!(e.target as Element).closest?.("[data-filter-dropdown]")) {
        setOpenFilter(null);
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setOpen(false);
        setOpenFilter(null);
      }
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
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">
        {activeFilterCount > 0
          ? `${visible.length} of ${schools.length} schools`
          : `All Schools (${schools.length})`}
      </h2>

      <div className="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center text-sm text-gray-600">
          <span className="col-span-2 sm:col-span-1 font-medium sm:mr-1">
            Filter
          </span>
          {FILTER_GROUPS.map((group, index) => (
            <FilterDropdown
              key={group.key}
              group={group}
              selected={filters[group.key]}
              open={openFilter === group.key}
              alignRightOnMobile={index % 2 === 1}
              onToggleOpen={() =>
                setOpenFilter((k) => (k === group.key ? null : group.key))
              }
              onToggleValue={(value) => toggleFilter(group.key, value)}
              onClear={() => updateFilters({ ...filters, [group.key]: [] })}
            />
          ))}
          {activeFilterCount > 0 && (
            <button
              type="button"
              onClick={() => updateFilters(EMPTY_FILTERS)}
              className="min-h-11 px-2 text-sm font-medium text-blue-600 hover:text-blue-700 text-left"
            >
              Clear all
            </button>
          )}
        </div>

        <div className="grid grid-cols-[minmax(0,1fr)_auto] sm:flex sm:items-center gap-2 w-full sm:w-auto flex-shrink-0 text-sm text-gray-600">
          <span className="col-span-2 sm:col-span-1 font-medium">Sort by</span>
          <div className="relative min-w-0" ref={menuRef}>
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              aria-haspopup="listbox"
              aria-expanded={open}
              className="flex min-h-11 w-full sm:w-auto items-center justify-between gap-2 sm:min-w-[12rem] rounded-lg border border-gray-300 bg-white pl-4 pr-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:border-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400"
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
                className="absolute left-0 sm:left-auto sm:right-0 mt-2 w-full sm:w-64 bg-white rounded-xl shadow-lg border border-gray-100 p-1.5 z-50"
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
                      className={`w-full min-h-11 text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-between ${
                        selected
                          ? "bg-gray-100 text-gray-900"
                          : "text-gray-700 hover:bg-gray-50"
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
            title={`Reverse order (currently ${direction === "asc" ? "ascending" : "descending"})`}
            aria-label="Reverse sort order"
            className="flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-gray-300 bg-white p-2 shadow-sm transition-colors hover:bg-gray-50 focus:border-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400"
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

      {visible.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {visible.map((school) => (
            <SchoolCard key={school.slug} school={school} showSaveButton />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-gray-200">
          <p className="text-gray-600 mb-4">No schools match these filters.</p>
          <button
            type="button"
            onClick={() => updateFilters(EMPTY_FILTERS)}
            className="inline-flex min-h-11 items-center px-5 py-2.5 bg-gray-800 text-white rounded-lg font-medium text-sm hover:bg-gray-700 transition-colors"
          >
            Clear filters
          </button>
        </div>
      )}
    </>
  );
}

interface FilterDropdownProps {
  group: FilterGroup;
  selected: string[];
  open: boolean;
  alignRightOnMobile: boolean;
  onToggleOpen: () => void;
  onToggleValue: (value: string) => void;
  onClear: () => void;
}

function FilterDropdown({
  group,
  selected,
  open,
  alignRightOnMobile,
  onToggleOpen,
  onToggleValue,
  onClear,
}: FilterDropdownProps) {
  const active = selected.length > 0;
  const summary =
    selected.length === 1
      ? group.options.find((o) => o.value === selected[0])?.label
      : null;

  return (
    <div className="relative min-w-0" data-filter-dropdown>
      <button
        type="button"
        onClick={onToggleOpen}
        aria-haspopup="true"
        aria-expanded={open}
        className={`flex min-h-11 w-full sm:w-auto items-center justify-between gap-2 rounded-lg border bg-white pl-4 pr-3 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-gray-400 ${
          active
            ? "border-gray-800 text-gray-900"
            : "border-gray-300 text-gray-700"
        }`}
      >
        <span className="truncate">
          {group.label}
          {summary && (
            <span className="text-gray-500 font-normal">: {summary}</span>
          )}
        </span>
        <span className="flex items-center gap-1.5 flex-shrink-0">
          {selected.length > 1 && (
            <span className="rounded-full bg-gray-800 px-1.5 text-xs leading-5 text-white">
              {selected.length}
            </span>
          )}
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
        </span>
      </button>

      {open && (
        <div
          role="group"
          aria-label={group.label}
          className={`absolute ${
            alignRightOnMobile ? "right-0" : "left-0"
          } sm:left-0 sm:right-auto mt-2 w-full min-w-[11rem] sm:w-56 bg-white rounded-xl shadow-lg border border-gray-100 p-1.5 z-50`}
        >
          {group.options.map((option) => {
            const checked = selected.includes(option.value);
            return (
              <button
                key={option.value}
                type="button"
                role="menuitemcheckbox"
                aria-checked={checked}
                onClick={() => onToggleValue(option.value)}
                className={`w-full min-h-11 text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-between ${
                  checked
                    ? "bg-gray-100 text-gray-900"
                    : "text-gray-700 hover:bg-gray-50"
                }`}
              >
                <span>{option.label}</span>
                {checked && (
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
          {selected.length > 0 && (
            <button
              type="button"
              onClick={onClear}
              className="mt-1 w-full min-h-9 border-t border-gray-100 px-3 pt-2 pb-1 text-left text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              Clear
            </button>
          )}
        </div>
      )}
    </div>
  );
}
