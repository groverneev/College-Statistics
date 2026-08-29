"use client";

import { useEffect } from "react";
import { signIn } from "next-auth/react";

interface SignInPromptProps {
  open: boolean;
  onClose: () => void;
  icon?: string;
  title?: string;
  description?: string;
}

export default function SignInPrompt({
  open,
  onClose,
  icon = "🔖",
  title = "Sign in to save schools",
  description = "Create your free college list and organize schools as Reach, Target, or Safety. Sign in with Google to get started.",
}: SignInPromptProps) {
  // Close on Escape
  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="signin-prompt-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Card */}
      <div className="relative w-full max-w-sm max-h-[calc(100dvh-2rem)] overflow-y-auto bg-white rounded-2xl shadow-xl p-6 text-center">
        <div className="text-4xl mb-3">{icon}</div>
        <h2
          id="signin-prompt-title"
          className="text-lg font-semibold text-gray-800 mb-2"
        >
          {title}
        </h2>
        <p className="text-sm text-gray-500 mb-6">{description}</p>

        <button
          onClick={() => signIn("google")}
          className="w-full min-h-11 flex items-center justify-center space-x-2 bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Sign in with Google</span>
        </button>

        <button
          onClick={onClose}
          className="mt-3 w-full min-h-11 text-sm text-gray-400 hover:text-gray-600 transition-colors"
        >
          Maybe later
        </button>
      </div>
    </div>
  );
}
