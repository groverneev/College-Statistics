"use client";

import { useEffect, useRef } from "react";
import type { SearchableSchool } from "@/data/schools";
import { formatPercent } from "@/utils/dataHelpers";

/** All schools A–Z for an empty query; otherwise matches by name or alias, prefix matches first. */
export function searchSchools(schools: SearchableSchool[], query: string): SearchableSchool[] {
  const q = query.trim().toLowerCase();
  if (!q) return [...schools].sort((a, b) => a.name.localeCompare(b.name));

  return schools
    .filter(
      (school) =>
        school.name.toLowerCase().includes(q) ||
        school.aliases.some((alias) => alias.toLowerCase().includes(q)),
    )
    .sort(
      (a, b) =>
        Number(b.name.toLowerCase().startsWith(q)) - Number(a.name.toLowerCase().startsWith(q)),
    );
}

interface SchoolSearchResultsProps {
  results: SearchableSchool[];
  query: string;
  highlightedIndex: number;
  onHighlight: (index: number) => void;
  onSelect: (slug: string) => void;
  className?: string;
}

export default function SchoolSearchResults({
  results,
  query,
  highlightedIndex,
  onHighlight,
  onSelect,
  className = "",
}: SchoolSearchResultsProps) {
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    listRef.current
      ?.querySelector(`[data-index="${highlightedIndex}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [highlightedIndex]);

  if (results.length === 0) {
    return (
      <div className="px-4 py-8 text-center text-gray-500">
        No colleges found matching &quot;{query}&quot;
      </div>
    );
  }

  return (
    <ul
      ref={listRef}
      className={`max-h-[min(26rem,calc(100dvh-14rem))] overflow-y-auto overscroll-contain py-2 ${className}`}
    >
      {results.map((school, index) => (
        <li key={school.slug} data-index={index}>
          <button
            type="button"
            onClick={() => onSelect(school.slug)}
            onMouseMove={() => onHighlight(index)}
            className={`w-full min-h-11 px-4 py-2.5 flex items-center justify-between gap-3 text-left transition-colors ${
              index === highlightedIndex ? "bg-gray-100" : ""
            }`}
          >
            <span className="min-w-0 font-medium text-gray-800">{school.name}</span>
            <span className="shrink-0 text-sm text-gray-500">
              {formatPercent(school.acceptanceRate)} acceptance
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
