/** @type {import('next').NextConfig} */

const API_ORIGIN = process.env.TWIN_API_ORIGIN || "http://127.0.0.1:8011";
const STATIC_EXPORT = process.env.STATIC_EXPORT === "1";
const BASE_PATH = process.env.NEXT_BASE_PATH || "";

const nextConfig = {
  reactStrictMode: true,
  // Static Pages builds must not replace the .next directory the live server is running.
  distDir: STATIC_EXPORT ? ".next-export" : ".next",
  ...(STATIC_EXPORT
    ? {
        output: "export",
        trailingSlash: true,
        images: { unoptimized: true },
        ...(BASE_PATH ? { basePath: BASE_PATH, assetPrefix: BASE_PATH } : {}),
      }
    : {
        async rewrites() {
          return [
            { source: "/twin-api/:path*", destination: `${API_ORIGIN}/:path*` },
            { source: "/visits/:path*", destination: `${API_ORIGIN}/visits/:path*` },
            { source: "/pitch", destination: "/pitch/index.html" },
            { source: "/pitch/", destination: "/pitch/index.html" },
          ];
        },
      }),
};

module.exports = nextConfig;
