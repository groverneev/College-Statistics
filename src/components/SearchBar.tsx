"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { formatPercent } from "@/utils/dataHelpers";

interface School {
  name: string;
  slug: string;
  acceptanceRate: number;
}

interface SearchBarProps {
  schools: School[];
}

const SCHOOL_ALIASES: Record<string, string[]> = {
  mit: ["MIT", "Massachusetts Institute of Technology"],
  upenn: ["UPenn", "Penn", "U Penn", "University of Pennsylvania"],
  caltech: ["Caltech", "Cal Tech", "CIT"],
  cmu: ["CMU", "Carnegie Mellon", "Carnegie-Mellon"],
  ucla: ["UCLA", "University of California Los Angeles", "UC Los Angeles"],
  ucberkeley: [
    "UC Berkeley",
    "Cal",
    "Berkeley",
    "University of California Berkeley",
  ],
  ucdavis: [
    "UC Davis",
    "University of California Davis",
    "University of California, Davis",
    "Davis",
  ],
  ucsb: [
    "UCSB",
    "UC Santa Barbara",
    "University of California Santa Barbara",
    "University of California, Santa Barbara",
    "Santa Barbara",
  ],
  ucsandiego: [
    "UCSD",
    "UC San Diego",
    "University of California San Diego",
    "University of California, San Diego",
    "San Diego",
  ],
  uci: [
    "UCI",
    "UC Irvine",
    "University of California Irvine",
    "University of California, Irvine",
    "Irvine",
  ],
  uflorida: ["UF", "UFlorida", "U of F", "Florida", "University of Florida"],
  uiuc: [
    "UIUC",
    "University of Illinois Urbana-Champaign",
    "University of Illinois",
    "Illinois",
    "U of I",
    "Urbana-Champaign",
  ],
  uncchapelhill: [
    "UNC",
    "UNC Chapel Hill",
    "UNC-Chapel Hill",
    "Carolina",
    "University of North Carolina",
    "University of North Carolina at Chapel Hill",
  ],
  usc: ["USC", "Southern Cal", "University of Southern California"],
  brown: ["Brown"],
  bostoncollege: ["BC", "Boston College"],
  bostonuniversity: ["BU", "Boston U", "Boston University"],
  casewesternreserve: [
    "Case Western",
    "Case Western Reserve",
    "Case Western Reserve University",
    "CWRU",
  ],
  columbia: ["Columbia"],
  cornell: ["Cornell"],
  dartmouth: ["Dartmouth"],
  duke: ["Duke"],
  emory: ["Emory", "Emory University"],
  georgiatech: [
    "Georgia Tech",
    "Georgia Institute of Technology",
    "Georgia Tech University",
    "GaTech",
    "GT",
  ],
  georgetown: ["Georgetown", "Georgetown University", "GU"],
  harvard: ["Harvard"],
  johnshopkins: ["JHU", "Johns Hopkins", "Johns Hopkins University", "Hopkins"],
  northeastern: ["Northeastern", "Northeastern University", "NEU"],
  notredame: ["Notre Dame", "University of Notre Dame", "ND"],
  nyu: ["NYU", "New York University"],
  ohiostate: [
    "OSU",
    "Ohio State",
    "Ohio State University",
    "The Ohio State University",
    "tOSU",
  ],
  pennstate: [
    "Penn State",
    "Penn State University",
    "Pennsylvania State University",
    "PSU",
  ],
  northwestern: ["NU", "Northwestern"],
  princeton: ["Princeton"],
  rice: ["Rice", "Rice University", "William Marsh Rice University"],
  purdue: ["Purdue", "Purdue University", "Purdue West Lafayette"],
  rutgersnewbrunswick: [
    "Rutgers",
    "Rutgers New Brunswick",
    "Rutgers-New Brunswick",
    "RU",
  ],
  stanford: ["Stanford"],
  tufts: ["Tufts", "Tufts University"],
  uchicago: ["UChicago", "University of Chicago", "Chicago"],
  umich: [
    "UMich",
    "U-M",
    "Michigan",
    "University of Michigan",
    "University of Michigan Ann Arbor",
    "UM Ann Arbor",
  ],
  universitypittsburgh: [
    "Pitt",
    "University of Pittsburgh",
    "Pittsburgh",
    "Pittsburgh Campus",
    "UPitt",
    "U Pitt",
  ],
  uwmadison: [
    "UW Madison",
    "UW-Madison",
    "Wisconsin",
    "Wisconsin Madison",
    "University of Wisconsin",
    "University of Wisconsin Madison",
    "University of Wisconsin-Madison",
  ],
  utexasaustin: [
    "UT Austin",
    "UTexasAustin",
    "UTexas",
    "University of Texas at Austin",
    "University of Texas Austin",
  ],
  uva: ["UVA", "University of Virginia", "Virginia", "U. Virginia"],
  vanderbilt: ["Vanderbilt", "Vandy", "Vanderbilt University"],
  wakeforest: ["Wake", "Wake Forest", "Wake Forest University"],
  washu: [
    "WashU",
    "Wash U",
    "WUSTL",
    "Washington University",
    "Washington University in St. Louis",
    "Washington University in St Louis",
  ],
  yale: ["Yale"],
};

export default function SearchBar({ schools }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const filteredSchools = query.trim()
    ? schools
        .filter((school) => {
          const q = query.toLowerCase();
          if (school.name.toLowerCase().includes(q)) return true;
          const aliases = SCHOOL_ALIASES[school.slug] ?? [];
          return aliases.some((alias) => alias.toLowerCase().includes(q));
        })
        .slice(0, 6)
    : [];

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

  return (
    <div className="relative w-full max-w-xl mx-auto">
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
