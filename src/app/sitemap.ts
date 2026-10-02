import type { MetadataRoute } from "next";
import { allSchools } from "@/data/schools";
import { trends } from "@/data/trends/index";
import { INTERNATIONAL_PREVIEW_SLUG } from "@/lib/internationalPreviewConfig";
import { SITE_URL } from "@/lib/seo";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPages: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}/`, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE_URL}/schools`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${SITE_URL}/trends`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${SITE_URL}/uc`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${SITE_URL}/csu`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${SITE_URL}/how-it-works`, changeFrequency: "yearly", priority: 0.5 },
    { url: `${SITE_URL}/about`, changeFrequency: "yearly", priority: 0.4 },
    { url: `${SITE_URL}/contact`, changeFrequency: "yearly", priority: 0.3 },
  ];

  const schoolPages: MetadataRoute.Sitemap = allSchools.map((school) => ({
    url: `${SITE_URL}/${school.slug}`,
    changeFrequency: "monthly",
    priority: 0.9,
  }));

  // The password-gated preview story is excluded until it is public.
  const trendPages: MetadataRoute.Sitemap = trends
    .filter((story) => story.slug !== INTERNATIONAL_PREVIEW_SLUG)
    .map((story) => ({
      url: `${SITE_URL}/trends/${story.slug}`,
      lastModified: story.date,
      changeFrequency: "monthly",
      priority: 0.7,
    }));

  return [...staticPages, ...schoolPages, ...trendPages];
}
