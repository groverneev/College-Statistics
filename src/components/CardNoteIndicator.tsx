"use client";

import { useNotes } from "@/components/NotesContext";

export default function CardNoteIndicator({ schoolSlug }: { schoolSlug: string }) {
  const { getNote } = useNotes();
  const note = getNote(schoolSlug);
  if (!note) return null;

  // First non-empty line, used as a one-line preview
  const preview = note.split("\n").find((line) => line.trim().length > 0)?.trim() ?? "";

  return (
    <div className="mt-3">
      <span className="inline-flex items-center gap-1.5 text-xs text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
        Note
      </span>
      <p className="mt-2 text-xs text-gray-400 italic truncate">{preview}</p>
    </div>
  );
}
