import { internationalEnrollmentStoryData } from "@/data/trends/international-enrollment/data";
import InternationalEnrollmentStoryClient from "./InternationalEnrollmentStoryClient";

// Server wrapper: the rows are computed from every school's JSON at build time,
// so only the finished rows (not the school data) are sent to the browser.
export default function InternationalEnrollmentStory() {
  return <InternationalEnrollmentStoryClient story={internationalEnrollmentStoryData} />;
}
