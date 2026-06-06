"use client";

import { useState, useRef, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useSavedSchools } from "@/components/SavedSchoolsContext";

type Category = "REACH" | "TARGET" | "SAFETY" | "UNDECIDED";

const CATEGORIES: { value: Category; label: string; color: string }[] = [
  { value: "REACH", label: "Reach", color: "text-red-600" },
  { value: "TARGET", label: "Target", color: "text-yellow-600" },
  { value: "SAFETY", label: "Safety", color: "text-green-600" },
  { value: "UNDECIDED", label: "Undecided", color: "text-gray-500" },
];

interface SaveSchoolButtonProps {
  schoolSlug: string;
  schoolName: string;
  variant?: "icon" | "button";
}

export default function SaveSchoolButton({
  schoolSlug,
  schoolName,
  variant = "icon",
}: SaveSchoolButtonProps) {
  const { data: session } = useSession();
  const { isSaved, getCategory, saveSchool, removeSchool, promptSignIn } = useSavedSchools();
  const [popoverOpen, setPopoverOpen] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);

  const saved = isSaved(schoolSlug);
  const category = getCategory(schoolSlug) ?? "UNDECIDED";
  const categoryInfo = CATEGORIES.find((c) => c.value === category);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setPopoverOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (!session) {
      promptSignIn();
      return;
    }
    setPopoverOpen(!popoverOpen);
  }

  function handleSave(selectedCategory: Category) {
    saveSchool(schoolSlug, selectedCategory);
    setPopoverOpen(false);
  }

  function handleRemove(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    removeSchool(schoolSlug);
    setPopoverOpen(false);
  }

  if (variant === "button") {
    return (
      <div className="relative inline-block" ref={popoverRef}>
        <button
          onClick={handleClick}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
            saved
              ? "bg-white/20 border border-white/40 text-white hover:bg-white/30"
              : "bg-white/10 border border-white/30 text-white hover:bg-white/20"
          }`}
        >
          <svg
            className="w-4 h-4"
            fill={saved ? "currentColor" : "none"}
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
            />
          </svg>
          <span>{saved ? `Saved · ${categoryInfo?.label}` : "Save to My List"}</span>
        </button>

        {popoverOpen && (
          <div className="absolute left-0 mt-2 w-52 bg-white rounded-xl shadow-lg border border-gray-100 p-3 z-50">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              {saved ? schoolName : `Save ${schoolName}`}
            </p>
            <div className="space-y-1">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => handleSave(cat.value)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-between ${
                    category === cat.value && saved ? "bg-gray-100" : "hover:bg-gray-50"
                  }`}
                >
                  <span className={cat.color}>{cat.label}</span>
                  {category === cat.value && saved && (
                    <svg className="w-3.5 h-3.5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
            {saved && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <button
                  onClick={handleRemove}
                  className="w-full text-left px-3 py-1.5 rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors"
                >
                  Remove from list
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // icon variant
  return (
    <div className="relative" ref={popoverRef}>
      <button
        onClick={handleClick}
        className={`p-1.5 rounded-full transition-colors ${
          saved
            ? "text-blue-600 bg-blue-50 hover:bg-blue-100"
            : "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        }`}
        title={saved ? `Saved as ${categoryInfo?.label}` : "Save school"}
      >
        <svg
          className="w-4 h-4"
          fill={saved ? "currentColor" : "none"}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
          />
        </svg>
      </button>

      {popoverOpen && (
        <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-lg border border-gray-100 p-3 z-50">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            {saved ? schoolName : `Save ${schoolName}`}
          </p>
          <div className="space-y-1">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                onClick={() => handleSave(cat.value)}
                className={`w-full text-left px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-between ${
                  category === cat.value && saved ? "bg-gray-100" : "hover:bg-gray-50"
                }`}
              >
                <span className={cat.color}>{cat.label}</span>
                {category === cat.value && saved && (
                  <svg className="w-3.5 h-3.5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>
          {saved && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <button
                onClick={handleRemove}
                className="w-full text-left px-3 py-1.5 rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors"
              >
                Remove from list
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
