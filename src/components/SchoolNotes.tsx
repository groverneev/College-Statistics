"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { useNotes } from "@/components/NotesContext";
import ConfirmDialog from "@/components/ConfirmDialog";

const MAX_NOTE_LENGTH = 5000;

/** How many lines of a note to show before collapsing behind "Show more". */
const COLLAPSED_NOTE_LINES = 8;
const COLLAPSED_NOTE_STYLE: CSSProperties = {
  display: "-webkit-box",
  WebkitLineClamp: COLLAPSED_NOTE_LINES,
  WebkitBoxOrient: "vertical",
  overflow: "hidden",
};

interface SchoolNotesProps {
  schoolSlug: string;
  schoolColor: string;
  /** Mount directly in edit mode (used when opened via the banner "Add note" button). */
  startEditing?: boolean;
  /** Called when the panel should stop being shown (cancelled compose, or note deleted). */
  onClose?: () => void;
}

function NoteIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
      />
    </svg>
  );
}

export default function SchoolNotes({
  schoolSlug,
  schoolColor,
  startEditing = false,
  onClose,
}: SchoolNotesProps) {
  const { getNote, saveNote, deleteNote } = useNotes();

  const note = getNote(schoolSlug);
  const [editing, setEditing] = useState(startEditing);
  const [draft, setDraft] = useState(startEditing ? note ?? "" : "");
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  // Collapse long notes to a fixed number of lines with a "Show more" toggle.
  const noteRef = useRef<HTMLParagraphElement>(null);
  const [collapsed, setCollapsed] = useState(true);
  const [isOverflowing, setIsOverflowing] = useState(false);

  useEffect(() => {
    const el = noteRef.current;
    if (!el || !collapsed) return;
    setIsOverflowing(el.scrollHeight > el.clientHeight + 1);
  }, [note, collapsed, editing]);

  // Auto-grow the editor textarea so it fits its content without inner scrolling.
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    const el = textareaRef.current;
    if (!editing || !el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [editing, draft]);

  function startEdit() {
    setDraft(note ?? "");
    setEditing(true);
  }

  function cancel() {
    setEditing(false);
    setDraft("");
    if (!note) onClose?.(); // composing was cancelled with nothing saved
  }

  async function save() {
    const trimmed = draft.trim();
    if (!trimmed) {
      if (note) await deleteNote(schoolSlug);
      setEditing(false);
      setDraft("");
      onClose?.();
      return;
    }
    await saveNote(schoolSlug, trimmed);
    setEditing(false);
    setDraft("");
  }

  async function confirmDelete() {
    setConfirmingDelete(false);
    await deleteNote(schoolSlug);
    setEditing(false);
    setDraft("");
    onClose?.();
  }

  return (
    <div className="card p-6" style={{ backgroundColor: "#ffffff" }}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="flex items-center gap-2 text-base font-semibold text-gray-800">
          <NoteIcon className="w-[18px] h-[18px]" />
          My note
        </h3>
        {!editing && note && (
          <div className="flex items-center gap-3">
            <button
              onClick={startEdit}
              className="text-sm font-medium transition-colors hover:opacity-80"
              style={{ color: schoolColor }}
            >
              Edit
            </button>
            <button
              onClick={() => setConfirmingDelete(true)}
              className="text-sm font-medium transition-colors hover:opacity-80"
              style={{ color: schoolColor }}
            >
              Delete
            </button>
          </div>
        )}
      </div>

      {editing ? (
        <div>
          <textarea
            ref={textareaRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            maxLength={MAX_NOTE_LENGTH}
            autoFocus
            placeholder="What stood out about this school? Reminders, pros/cons, people to contact…"
            className="w-full min-h-[160px] max-h-[60vh] overflow-y-auto rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-700 resize-y focus:outline-none focus:ring-2"
            style={{ outlineColor: schoolColor }}
          />
          <div className="flex items-center justify-between mt-2.5">
            <span className="text-xs text-gray-400">
              {draft.length}/{MAX_NOTE_LENGTH}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={cancel}
                className="px-4 py-1.5 rounded-lg text-sm text-gray-600 border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={save}
                className="px-4 py-1.5 rounded-lg text-sm font-medium text-white transition-opacity hover:opacity-90"
                style={{ backgroundColor: schoolColor }}
              >
                Save note
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <p
            ref={noteRef}
            className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap"
            style={collapsed ? COLLAPSED_NOTE_STYLE : undefined}
          >
            {note}
          </p>
          {isOverflowing && (
            <button
              onClick={() => setCollapsed((c) => !c)}
              className="mt-1.5 text-sm font-medium transition-colors hover:opacity-80"
              style={{ color: schoolColor }}
            >
              {collapsed ? "Show more" : "Show less"}
            </button>
          )}
          <p className="text-xs text-gray-400 mt-2.5">Only you can see this</p>
        </div>
      )}

      <ConfirmDialog
        open={confirmingDelete}
        onClose={() => setConfirmingDelete(false)}
        onConfirm={confirmDelete}
        title="Delete this note?"
        description="This will permanently remove your note for this school. This can't be undone."
        confirmLabel="Delete note"
        confirmColor={schoolColor}
      />
    </div>
  );
}
