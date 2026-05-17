#!/usr/bin/env node
/**
 * R-D3.2.1-02: Genera el contrato JSON de headers SSE para que el frontend
 * lo consuma vía import estándar (sin fs.readFileSync en runtime de tests,
 * que falla en CI workspace-aislado).
 *
 * Uso:
 *   pnpm --filter la-forja-api contract:headers
 *
 * Lee apps/la-forja/api/src/shared/headers.ts (fuente única de verdad) y
 * emite apps/la-forja/web/src/lib/forjaHeaders.contract.json. El JSON queda
 * committed en git; si el dev edita el backend pero olvida regenerar, el
 * contract test fallará binariamente con un diff exacto.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const apiHeadersPath = resolve(__dirname, "../src/shared/headers.ts");
const webContractPath = resolve(
  __dirname,
  "../../web/src/lib/forjaHeaders.contract.json",
);

const src = readFileSync(apiHeadersPath, "utf-8");

// Match el bloque `export const FORJA_TUTOR_HEADER_KEYS = { ... } as const;`
const objectMatch = src.match(
  /export const FORJA_TUTOR_HEADER_KEYS\s*=\s*\{([\s\S]*?)\}\s*as const;/,
);
if (!objectMatch) {
  console.error(
    "[la-forja:contract_gen] no se pudo parsear FORJA_TUTOR_HEADER_KEYS",
  );
  process.exit(1);
}
const body = objectMatch[1] ?? "";

// Match líneas tipo `key: "value",` (ignora JSDoc /** ... */)
const entryRe = /^\s*([a-zA-Z][a-zA-Z0-9]*)\s*:\s*"([^"]+)"/gm;
const headers = {};
let m;
while ((m = entryRe.exec(body)) !== null) {
  const key = m[1];
  const value = m[2];
  if (key && value) headers[key] = value;
}

if (Object.keys(headers).length === 0) {
  console.error(
    "[la-forja:contract_gen] no se extrajo ninguna clave del backend",
  );
  process.exit(1);
}

// Match cap bytes
const capMatch = src.match(
  /export const FORJA_CITATIONS_HEADER_MAX_BYTES\s*=\s*(\d+)\s*;/,
);
const capBytes = capMatch ? Number.parseInt(capMatch[1] ?? "0", 10) : null;
if (!capBytes || Number.isNaN(capBytes)) {
  console.error(
    "[la-forja:contract_gen] no se pudo parsear FORJA_CITATIONS_HEADER_MAX_BYTES",
  );
  process.exit(1);
}

const contract = {
  $schema:
    "https://github.com/alfredogl1804/el-monstruo/apps/la-forja/api/scripts/generate-headers-contract.mjs",
  $generated: "do not edit by hand — run pnpm contract:headers to regenerate",
  forjaTutorHeaderKeys: headers,
  forjaCitationsHeaderMaxBytes: capBytes,
};

writeFileSync(webContractPath, JSON.stringify(contract, null, 2) + "\n");
console.log(
  `[la-forja:contract_gen] OK ${webContractPath} (${
    Object.keys(headers).length
  } headers, cap=${capBytes}B)`,
);
