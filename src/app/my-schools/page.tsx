import { redirect } from "next/navigation";
import SavedSchoolsDashboard from "@/components/SavedSchoolsDashboard";
import { getSession } from "@/lib/auth";

export const metadata = {
  title: "My Schools – College Statistics",
  robots: { index: false, follow: false },
};

export default async function MySchoolsPage() {
  const session = await getSession();
  if (!session) {
    redirect("/");
  }

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      <SavedSchoolsDashboard />
    </div>
  );
}
