import { pageMetadata } from "@/lib/seo";

// The contact page is a client component, so its metadata lives here.
export const metadata = pageMetadata({
  title: "Contact – College Statistics",
  description:
    "Questions, feedback, or suggestions about College Statistics? Get in touch.",
  path: "/contact",
});

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return children;
}
