import Link from "next/link";

export default function AboutPage() {
  const socialLinks = [
    {
      href: "https://x.com/groverneev01",
      label: "Twitter",
    },
    {
      href: "https://github.com/groverneev",
      label: "GitHub",
    },
    {
      href: "https://techunpacked.substack.com",
      label: "Blog",
    },
    {
      href: "https://neevgrover.com",
      label: "Website",
    },
  ];

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 px-4 text-center text-white">
        <h1 className="text-4xl md:text-5xl font-bold mb-3">About</h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto">
          Learn more about College Statistics and its creator
        </p>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* About the Project */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            About College Statistics
          </h2>
          <p className="text-gray-600 mb-4">
            College Statistics is a free tool designed to help students,
            parents, and educators explore and compare admissions data from top
            universities. Our data comes directly from official Common Data Set
            (CDS) reports, ensuring accuracy and reliability.
          </p>
          <p className="text-gray-600 mb-4">
            The Common Data Set initiative is a collaborative effort among
            colleges, publishers, and data users to improve the quality and
            accuracy of information provided to students and their families.
            Each year, participating institutions complete a standardized survey
            with data about admissions, enrollment, costs, financial aid, and
            more.
          </p>
          <p className="text-gray-600">
            We believe that access to clear, accurate college data shouldn&apos;t
            require expensive consultants or confusing government databases. Our
            goal is to make this information accessible to everyone.
          </p>
        </section>

        {/* About the Creator */}
        <section className="card p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            About the Creator
          </h2>
          <div className="flex flex-col md:flex-row gap-8">
            {/* Photo placeholder */}
            <div className="flex-shrink-0">
              <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center">
                <svg
                  className="w-16 h-16 text-gray-400"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
            </div>

            {/* Bio */}
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-800 mb-1">
                Neev Grover
              </h3>
              <p className="text-gray-500 mb-4">
                Sophomore at the Harker School
              </p>
              <p className="text-gray-600 mb-4">
                I&apos;m passionate about making information accessible and building
                tools that help people make better decisions. College Statistics
                started as a personal project to help myself and my peers
                navigate the college admissions process with better data.
              </p>
              <p className="text-gray-600 mb-6">
                When I&apos;m not coding, you can find me writing about technology on
                my blog, exploring new ideas, and working on various side
                projects.
              </p>

              {/* Social Links */}
              <div className="flex flex-wrap gap-3">
                {socialLinks.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    {link.label}
                    <svg
                      className="w-4 h-4 ml-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                  </a>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="text-center mt-8">
          <Link
            href="/contact"
            className="inline-flex items-center px-6 py-3 bg-gray-800 hover:bg-gray-900 text-white rounded-lg font-medium transition-colors"
          >
            Get in Touch
            <svg
              className="w-4 h-4 ml-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
