import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import { trends } from "@/data/trends/index";
import { getStoryComponent } from "@/data/trends/storyRegistry";
import {
  getInternationalPreviewToken,
  INTERNATIONAL_PREVIEW_COOKIE,
} from "@/lib/internationalPreview";
import { INTERNATIONAL_PREVIEW_SLUG } from "@/lib/internationalPreviewConfig";

export function generateStaticParams() {
  return trends.map((t) => ({ slug: t.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const story = trends.find((t) => t.slug === slug);
  if (!story) return {};
  return {
    title: `${story.title} – College Statistics`,
    description: story.preview,
  };
}

export default async function StoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const story = trends.find((t) => t.slug === slug);
  const StoryComponent = getStoryComponent(slug);
  if (!story) notFound();
  if (!StoryComponent) notFound();

  if (slug === INTERNATIONAL_PREVIEW_SLUG) {
    const previewPassword = process.env.REPORTER_PREVIEW_PASSWORD;
    const previewCookie = (await cookies()).get(INTERNATIONAL_PREVIEW_COOKIE)?.value;
    const isAuthorized =
      previewPassword !== undefined &&
      previewCookie === getInternationalPreviewToken(previewPassword);

    if (!isAuthorized) {
      redirect(`/trends?preview=${INTERNATIONAL_PREVIEW_SLUG}`);
    }
  }

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-14 px-4 text-center text-white">
        <div className="flex flex-wrap justify-center gap-2 mb-4">
          {story.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs font-medium px-3 py-1 bg-white/10 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
        <h1 className="text-3xl md:text-4xl font-bold mb-3 max-w-3xl mx-auto leading-tight">
          {story.title}
        </h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto mb-2">
          {story.subtitle}
        </p>
        <p className="text-gray-400 text-sm">
          {new Date(story.date).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
            timeZone: "UTC",
          })}
        </p>
      </div>

      {/* Story Content */}
      <div className="max-w-5xl mx-auto px-4 py-10">
        <StoryComponent />
      </div>
    </div>
  );
}
