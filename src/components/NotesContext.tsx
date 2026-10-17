"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";

export interface SchoolNote {
  schoolSlug: string;
  body: string;
}

interface NotesContextValue {
  notes: SchoolNote[];
  getNote: (slug: string) => string | null;
  hasNote: (slug: string) => boolean;
  saveNote: (slug: string, body: string) => Promise<void>;
  deleteNote: (slug: string) => Promise<void>;
  isLoggedIn: boolean;
  loading: boolean;
}

const NotesContext = createContext<NotesContextValue | null>(null);

export function NotesProvider({
  children,
  initialNotes,
  isLoggedIn,
}: {
  children: React.ReactNode;
  initialNotes: SchoolNote[];
  isLoggedIn: boolean;
}) {
  const { data: session } = useSession();
  const [notes, setNotes] = useState<SchoolNote[]>(initialNotes);
  const [loading, setLoading] = useState(false);

  const hadServerData = isLoggedIn;
  useEffect(() => {
    if (!session) {
      setNotes([]);
      return;
    }
    if (hadServerData) return;
    setLoading(true);
    fetch("/api/my-notes")
      .then((r) => r.json())
      .then((data) => setNotes(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [session, hadServerData]);

  const getNote = useCallback(
    (slug: string) => notes.find((n) => n.schoolSlug === slug)?.body ?? null,
    [notes]
  );

  const hasNote = useCallback(
    (slug: string) => notes.some((n) => n.schoolSlug === slug),
    [notes]
  );

  const saveNote = useCallback(async (slug: string, body: string) => {
    const trimmed = body.trim();
    if (!trimmed) return;
    const prevNotes = notes;
    setNotes((prev) => {
      const existing = prev.find((n) => n.schoolSlug === slug);
      if (existing) {
        return prev.map((n) => (n.schoolSlug === slug ? { ...n, body: trimmed } : n));
      }
      return [...prev, { schoolSlug: slug, body: trimmed }];
    });
    try {
      const res = await fetch("/api/my-notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ schoolSlug: slug, body: trimmed }),
      });
      if (!res.ok) throw new Error("save failed");
    } catch {
      setNotes(prevNotes);
    }
  }, [notes]);

  const deleteNote = useCallback(async (slug: string) => {
    const prevNotes = notes;
    setNotes((prev) => prev.filter((n) => n.schoolSlug !== slug));
    try {
      const res = await fetch(`/api/my-notes/${slug}`, { method: "DELETE" });
      if (!res.ok) throw new Error("delete failed");
    } catch {
      setNotes(prevNotes);
    }
  }, [notes]);

  return (
    <NotesContext.Provider
      value={{ notes, getNote, hasNote, saveNote, deleteNote, isLoggedIn, loading }}
    >
      {children}
    </NotesContext.Provider>
  );
}

export function useNotes() {
  const ctx = useContext(NotesContext);
  if (!ctx) throw new Error("useNotes must be used within NotesProvider");
  return ctx;
}
