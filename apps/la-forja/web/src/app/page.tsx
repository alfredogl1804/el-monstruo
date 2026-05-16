import Link from "next/link";
import { cookies } from "next/headers";
import { FORJA_TOUR_COOKIE_NAME } from "@/lib/onboarding/cookie";

/**
 * La Forja — landing.
 * Sprint LA-FORJA-001 D3.0 + D3.1 (tour CTA cookie-aware).
 *
 * Brand DNA: forja al rojo vivo, sin corporativismo, sin chatbot
 * amigable. Esta es una herramienta de trabajo, no una experiencia de
 * marketing.
 *
 * Server Component. Lee la cookie de tour completado para decidir si
 * el CTA primario es "Empezar tour" o "Volver a verlo".
 */
export const dynamic = "force-dynamic";

export default async function ForjaHome() {
  const cookieStore = await cookies();
  const tourCompleted = cookieStore.get(FORJA_TOUR_COOKIE_NAME)?.value;

  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col justify-center gap-12 px-6 py-16">
      <header className="flex items-baseline gap-3">
        <span className="text-forja-500 font-mono text-xs tracking-[0.3em] uppercase">
          La Forja
        </span>
        <span className="text-graphite-500 font-mono text-xs">
          v0.1.0 · D3.1
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
          className="rounded-[var(--radius-forja)] bg-forja-500 px-5 py-2.5 text-center text-sm font-semibold text-graphite-900 hover:bg-forja-400 focus:outline-none focus:ring-2 focus:ring-forja-300 focus:ring-offset-2 focus:ring-offset-graphite-900"
        >
          {tourCompleted ? "Volver a ver el tour" : "Empezar tour"}
        </Link>
        <Link
          href="/salud"
          className="text-forja-500 hover:text-forja-300 font-mono text-sm uppercase tracking-widest transition-colors"
        >
          → estado del sistema
        </Link>
      </nav>

      {tourCompleted && (
        <p className="font-mono text-xs text-graphite-500">
          Tour completado: {new Date(tourCompleted).toLocaleString()}
        </p>
      )}

      <footer className="text-graphite-500 mt-auto pt-12 font-mono text-xs">
        Sprint LA-FORJA-001 · D3.1 onboarding tour
      </footer>
    </main>
  );
}
