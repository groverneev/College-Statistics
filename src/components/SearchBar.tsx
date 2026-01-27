"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

interface School {
  name: string;
  slug: string;
  acceptanceRate: number;
}

interface SearchBarProps {
  schools: School[];
}

export default function SearchBar({ schools }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Filter schools based on query
  const filteredSchools = query.trim()
    ? schools
        .filter((school) =>
          school.name.toLowerCase().includes(query.toLowerCase())
        )
        .slice(0, 6)
    : [];

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Reset highlighted index when results change
  useEffect(() => {
    setHighlightedIndex(0);
  }, [filteredSchools.length]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsOpen(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || filteredSchools.length === 0) {
      if (e.key === "Enter" && filteredSchools.length === 0 && query.trim()) {
        // No results, do nothing
        return;
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < filteredSchools.length - 1 ? prev + 1 : 0
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev > 0 ? prev - 1 : filteredSchools.length - 1
        );
        break;
      case "Enter":
        e.preventDefault();
        if (filteredSchools[highlightedIndex]) {
          navigateToSchool(filteredSchools[highlightedIndex].slug);
        }
        break;
      case "Escape":
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  const navigateToSchool = (slug: string) => {
    setQuery("");
    setIsOpen(false);
    router.push(`/${slug}`);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="relative w-full max-w-xl mx-auto">
      {/* Search Input */}
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
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim() && setIsOpen(true)}
          placeholder="Search for a college..."
          className="search-input-animate w-full pl-12 pr-4 py-4 text-lg rounded-full border-2 border-white/30 focus:outline-none focus:border-white text-gray-800 placeholder-gray-500 bg-white"
          autoComplete="off"
        />
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && query.trim() && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl overflow-hidden z-50"
        >
          {filteredSchools.length > 0 ? (
            <ul className="py-2">
              {filteredSchools.map((school, index) => (
                <li key={school.slug}>
                  <button
                    onClick={() => navigateToSchool(school.slug)}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    className={`w-full px-4 py-3 flex items-center justify-between text-left transition-colors ${
                      index === highlightedIndex
                        ? "bg-gray-100"
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <span className="font-medium text-gray-800">
                      {school.name}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatPercent(school.acceptanceRate)} acceptance
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-6 text-center text-gray-500">
              No colleges found matching &quot;{query}&quot;
            </div>
          )}
        </div>
      )}
    </div>
  );
}
