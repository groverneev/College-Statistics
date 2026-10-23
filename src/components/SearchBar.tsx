"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import SchoolSearchResults, { searchSchools } from "@/components/SchoolSearchResults";
import type { SearchableSchool } from "@/data/schools";

interface SearchBarProps {
  schools: SearchableSchool[];
}

export default function SearchBar({ schools }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const results = searchSchools(schools, query);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setIsOpen(false);
      inputRef.current?.blur();
      return;
    }
    if (!isOpen) {
      if (e.key === "ArrowDown") setIsOpen(true);
      return;
    }
    if (results.length === 0) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((i) => (i + 1) % results.length);
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((i) => (i - 1 + results.length) % results.length);
        break;
      case "Enter":
        e.preventDefault();
        if (results[highlightedIndex]) navigateToSchool(results[highlightedIndex].slug);
        break;
    }
  };

  const navigateToSchool = (slug: string) => {
    setQuery("");
    setIsOpen(false);
    router.push(`/${slug}`);
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-2xl mx-auto">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setHighlightedIndex(0);
            setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          onClick={() => setIsOpen(true)}
          placeholder="Search for a college..."
          className="search-input-animate w-full pl-12 pr-4 py-4 text-lg rounded-full border-2 border-black/10 focus:outline-none focus:border-indigo-400 text-gray-800 placeholder-gray-500 bg-white"
          autoComplete="off"
        />
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 overflow-hidden rounded-2xl bg-white text-left shadow-xl z-50">
          <SchoolSearchResults
            results={results}
            query={query}
            highlightedIndex={highlightedIndex}
            onHighlight={setHighlightedIndex}
            onSelect={navigateToSchool}
          />
        </div>
      )}
    </div>
  );
}
