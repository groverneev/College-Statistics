import type { Metadata } from "next";
import "./globals.css";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import { NotesProvider } from "@/components/NotesContext";
import { SavedSchoolsProvider } from "@/components/SavedSchoolsContext";
import { searchableSchools } from "@/data/schools";
import { SITE_NAME, SITE_URL } from "@/lib/seo";
import { Analytics } from "@vercel/analytics/next";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "College Statistics - Compare University Data",
  description:
    "Compare university admissions data, test scores, costs, and financial aid across top colleges using official Common Data Set reports.",
  applicationName: SITE_NAME,
  openGraph: {
    siteName: SITE_NAME,
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light" style={{ colorScheme: "light" }}>
      <body className="min-h-screen antialiased bg-[#f5f5f5] flex flex-col">
        <SavedSchoolsProvider>
          <NotesProvider>
            <Header schools={searchableSchools} />
            <main className="flex-1 pt-16">{children}</main>
            <Footer />
          </NotesProvider>
        </SavedSchoolsProvider>
        <Analytics />
      </body>
    </html>
  );
}
