import Link from "next/link";
import { cookies } from "next/headers";
import { FORJA_TOUR_COOKIE_NAME } from "@/lib/onboarding/cookie";
import { FORJA_DELIVERY_LABEL, FORJA_VERSION } from "@/lib/version";

/**
 * La Forja — landing.
 * Sprint LA-FORJA-001 D3.0 + D3.1 + D3.1 hardening Perplexity F-D3.1-08, -14.
 *
 * Brand DNA: forja al rojo vivo, sin corporativismo, sin chatbot
 * amigable. Esta es una herramienta de trabajo, no una experiencia de
 * marketing.
 *
 * Server Component. Lee la cookie de tour completado para decidir si
 * el CTA primario es "Empezar tour" o "Volver a verlo".
 *
 * Hardening aplicado:
 *   F-D3.1-08: parsea el timestamp y solo lo muestra si es válido.
 *              Cookie manipulada con `zzz` ya no rinde "Invalid Date".
 *   F-D3.1-14: versión y delivery label provienen de
 *              `@/lib/version` que las lee de `package.json` y de
 *              `NEXT_PUBLIC_FORJA_DELIVERY` respectivamente, en lugar
 *              de string literal `v0.1.0 · D3.1`.
 */
export const dynamic = "force-dynamic";

function formatTourCompletedAt(raw: string | undefined): string | null {
  if (!raw) return null;
  const parsed = new Date(raw);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleString();
}

export default async function ForjaHome() {
  const cookieStore = await cookies();
  const tourCookieValue = cookieStore.get(FORJA_TOUR_COOKIE_NAME)?.value;
  const tourCompletedAt = formatTourCompletedAt(tourCookieValue);
  const tourSeen = tourCompletedAt !== null;

  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col justify-center gap-12 px-6 py-16">
      <header className="flex items-baseline gap-3">
        <span className="text-forja-500 font-mono text-xs tracking-[0.3em] uppercase">
          La Forja
        </span>
        <span className="text-graphite-500 font-mono text-xs">
          v{FORJA_VERSION} · {FORJA_DELIVERY_LABEL}
        </span>
      </header>

      <h1 className="text-graphite-100 max-w-xl text-5xl leading-tight font-semibold tracking-tight md:text-6xl">
        Donde se forjan los sprints
        <br />
        <span className="text-forja-500">del Monstruo.</span>
      </h1>

      <p className="text-acero-500 max-w-xl text-lg leading-relaxed">
        Disciplina binaria. Estados en inglés.
        <br />
        Cap de 50 USD por mes por usuario, no negociable.
        <br />
        Cinco puertas, ni una más.
      </p>

      <nav className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-8">
        <Link
          href="/onboarding"
          className="rounded-[var(--radius-forja)] bg-forja-500 px-5 py-2.5 text-center text-sm font-semibold text-graphite-900 hover:bg-forja-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-forja-300 focus-visible:ring-offset-2 focus-visible:ring-offset-graphite-900"
        >
          {tourSeen ? "Volver a ver el tour" : "Empezar tour"}
        </Link>
        <Link
          href="/salud"
          className="text-forja-500 hover:text-forja-300 font-mono text-sm uppercase tracking-widest transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-forja-300 focus-visible:ring-offset-2 focus-visible:ring-offset-graphite-900 rounded-sm"
        >
          → estado del sistema
        </Link>
      </nav>

      {tourCompletedAt && (
        <p className="font-mono text-xs text-graphite-500">
          Tour completado: {tourCompletedAt}
        </p>
      )}

      <footer className="text-graphite-500 mt-auto pt-12 font-mono text-xs">
        Sprint LA-FORJA-001 · {FORJA_DELIVERY_LABEL} onboarding tour
      </footer>
    </main>
  );
}
