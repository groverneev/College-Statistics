"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { INTERNATIONAL_PREVIEW_SLUG } from "@/lib/internationalPreviewConfig";

export default function InternationalPreviewPrompt({ open }: { open: boolean }) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    inputRef.current?.focus();

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        router.replace("/trends", { scroll: false });
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, router]);

  if (!open) return null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/international-enrollment-preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const result = (await response.json()) as { error?: string };

      if (!response.ok) {
        setError(result.error ?? "Unable to unlock this story.");
        setIsSubmitting(false);
        return;
      }

      // Use a full navigation so the server evaluates the newly-set cookie
      // instead of reusing a prefetched redirect from the locked route.
      window.location.assign(`/trends/${INTERNATIONAL_PREVIEW_SLUG}`);
    } catch {
      setError("Something went wrong. Please try again.");
      setIsSubmitting(false);
    }
  }

  function closePrompt() {
    if (!isSubmitting) router.replace("/trends", { scroll: false });
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="international-preview-title"
    >
      <button
        type="button"
        className="absolute inset-0 h-full w-full cursor-default bg-black/40"
        onClick={closePrompt}
        aria-label="Close preview password prompt"
      />

      <div className="relative w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-xl sm:p-7">
        <div
          className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-2xl"
          aria-hidden="true"
        >
          🔒
        </div>
        <h2
          id="international-preview-title"
          className="mb-2 text-lg font-semibold text-gray-800"
        >
          This story is private
        </h2>
        <p className="mb-6 text-sm leading-relaxed text-gray-500">
          Enter the password shared with you to read the international enrollment story.
        </p>

        <form onSubmit={handleSubmit} className="text-left">
          <label htmlFor="international-preview-password" className="sr-only">
            Preview password
          </label>
          <input
            ref={inputRef}
            id="international-preview-password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
              if (error) setError("");
            }}
            placeholder="Password"
            disabled={isSubmitting}
            className="form-input min-h-11"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "international-preview-error" : undefined}
          />
          {error && (
            <p
              id="international-preview-error"
              className="mt-2 text-sm text-red-600"
              role="alert"
            >
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={!password || isSubmitting}
            className="mt-4 flex min-h-11 w-full items-center justify-center rounded-lg bg-gray-800 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? "Checking password…" : "Continue to story"}
          </button>
        </form>

        <button
          type="button"
          onClick={closePrompt}
          disabled={isSubmitting}
          className="mt-3 min-h-11 w-full text-sm text-gray-400 transition-colors hover:text-gray-600 disabled:cursor-not-allowed"
        >
          Maybe later
        </button>
      </div>
    </div>
  );
}
