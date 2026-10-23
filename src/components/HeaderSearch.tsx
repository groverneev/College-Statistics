"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import SchoolSearchResults, { searchSchools } from "@/components/SchoolSearchResults";
import type { SearchableSchool } from "@/data/schools";

interface HeaderSearchProps {
  schools: SearchableSchool[];
}

function SearchIcon({ className }: { className: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
  );
}

export default function HeaderSearch({ schools }: HeaderSearchProps) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handleShortcut = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(true);
        return;
      }
      if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
      const target = e.target as HTMLElement | null;
      if (
        target &&
        (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName))
      ) {
        return;
      }
      e.preventDefault();
      setOpen(true);
    };

    document.addEventListener("keydown", handleShortcut);
    return () => document.removeEventListener("keydown", handleShortcut);
  }, []);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Search colleges"
        title="Search colleges (/)"
        className="flex h-9 w-12 items-center justify-center rounded-full border border-black/10 bg-white text-gray-500 hover:text-gray-900 hover:border-black/20 transition-colors"
      >
        <SearchIcon className="w-4 h-4" />
      </button>

      {open && <SearchDialog schools={schools} onClose={() => setOpen(false)} />}
    </>
  );
}

function SearchDialog({
  schools,
  onClose,
}: {
  schools: SearchableSchool[];
  onClose: () => void;
}) {
  const [query, setQuery] = useState("");
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const results = searchSchools(schools, query);

  useEffect(() => {
    inputRef.current?.focus();
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, []);

  const navigateToSchool = (slug: string) => {
    onClose();
    router.push(`/${slug}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        if (results.length) setHighlightedIndex((i) => (i + 1) % results.length);
        break;
      case "ArrowUp":
        e.preventDefault();
        if (results.length) {
          setHighlightedIndex((i) => (i - 1 + results.length) % results.length);
        }
        break;
      case "Enter":
        e.preventDefault();
        if (results[highlightedIndex]) navigateToSchool(results[highlightedIndex].slug);
        break;
      case "Escape":
        e.preventDefault();
        onClose();
        break;
    }
  };

  return (
    <div
      className="fixed inset-0 z-[60] flex items-start justify-center bg-black/30 px-4 pt-[12vh] backdrop-blur-[2px]"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Search colleges"
        className="flex w-full max-w-xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl"
        onKeyDown={handleKeyDown}
      >
        <div className="flex items-center gap-3 border-b border-gray-100 px-4">
          <SearchIcon className="w-5 h-5 shrink-0 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setHighlightedIndex(0);
            }}
            placeholder="Search for a college..."
            aria-label="Search for a college"
            className="w-full py-4 text-base text-gray-800 placeholder-gray-500 focus:outline-none"
            autoComplete="off"
          />
        </div>

        <SchoolSearchResults
          results={results}
          query={query}
          highlightedIndex={highlightedIndex}
          onHighlight={setHighlightedIndex}
          onSelect={navigateToSchool}
        />
      </div>
    </div>
  );
}
