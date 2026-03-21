import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@encypher/design-system"],
  images: {
    unoptimized: true,
  },
  output: "export",
};

export default nextConfig;
