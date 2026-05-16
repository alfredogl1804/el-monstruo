import { defineConfig } from "vitest/config";
import path from "node:path";

/**
 * La Forja — vitest config (frontend).
 * Sprint LA-FORJA-001 D3.0.
 */
export default defineConfig({
  test: {
    environment: "happy-dom",
    globals: false,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
});
