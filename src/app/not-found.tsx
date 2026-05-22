import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 px-4 text-center text-white">
        <div className="text-8xl font-bold mb-4 text-gray-400">404</div>
        <h1 className="text-3xl md:text-4xl font-bold mb-3">Page Not Found</h1>
        <p className="text-gray-300 text-lg max-w-xl mx-auto">
          This page doesn&apos;t exist — but plenty of great college data does.
        </p>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="card p-8 text-center">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Looking for a school?
          </h2>
          <p className="text-gray-500 mb-8 text-sm">
            Search for a university from the homepage, or browse our featured schools below.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/"
              className="inline-flex items-center justify-center px-6 py-3 bg-gray-800 hover:bg-gray-900 text-white rounded-lg font-medium transition-colors"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                />
              </svg>
              Back to Home
            </Link>
            <Link
              href="/trends"
              className="inline-flex items-center justify-center px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                />
              </svg>
              Explore Trends
            </Link>
          </div>
        </div>

        <p className="text-center text-gray-400 text-sm mt-8">
          Think something&apos;s missing?{" "}
          <Link href="/contact" className="text-gray-600 hover:text-gray-800 underline">
            Let us know
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
