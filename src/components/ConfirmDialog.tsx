"use client";

import { useEffect } from "react";

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  icon?: string;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  /** Background color for the confirm button (defaults to a neutral red). */
  confirmColor?: string;
}

export default function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  icon = "🗑️",
  title = "Are you sure?",
  description,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  confirmColor = "#ef4444",
}: ConfirmDialogProps) {
  // Close on Escape
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Card */}
      <div className="relative w-full max-w-sm bg-white rounded-2xl shadow-xl p-6 text-center">
        <div className="text-4xl mb-3">{icon}</div>
        <h2
          id="confirm-dialog-title"
          className="text-lg font-semibold text-gray-800 mb-2"
        >
          {title}
        </h2>
        {description && (
          <p className="text-sm text-gray-500 mb-6">{description}</p>
        )}

        <button
          onClick={onConfirm}
          className="w-full rounded-lg px-4 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: confirmColor }}
        >
          {confirmLabel}
        </button>

        <button
          onClick={onClose}
          className="mt-3 w-full text-sm text-gray-400 hover:text-gray-600 transition-colors"
        >
          {cancelLabel}
        </button>
      </div>
    </div>
  );
}
