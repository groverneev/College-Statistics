import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Only use static export for production builds
  output: process.env.NODE_ENV === "production" ? "export" : undefined,
};

export default nextConfig;
