/**
 * La Forja — fuente única de versión y delivery label.
 *
 * Sprint LA-FORJA-001 D3.1 hardening Perplexity F-D3.1-14.
 *
 * Antes: el header del landing decía `v0.1.0 · D3.1` hard-coded en
 * JSX. Cualquier bump de versión o cambio de delivery quedaba a la
 * disciplina manual del agente. Cuando D3.2 llegue, el label seguiría
 * mintiendo.
 *
 * Ahora:
 *   - `FORJA_VERSION` se importa de `package.json` (resuelto en
 *     build por bundler con `resolveJsonModule: true`).
 *   - `FORJA_DELIVERY_LABEL` se lee de `NEXT_PUBLIC_FORJA_DELIVERY`,
 *     con fallback explícito al delivery actual cuando la variable
 *     no está seteada (dev local sin .env). Fallback es fail-safe,
 *     no fail-loud, porque D3.x es un label informativo del header,
 *     no una credencial.
 */

import pkg from "../../package.json" with { type: "json" };

export const FORJA_VERSION: string = pkg.version;

const DELIVERY_FALLBACK = "D3.1";

export const FORJA_DELIVERY_LABEL: string =
  process.env.NEXT_PUBLIC_FORJA_DELIVERY ?? DELIVERY_FALLBACK;
