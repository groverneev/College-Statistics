"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import SchoolCard from "@/components/SchoolCard";
import { allSchools } from "@/data/schools";

// Matches the old CSS animation's pace: a full -50% loop over 430s.
const LOOP_DURATION_MS = 430_000;

export default function SchoolCarousel() {
  const trackRef = useRef<HTMLDivElement>(null);
  const positionRef = useRef(0);
  const singleWidthRef = useRef(0);
  const isHoveredRef = useRef(false);
  const isDraggingRef = useRef(false);
  const dragStartXRef = useRef(0);
  const dragStartPositionRef = useRef(0);
  const draggedRef = useRef(false);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;
    if (reduceMotion) return;

    singleWidthRef.current = track.scrollWidth / 2;
    const speed = singleWidthRef.current / LOOP_DURATION_MS;

    const applyTransform = () => {
      track.style.transform = `translateX(-${positionRef.current}px)`;
    };

    const wrapPosition = () => {
      const w = singleWidthRef.current;
      if (w > 0) {
        positionRef.current = ((positionRef.current % w) + w) % w;
      }
    };

    let lastTime: number | null = null;
    let rafId: number;

    const step = (time: number) => {
      if (lastTime === null) lastTime = time;
      const dt = time - lastTime;
      lastTime = time;

      if (!isHoveredRef.current && !isDraggingRef.current) {
        positionRef.current += speed * dt;
        wrapPosition();
        applyTransform();
      }
      rafId = requestAnimationFrame(step);
    };

    rafId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(rafId);
  }, []);

  // Deliberately not using setPointerCapture here: capturing on the mask
  // redirects the follow-up mouseup/click to the mask itself, which kills
  // normal card-link clicks. Tracking move/up on window instead leaves
  // click delivery to the real element under the pointer.
  const handlePointerMoveWindow = (e: PointerEvent) => {
    const dx = e.clientX - dragStartXRef.current;
    if (Math.abs(dx) > 3) draggedRef.current = true;

    const w = singleWidthRef.current;
    let newPos = dragStartPositionRef.current - dx;
    newPos = ((newPos % w) + w) % w;
    positionRef.current = newPos;
    if (trackRef.current) {
      trackRef.current.style.transform = `translateX(-${newPos}px)`;
    }
  };

  const handlePointerUpWindow = () => {
    isDraggingRef.current = false;
    setIsDragging(false);
    window.removeEventListener("pointermove", handlePointerMoveWindow);
    window.removeEventListener("pointerup", handlePointerUpWindow);
    window.removeEventListener("pointercancel", handlePointerUpWindow);
  };

  const handlePointerDown = (e: React.PointerEvent) => {
    if (singleWidthRef.current <= 0) return;
    isDraggingRef.current = true;
    draggedRef.current = false;
    dragStartXRef.current = e.clientX;
    dragStartPositionRef.current = positionRef.current;
    setIsDragging(true);
    window.addEventListener("pointermove", handlePointerMoveWindow);
    window.addEventListener("pointerup", handlePointerUpWindow);
    window.addEventListener("pointercancel", handlePointerUpWindow);
  };

  const handleClickCapture = (e: React.MouseEvent) => {
    // Suppress the click that follows a drag so we don't accidentally
    // navigate into a school page while the user was just panning.
    if (draggedRef.current) {
      e.preventDefault();
      e.stopPropagation();
      draggedRef.current = false;
    }
  };

  return (
    <div className="pt-4 pb-8 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 flex items-baseline justify-between mb-5">
        <h2 className="section-label">All {allSchools.length} schools</h2>
        <Link href="/schools" className="browse-all-btn">
          Browse all
          <span aria-hidden>&rarr;</span>
        </Link>
      </div>

      {/* Padding lives on this wrapper (not .marquee-mask) so the track's
          translated cards are actually confined inside the inset box —
          padding on the overflow:hidden element itself doesn't stop a
          transformed child from reaching the true edge, only a narrower
          box does. */}
      <div className="max-w-6xl mx-auto px-4">
        <div
          className={`marquee-mask${isDragging ? " marquee-dragging" : ""}`}
          onMouseEnter={() => {
            isHoveredRef.current = true;
          }}
          onMouseLeave={() => {
            isHoveredRef.current = false;
          }}
          onPointerDown={handlePointerDown}
          onClickCapture={handleClickCapture}
          onDragStart={(e) => e.preventDefault()}
        >
          <div ref={trackRef} className="marquee-track">
            {/* Two identical copies make the -50% translate loop seamless. The
                second is decorative only, so it's hidden from AT and tab order. */}
            {[0, 1].map((copy) => (
              <div
                key={copy}
                className="flex"
                aria-hidden={copy === 1 || undefined}
                inert={copy === 1 || undefined}
              >
                {allSchools.map((school) => (
                  <div
                    key={`${copy}-${school.slug}`}
                    className="w-[calc(100vw-3rem)] max-w-80 flex-shrink-0 mr-4"
                  >
                    <SchoolCard school={school} showSaveButton />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
