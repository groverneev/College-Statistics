import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import SessionWrapper from "@/components/SessionWrapper";
import { SavedSchoolsProvider } from "@/components/SavedSchoolsContext";
import { NotesProvider } from "@/components/NotesContext";
import { getSession, getSavedSchoolsForUser } from "@/lib/savedSchools";
import { getNotesForUser } from "@/lib/notes";

export const metadata: Metadata = {
  title: "College Statistics - Compare University Data",
  description:
    "Compare university admissions data, test scores, costs, and financial aid across top colleges using official Common Data Set reports.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await getSession();

  const [initialSavedSchools, initialNotes] = session?.user?.id
    ? await Promise.all([
        getSavedSchoolsForUser(session.user.id),
        getNotesForUser(session.user.id),
      ])
    : [[], []];

  return (
    <html lang="en" className="light" style={{ colorScheme: "light" }}>
      <body className="min-h-screen antialiased bg-[#f5f5f5] flex flex-col">
        <SessionWrapper session={session}>
          <SavedSchoolsProvider
            initialSavedSchools={initialSavedSchools}
            isLoggedIn={!!session}
          >
            <NotesProvider initialNotes={initialNotes} isLoggedIn={!!session}>
              <Header />
              <main className="flex-1 pt-16">{children}</main>
              <Footer />
            </NotesProvider>
          </SavedSchoolsProvider>
        </SessionWrapper>
      </body>
    </html>
  );
}
