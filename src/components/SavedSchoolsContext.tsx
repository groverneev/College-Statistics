"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import type { Category } from "@/db/schema";
import { useSession } from "@/lib/auth-client";
import SignInPrompt from "@/components/SignInPrompt";

interface SavedSchool {
  schoolSlug: string;
  category: Category;
}

export interface SignInPromptOptions {
  icon?: string;
  title?: string;
  description?: string;
}

interface SavedSchoolsContextValue {
  savedSchools: SavedSchool[];
  isSaved: (slug: string) => boolean;
  getCategory: (slug: string) => Category | null;
  saveSchool: (slug: string, category: Category) => Promise<void>;
  removeSchool: (slug: string) => Promise<void>;
  promptSignIn: (options?: SignInPromptOptions) => void;
  isLoggedIn: boolean;
  loading: boolean;
}

const SavedSchoolsContext = createContext<SavedSchoolsContextValue | null>(null);

export function SavedSchoolsProvider({ children }: { children: React.ReactNode }) {
  const { data: session } = useSession();
  const userId = session?.user.id;
  const isLoggedIn = !!userId;
  const [savedSchools, setSavedSchools] = useState<SavedSchool[]>([]);
  const [loading, setLoading] = useState(false);
  const [signInPromptOpen, setSignInPromptOpen] = useState(false);
  const [signInPromptOptions, setSignInPromptOptions] = useState<SignInPromptOptions>({});

  const promptSignIn = useCallback((options: SignInPromptOptions = {}) => {
    setSignInPromptOptions(options);
    setSignInPromptOpen(true);
  }, []);

  useEffect(() => {
    if (!userId) {
      setSavedSchools([]);
      return;
    }
    setLoading(true);
    fetch("/api/my-schools")
      .then((r) => r.json())
      .then((data) => setSavedSchools(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  const isSaved = useCallback(
    (slug: string) => savedSchools.some((s) => s.schoolSlug === slug),
    [savedSchools],
  );

  const getCategory = useCallback(
    (slug: string) => savedSchools.find((s) => s.schoolSlug === slug)?.category ?? null,
    [savedSchools],
  );

  const saveSchool = useCallback(async (slug: string, category: Category) => {
    setSavedSchools((prev) => {
      const existing = prev.find((s) => s.schoolSlug === slug);
      if (existing) {
        return prev.map((s) => (s.schoolSlug === slug ? { ...s, category } : s));
      }
      return [...prev, { schoolSlug: slug, category }];
    });
    try {
      await fetch("/api/my-schools", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ schoolSlug: slug, category }),
      });
    } catch {
      setSavedSchools((prev) => prev.filter((s) => s.schoolSlug !== slug));
    }
  }, []);

  const removeSchool = useCallback(async (slug: string) => {
    setSavedSchools((prev) => prev.filter((s) => s.schoolSlug !== slug));
    try {
      await fetch(`/api/my-schools/${slug}`, { method: "DELETE" });
    } catch {
      fetch("/api/my-schools")
        .then((r) => r.json())
        .then((data) => setSavedSchools(data))
        .catch(() => {});
    }
  }, []);

  return (
    <SavedSchoolsContext.Provider
      value={{
        savedSchools,
        isSaved,
        getCategory,
        saveSchool,
        removeSchool,
        promptSignIn,
        isLoggedIn,
        loading,
      }}
    >
      {children}
      <SignInPrompt
        open={signInPromptOpen}
        onClose={() => setSignInPromptOpen(false)}
        icon={signInPromptOptions.icon}
        title={signInPromptOptions.title}
        description={signInPromptOptions.description}
      />
    </SavedSchoolsContext.Provider>
  );
}

export function useSavedSchools() {
  const ctx = useContext(SavedSchoolsContext);
  if (!ctx) throw new Error("useSavedSchools must be used within SavedSchoolsProvider");
  return ctx;
}
