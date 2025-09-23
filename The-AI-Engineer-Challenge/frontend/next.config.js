/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig
