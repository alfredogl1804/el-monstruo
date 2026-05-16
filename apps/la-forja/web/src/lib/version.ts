/**
 * La Forja — fuente única de versión y delivery label.
 *
 * Sprint LA-FORJA-001 D3.1 hardening Perplexity F-D3.1-14
 * + D3.1.1 R-D3.1-01 (regression): el fallback hardcoded "D3.1"
 * reintroducía el defecto que F-14 prometía cerrar — cuando D3.2
 * llegue, el label seguiría diciendo "D3.1" sin la env seteada.
 *
 * Doctrina:
 *   - FORJA_VERSION viene de package.json (resuelto en build con
 *     resolveJsonModule: true).
 *   - FORJA_DELIVERY_LABEL viene de NEXT_PUBLIC_FORJA_DELIVERY como
 *     única fuente de verdad. Sin fallback. Si la env no está
 *     seteada o está vacía, throw inmediato (Regla Dura #6 fail-loud).
 *
 * En dev local, el valor se setea en .env.local (ver .env.local.example).
 * En producción, viene del pipeline de build de Manus/Vercel/Cloud Run.
 *
 * Si esto rompe un build futuro, es la señal correcta: la disciplina
 * de bumpear la env por delivery se hace explícita.
 */

import pkg from "../../package.json" with { type: "json" };

export const FORJA_VERSION: string = pkg.version;

const rawDelivery = process.env.NEXT_PUBLIC_FORJA_DELIVERY;
if (typeof rawDelivery !== "string" || rawDelivery.trim().length === 0) {
  throw new Error(
    "[la-forja:web_missing_env] NEXT_PUBLIC_FORJA_DELIVERY no seteada. " +
      "Setear en .env.local (dev) o build env (prod). Ver .env.local.example.",
  );
}

export const FORJA_DELIVERY_LABEL: string = rawDelivery.trim();
