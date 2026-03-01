import Link from "next/link";
import { TrendMeta } from "@/data/trends/index";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default function StoryCard({ story }: { story: TrendMeta }) {
  return (
    <Link href={`/trends/${story.slug}`}>
      <div className="card p-6 hover:shadow-lg transition-shadow cursor-pointer border-t-4 border-t-gray-800 h-full flex flex-col">
        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-3">
          {story.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs font-medium px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-800 mb-1 leading-snug">
          {story.title}
        </h3>

        {/* Subtitle */}
        <p className="text-sm text-gray-500 mb-3">{story.subtitle}</p>

        {/* Preview */}
        <p className="text-sm text-gray-600 flex-1">{story.preview}</p>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <span className="text-xs text-gray-400">{formatDate(story.date)}</span>
          <span className="text-sm font-medium text-gray-800">Read &rarr;</span>
        </div>
      </div>
    </Link>
  );
}
