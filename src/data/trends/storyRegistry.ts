import type { ComponentType } from "react";
import CommonApp2026Story from "@/components/trends/stories/CommonApp2026Story";
import UC2026Story from "@/components/trends/stories/UC2026Story";

const storyComponentMap: Record<string, ComponentType> = {
  "common-app-2026": CommonApp2026Story,
  "uc-2026-applications": UC2026Story,
};

export function getStoryComponent(slug: string): ComponentType | null {
  return storyComponentMap[slug] ?? null;
}
