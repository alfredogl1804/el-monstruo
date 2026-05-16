import { Tour } from "@/components/onboarding/Tour";

/**
 * La Forja — página `/onboarding`.
 *
 * Sprint LA-FORJA-001 D3.1 + hardening Perplexity F-D3.1-02, -15.
 *
 * Server Component shell. La lógica del tour vive en el Client
 * Component `Tour.tsx`. Esta página solo provee layout y metadata.
 *
 * Forzamos render dinámico para que la página respete cualquier
 * cookie ya presente (no queremos prerender estático que bake un
 * estado distinto al del usuario real).
 *
 * Hardening aplicado:
 *   F-D3.1-02 + F-D3.1-15: eliminado el wrapper redundante
 *   `OnboardingFinishHandler` (que violaba Brand Engine por el
 *   sufijo `Handler` y solo encapsulaba un `router.push("/")`). El
 *   `useRouter` ahora vive dentro de `Tour.tsx` y la página le pasa
 *   `redirectTo="/"` directo.
 */
export const dynamic = "force-dynamic";

export const metadata = {
  title: "La Forja — Tour de bienvenida",
  description:
    "Conoce La Forja: el taller para diseñar sprints reales con disciplina doctrinal.",
};

export default function OnboardingPage() {
  return (
    <main className="min-h-dvh bg-graphite-900 px-4 py-12 sm:px-8 sm:py-20">
      <div className="container flex max-w-3xl flex-col gap-10">
        <header className="flex flex-col gap-3">
          <span className="font-mono text-xs uppercase tracking-[0.2em] text-forja-500">
            La Forja
          </span>
          <h1 className="text-2xl font-semibold text-graphite-50 sm:text-3xl">
            Tour de bienvenida
          </h1>
          <p className="text-sm text-acero-500">
            Siete pasos cortos. Sin floreo. Después entras a tu Dashboard.
          </p>
        </header>

        <Tour redirectTo="/" />
      </div>
    </main>
  );
}
