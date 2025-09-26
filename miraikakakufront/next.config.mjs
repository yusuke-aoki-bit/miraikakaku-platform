/** @type {import("next").NextConfig} */
const nextConfig = {
    output: "standalone",
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://miraikakaku-api-zbaru5v7za-uc.a.run.app"
    },
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/:path*"
            }
        ];
    }
};

export default nextConfig;
