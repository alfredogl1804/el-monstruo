/**
 * R-D3.2-02: Contract test backend ↔ frontend para los nombres de headers SSE.
 *
 * Lee el archivo fuente del backend (`apps/la-forja/api/src/shared/headers.ts`)
 * con fs.readFileSync, parsea sus claves del objeto literal y las compara con
 * el espejo del frontend (`forjaHeaders.ts`). Si una clave o valor difiere,
 * el test rompe binariamente y pinta exactamente cuál header está en drift.
 *
 * Esto cierra el riesgo identificado por Perplexity D3.2-PASS-1: el frontend
 * leía `x-la-forja-citations` mientras el backend emitía `x-la-forja-citations`
 * pero ambos podían divergir sin que ningún test lo detectara.
 */
import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { FORJA_TUTOR_HEADER_KEYS } from "./forjaHeaders";

function parseBackendKeys(): Record<string, string> {
  const apiHeadersPath = resolve(
    __dirname,
    "../../../api/src/shared/headers.ts",
  );
  const src = readFileSync(apiHeadersPath, "utf-8");
  const objectMatch = src.match(
    /export const FORJA_TUTOR_HEADER_KEYS\s*=\s*\{([\s\S]*?)\}\s*as const;/,
  );
  if (!objectMatch) {
    throw new Error(
      "[la-forja:contract_test] no se pudo parsear FORJA_TUTOR_HEADER_KEYS del backend",
    );
  }
  const body = objectMatch[1] ?? "";
  const out: Record<string, string> = {};
  // Match líneas tipo `key: "value",` (ignora comentarios JSDoc y bloques).
  const entryRe = /^\s*([a-zA-Z][a-zA-Z0-9]*)\s*:\s*"([^"]+)"/gm;
  let m: RegExpExecArray | null;
  while ((m = entryRe.exec(body)) !== null) {
    const key = m[1];
    const value = m[2];
    if (key && value) {
      out[key] = value;
    }
  }
  return out;
}

describe("R-D3.2-02: backend ↔ frontend headers contract", () => {
  it("FORJA_TUTOR_HEADER_KEYS está sincronizado byte por byte entre api y web", () => {
    const backendKeys = parseBackendKeys();
    expect(Object.keys(backendKeys).sort()).toEqual(
      Object.keys(FORJA_TUTOR_HEADER_KEYS).sort(),
    );
    for (const [k, v] of Object.entries(FORJA_TUTOR_HEADER_KEYS)) {
      const backendValue = backendKeys[k];
      expect(backendValue, `Backend header key '${k}' missing`).toBeDefined();
      expect(backendValue).toBe(v);
    }
  });
});
