import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  skipTrailingSlashRedirect: true,

  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**", pathname: "/**" },
      { protocol: "http", hostname: "localhost", pathname: "/**" },
      { protocol: "http", hostname: "127.0.0.1", pathname: "/**" },
    ],
  },

  // ─── Django API Proxy ──────────────────────────────────────────────────────
  // Browser calls /django-api/... → Next.js rewrites to Django backend
  // Works in dev AND production — no env changes needed after deploy
  async rewrites() {
    const djangoBase =
      process.env.API_ORIGIN ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000/api/v1";
    const origin = djangoBase.replace(/\/api\/v1\/?$/, "");
    return [
      {
        source: "/django-api/:path*",
        destination: `${origin}/api/v1/:path*`,
      },
    ];
  },

  async headers() {
    const corsOrigin = process.env.CORS_ORIGIN ?? "http://localhost:3000";
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Credentials", value: "true" },
          { key: "Access-Control-Allow-Origin", value: corsOrigin },
          { key: "Access-Control-Allow-Methods", value: "GET,POST,PUT,PATCH,DELETE,OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Content-Type, Authorization" },
        ],
      },
    ];
  },
};

export default nextConfig;
