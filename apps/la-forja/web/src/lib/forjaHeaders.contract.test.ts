/**
 * R-D3.2-02 + R-D3.2.1-02: Contract test backend ↔ frontend para los nombres
 * de headers SSE.
 *
 * Estrategia (R-D3.2.1-02 — pase 2 Perplexity, fix sin fs runtime):
 *
 * 1. El backend declara la fuente única en
 *    `apps/la-forja/api/src/shared/headers.ts`.
 * 2. El generador `apps/la-forja/api/scripts/generate-headers-contract.mjs`
 *    parsea ese archivo y emite `forjaHeaders.contract.json` (committed en
 *    git al lado de este test).
 * 3. Este test importa el JSON con `import` estándar (sin fs.readFileSync
 *    runtime, que rompía en CI workspace-aislado).
 * 4. Si un dev edita el backend pero olvida regenerar el JSON, el test
 *    rompe binariamente con un diff exacto.
 *
 * Comando de regeneración:
 *   pnpm --filter la-forja-api contract:headers
 */
import { describe, it, expect } from "vitest";
import {
  FORJA_TUTOR_HEADER_KEYS,
  FORJA_CITATIONS_HEADER_MAX_BYTES,
} from "./forjaHeaders";
import contract from "./forjaHeaders.contract.json";

describe("R-D3.2-02 + R-D3.2.1-02: backend ↔ frontend headers contract", () => {
  it("frontend FORJA_TUTOR_HEADER_KEYS está sincronizado byte por byte con el contrato canónico", () => {
    expect(FORJA_TUTOR_HEADER_KEYS).toEqual(contract.forjaTutorHeaderKeys);
  });

  it("frontend FORJA_CITATIONS_HEADER_MAX_BYTES está sincronizado con el contrato canónico", () => {
    expect(FORJA_CITATIONS_HEADER_MAX_BYTES).toBe(
      contract.forjaCitationsHeaderMaxBytes,
    );
  });

  it("el contrato canónico declara TODOS los headers que el frontend importa (no permite drift por omisión)", () => {
    const contractKeys = Object.keys(contract.forjaTutorHeaderKeys).sort();
    const frontendKeys = Object.keys(FORJA_TUTOR_HEADER_KEYS).sort();
    expect(frontendKeys).toEqual(contractKeys);
  });
});
