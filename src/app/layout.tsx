import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "College Comparisons - CDS Data Dashboard",
  description: "Compare colleges using Common Data Set metrics - admissions, test scores, costs, and financial aid",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light" style={{ colorScheme: "light" }}>
      <body className="min-h-screen antialiased bg-[#f5f5f5]">
        {children}
      </body>
    </html>
  );
}
