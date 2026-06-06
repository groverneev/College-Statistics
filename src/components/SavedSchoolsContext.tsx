"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import SignInPrompt from "@/components/SignInPrompt";

type Category = "REACH" | "TARGET" | "SAFETY" | "UNDECIDED";

interface SavedSchool {
  schoolSlug: string;
  category: Category;
}

interface SavedSchoolsContextValue {
  savedSchools: SavedSchool[];
  isSaved: (slug: string) => boolean;
  getCategory: (slug: string) => Category | null;
  saveSchool: (slug: string, category: Category) => Promise<void>;
  removeSchool: (slug: string) => Promise<void>;
  promptSignIn: () => void;
  isLoggedIn: boolean;
  loading: boolean;
}

const SavedSchoolsContext = createContext<SavedSchoolsContextValue | null>(null);

export function SavedSchoolsProvider({
  children,
  initialSavedSchools,
  isLoggedIn,
}: {
  children: React.ReactNode;
  initialSavedSchools: SavedSchool[];
  isLoggedIn: boolean;
}) {
  const { data: session } = useSession();
  // Initialize directly with server data — present during SSR, no post-hydration flash
  const [savedSchools, setSavedSchools] = useState<SavedSchool[]>(initialSavedSchools);
  const [loading, setLoading] = useState(false);
  const [signInPromptOpen, setSignInPromptOpen] = useState(false);

  const promptSignIn = useCallback(() => setSignInPromptOpen(true), []);

  // Only fetch client-side if the user logs in AFTER initial load (e.g. signs in
  // without a full reload). On a normal page load the server already seeded us.
  const hadServerData = isLoggedIn;
  useEffect(() => {
    if (!session) {
      setSavedSchools([]);
      return;
    }
    if (hadServerData) return; // server already provided the list
    setLoading(true);
    fetch("/api/my-schools")
      .then((r) => r.json())
      .then((data) => setSavedSchools(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [session, hadServerData]);

  const isSaved = useCallback(
    (slug: string) => savedSchools.some((s) => s.schoolSlug === slug),
    [savedSchools]
  );

  const getCategory = useCallback(
    (slug: string) => savedSchools.find((s) => s.schoolSlug === slug)?.category ?? null,
    [savedSchools]
  );

  const saveSchool = useCallback(async (slug: string, category: Category) => {
    // Optimistic update — UI changes instantly
    setSavedSchools((prev) => {
      const existing = prev.find((s) => s.schoolSlug === slug);
      if (existing) {
        return prev.map((s) => s.schoolSlug === slug ? { ...s, category } : s);
      }
      return [...prev, { schoolSlug: slug, category }];
    });
    // Sync to DB in background
    try {
      await fetch("/api/my-schools", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ schoolSlug: slug, category }),
      });
    } catch {
      // Roll back on failure
      setSavedSchools((prev) => prev.filter((s) => s.schoolSlug !== slug));
    }
  }, []);

  const removeSchool = useCallback(async (slug: string) => {
    // Optimistic update — UI changes instantly
    setSavedSchools((prev) => prev.filter((s) => s.schoolSlug !== slug));
    // Sync to DB in background
    try {
      await fetch(`/api/my-schools/${slug}`, { method: "DELETE" });
    } catch {
      // Roll back on failure — re-fetch to restore accurate state
      fetch("/api/my-schools")
        .then((r) => r.json())
        .then((data) => setSavedSchools(data))
        .catch(() => {});
    }
  }, []);

  return (
    <SavedSchoolsContext.Provider
      value={{ savedSchools, isSaved, getCategory, saveSchool, removeSchool, promptSignIn, isLoggedIn, loading }}
    >
      {children}
      <SignInPrompt
        open={signInPromptOpen}
        onClose={() => setSignInPromptOpen(false)}
      />
    </SavedSchoolsContext.Provider>
  );
}

export function useSavedSchools() {
  const ctx = useContext(SavedSchoolsContext);
  if (!ctx) throw new Error("useSavedSchools must be used within SavedSchoolsProvider");
  return ctx;
}
