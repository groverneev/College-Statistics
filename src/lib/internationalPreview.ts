import { createHmac, timingSafeEqual } from "node:crypto";
import { INTERNATIONAL_PREVIEW_SLUG } from "@/lib/internationalPreviewConfig";

export const INTERNATIONAL_PREVIEW_COOKIE = "college-statistics-international-preview";
export const INTERNATIONAL_PREVIEW_MAX_AGE = 60 * 60 * 24 * 365;

export function getInternationalPreviewToken(password: string) {
  return createHmac("sha256", password)
    .update(INTERNATIONAL_PREVIEW_SLUG)
    .digest("hex");
}

export function matchesInternationalPreviewPassword(
  suppliedPassword: string,
  expectedPassword: string,
) {
  const supplied = Buffer.from(suppliedPassword);
  const expected = Buffer.from(expectedPassword);
  return supplied.length === expected.length && timingSafeEqual(supplied, expected);
}
