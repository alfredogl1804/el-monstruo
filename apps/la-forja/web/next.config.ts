import type { NextConfig } from "next";

/**
 * La Forja — Next.js 16.2.6 config.
 * Sprint LA-FORJA-001 D3.0.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  // El frontend NUNCA habla con Supabase directo (LF-1 + RLS-aware).
  // Toda data viaja vía el backend Hono en `apps/la-forja/api`.
  // En dev local, NEXT_PUBLIC_API_URL apunta a http://localhost:3000.
  // En producción, apunta a https://la-forja-api.up.railway.app.
};

export default nextConfig;
