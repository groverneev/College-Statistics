"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { INTERNATIONAL_PREVIEW_SLUG } from "@/lib/internationalPreviewConfig";

export default function InternationalPreviewPrompt({ open }: { open: boolean }) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const isSubmittingRef = useRef(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    const previouslyFocused =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.body.style.overflow = "hidden";
    inputRef.current?.focus({ preventScroll: true });

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !isSubmittingRef.current) {
        event.preventDefault();
        setPassword("");
        setError("");
        router.replace("/trends", { scroll: false });
      }

      if (event.key !== "Tab") return;

      const focusable = dialogRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
      );
      if (!focusable?.length) {
        event.preventDefault();
        dialogRef.current?.focus({ preventScroll: true });
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (!dialogRef.current?.contains(document.activeElement)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
      } else if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus({ preventScroll: true });
    };
  }, [open, router]);

  if (!open) return null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmittingRef.current) return;

    isSubmittingRef.current = true;
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/international-enrollment-preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const result = (await response.json().catch(() => ({}))) as { error?: string };

      if (!response.ok) {
        setError(result.error ?? "Unable to unlock this story.");
        isSubmittingRef.current = false;
        setIsSubmitting(false);
        requestAnimationFrame(() => {
          inputRef.current?.focus({ preventScroll: true });
          inputRef.current?.select();
        });
        return;
      }

      // Replace the prompt URL so Back returns to the trends list instead of
      // reopening the password prompt. A full navigation makes the server
      // evaluate the newly set cookie rather than a cached protected route.
      window.location.replace(`/trends/${INTERNATIONAL_PREVIEW_SLUG}`);
    } catch {
      setError("Something went wrong. Please try again.");
      isSubmittingRef.current = false;
      setIsSubmitting(false);
      requestAnimationFrame(() => {
        inputRef.current?.focus({ preventScroll: true });
        inputRef.current?.select();
      });
    }
  }

  function closePrompt() {
    if (isSubmittingRef.current) return;

    setPassword("");
    setError("");
    router.replace("/trends", { scroll: false });
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
    >
      <button
        type="button"
        className="absolute inset-0 h-full w-full cursor-default bg-black/40"
        onClick={closePrompt}
        aria-label="Close preview password prompt"
      />

      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="international-preview-title"
        aria-describedby="international-preview-description"
        tabIndex={-1}
        className="relative w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-xl sm:p-7"
      >
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
        <p
          id="international-preview-description"
          className="mb-6 text-sm leading-relaxed text-gray-500"
        >
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
            aria-errormessage={error ? "international-preview-error" : undefined}
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
