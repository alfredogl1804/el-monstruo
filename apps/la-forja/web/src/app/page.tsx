import Link from "next/link";

/**
 * La Forja — landing.
 * Sprint LA-FORJA-001 D3.0.
 *
 * Brand DNA: forja al rojo vivo, sin corporativismo, sin chatbot amigable.
 * Esta es una herramienta de trabajo, no una experiencia de marketing.
 */
export default function ForjaHome() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col justify-center gap-12 px-6 py-16">
      <header className="flex items-baseline gap-3">
        <span className="text-forja-500 font-mono text-xs tracking-[0.3em] uppercase">
          La Forja
        </span>
        <span className="text-graphite-500 font-mono text-xs">
          v0.1.0 · D3.0
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

      <nav className="flex gap-6">
        <Link
          href="/salud"
          className="text-forja-500 hover:text-forja-300 font-mono text-sm uppercase tracking-widest transition-colors"
        >
          → estado del sistema
        </Link>
      </nav>

      <footer className="text-graphite-500 mt-auto pt-12 font-mono text-xs">
        Sprint LA-FORJA-001 · D3.0 scaffold
      </footer>
    </main>
  );
}
