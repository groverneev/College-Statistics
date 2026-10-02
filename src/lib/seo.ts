import type { Metadata } from "next";

export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://collegestatistics.org"
).replace(/\/$/, "");

export const SITE_NAME = "College Statistics";

// Rendered by src/app/opengraph-image.tsx.
const DEFAULT_OG_IMAGE = {
  url: "/opengraph-image",
  width: 1200,
  height: 630,
  alt: "College Statistics – college admissions data from the Common Data Set",
};

interface PageMetadataOptions {
  title: string;
  description: string;
  path: string;
  type?: "website" | "article";
  // Set false on segments with their own opengraph-image file; an explicit
  // image here would take precedence over it.
  defaultImage?: boolean;
}

// Child segments replace (not merge) the parent's openGraph/twitter objects,
// so every page builds the full set here to keep site-wide fields intact.
export function pageMetadata({
  title,
  description,
  path,
  type = "website",
  defaultImage = true,
}: PageMetadataOptions): Metadata {
  // Omit the key entirely: even `images: undefined` hides a segment's own file.
  const images = defaultImage ? { images: [DEFAULT_OG_IMAGE] } : {};
  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      title,
      description,
      url: path,
      siteName: SITE_NAME,
      locale: "en_US",
      type,
      ...images,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      ...images,
    },
  };
}
