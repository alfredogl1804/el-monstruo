/**
 * La Forja — /tutor page (D3.2 SSE).
 *
 * Sprint LA-FORJA-001 D3.2.
 * Doctrina:
 *   - Server Component shell que pasa NEXT_PUBLIC_API_URL al Client Component.
 *   - Brand DNA: cabecera mono con namespace `la-forja`, sin sidebar
 *     corporativo. La página entera es la conversación.
 *
 * No usa cookies de tour ni gates de onboarding — el tutor es accesible
 * directamente para que el usuario forje sin fricción.
 */

import { loadForjaWebEnv } from "@/lib/env";
import { Chat } from "@/components/tutor/Chat";

export const dynamic = "force-dynamic";

export default function TutorPage() {
  const env = loadForjaWebEnv();
  return (
    <main className="mx-auto flex h-dvh max-w-4xl flex-col gap-6 px-6 py-8">
      <header className="flex items-baseline justify-between border-b border-acero-700 pb-3">
        <div className="flex items-baseline gap-3">
          <span className="text-forja-500 font-mono text-xs tracking-[0.3em] uppercase">
            La Forja
          </span>
          <span className="text-graphite-500 font-mono text-xs">
            tutor adaptativo
          </span>
        </div>
        <span className="text-acero-500 font-mono text-[10px] uppercase tracking-[0.25em]">
          DSC-LF-005 · SSE v1
        </span>
      </header>
      <div className="flex-1 min-h-0">
        <Chat apiUrl={env.NEXT_PUBLIC_API_URL} />
      </div>
    </main>
  );
}
