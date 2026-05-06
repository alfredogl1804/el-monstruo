// Test de paridad: kernel/brand/brand_dna.py ←→ packages/design-tokens
//
// Source of truth: kernel/brand/brand_dna.py (BRAND_DNA["visual"]).
// Este test verifica que los hex canónicos en TS/CSS/Tailwind/Flutter
// coincidan con los del kernel. Si alguien cambia un hex en un solo lugar,
// el test rompe y se obliga a sincronizar.
//
// Run: node --test tests/parity_with_brand_dna.test.js

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = join(__dirname, "..", "..", "..");

// ── Hex canónicos firmados en BRAND_DNA["visual"] ──────────────────
// (Hard-codeados aquí para no necesitar parser Python en el test;
//  si cambia algo en brand_dna.py hay que actualizar también aquí
//  o el test rompe.)
const BRAND_DNA_HEX = {
  primary: "#F97316", // forja-500
  background: "#1C1917", // graphite-700
  accent: "#A8A29E", // acero-400
};

// ── Test 1: kernel/brand/brand_dna.py contiene los hex esperados ──
test("kernel/brand/brand_dna.py declara los hex canónicos", () => {
  const brandDnaPy = readFileSync(
    join(REPO_ROOT, "kernel", "brand", "brand_dna.py"),
    "utf8",
  );
  for (const [key, hex] of Object.entries(BRAND_DNA_HEX)) {
    assert.ok(
      brandDnaPy.includes(hex),
      `tokens_parity_kernel_missing: kernel/brand/brand_dna.py NO contiene ${hex} (esperado para "${key}")`,
    );
  }
});

// ── Test 2: src/colors.ts usa los hex canónicos ───────────────────
test("packages/design-tokens/src/colors.ts usa los hex canónicos", () => {
  const colorsTs = readFileSync(
    join(REPO_ROOT, "packages", "design-tokens", "src", "colors.ts"),
    "utf8",
  );
  // forja-500 debe ser exactamente F97316
  assert.match(
    colorsTs,
    /500:\s*"#F97316"/,
    "tokens_parity_ts_forja_500_mismatch: forja[500] no es #F97316",
  );
  // graphite-700 debe ser 1C1917
  assert.match(
    colorsTs,
    /700:\s*"#1C1917"/,
    "tokens_parity_ts_graphite_700_mismatch: graphite[700] no es #1C1917",
  );
  // acero-400 debe ser A8A29E
  assert.match(
    colorsTs,
    /400:\s*"#A8A29E"/,
    "tokens_parity_ts_acero_400_mismatch: acero[400] no es #A8A29E",
  );
});

// ── Test 3: css/tokens.css declara los hex canónicos ──────────────
test("packages/design-tokens/css/tokens.css declara los hex canónicos", () => {
  const tokensCss = readFileSync(
    join(REPO_ROOT, "packages", "design-tokens", "css", "tokens.css"),
    "utf8",
  );
  assert.match(
    tokensCss,
    /--color-forja-500:\s*#F97316/,
    "tokens_parity_css_forja_500_mismatch",
  );
  assert.match(
    tokensCss,
    /--color-graphite-700:\s*#1C1917/,
    "tokens_parity_css_graphite_700_mismatch",
  );
  assert.match(
    tokensCss,
    /--color-acero-400:\s*#A8A29E/,
    "tokens_parity_css_acero_400_mismatch",
  );
});

// ── Test 4: tailwind/preset.js (v3) usa los hex canónicos ─────────
test("tailwind/preset.js (v3) usa los hex canónicos", () => {
  const preset = readFileSync(
    join(REPO_ROOT, "packages", "design-tokens", "tailwind", "preset.js"),
    "utf8",
  );
  assert.match(
    preset,
    /500:\s*"#F97316"/,
    "tokens_parity_tw_v3_forja_500_mismatch",
  );
  assert.match(
    preset,
    /700:\s*"#1C1917"/,
    "tokens_parity_tw_v3_graphite_700_mismatch",
  );
});

// ── Test 5: tailwind/theme.css (v4) usa los hex canónicos ─────────
test("tailwind/theme.css (v4) usa los hex canónicos", () => {
  const themeCss = readFileSync(
    join(REPO_ROOT, "packages", "design-tokens", "tailwind", "theme.css"),
    "utf8",
  );
  assert.match(
    themeCss,
    /--color-forja-500:\s*#F97316/,
    "tokens_parity_tw_v4_forja_500_mismatch",
  );
});

// ── Test 6: flutter/monstruo_tokens.dart usa los hex canónicos ────
test("flutter/monstruo_tokens.dart usa los hex canónicos", () => {
  const flutterTokens = readFileSync(
    join(
      REPO_ROOT,
      "packages",
      "design-tokens",
      "flutter",
      "monstruo_tokens.dart",
    ),
    "utf8",
  );
  assert.match(
    flutterTokens,
    /500:\s*Color\(0xFFF97316\)/,
    "tokens_parity_flutter_forja_500_mismatch",
  );
  assert.match(
    flutterTokens,
    /700:\s*Color\(0xFF1C1917\)/,
    "tokens_parity_flutter_graphite_700_mismatch",
  );
});

// ── Test 7: anti-anti-patrón — naming prohibido NO aparece ────────
test("ningún archivo del package usa naming prohibido (primary/secondary/gray)", () => {
  const files = [
    "src/colors.ts",
    "src/typography.ts",
    "css/tokens.css",
    "tailwind/preset.js",
    "tailwind/theme.css",
  ];
  // Patrones específicos que indican naming genérico (no falsos positivos
  // como "primary scale" en comentarios). Buscamos definiciones reales.
  const forbiddenPatterns = [
    /--color-primary[:\s-]/,
    /--color-secondary[:\s-]/,
    /--color-gray-/,
    /^\s*primary\s*:\s*[{"]/m,
    /^\s*secondary\s*:\s*[{"]/m,
    /^\s*gray\s*:/m,
  ];

  for (const relPath of files) {
    const content = readFileSync(
      join(REPO_ROOT, "packages", "design-tokens", relPath),
      "utf8",
    );
    for (const pattern of forbiddenPatterns) {
      const match = content.match(pattern);
      assert.ok(
        !match,
        `tokens_brand_dna_violation: ${relPath} contiene naming prohibido (${pattern}) — primary/secondary/gray están vetados por DSC-G-004`,
      );
    }
  }
});

// ── Test 8: paquete declara correctamente metadata Monstruo ───────
test("package.json declara metadata canónica del Monstruo", () => {
  const pkg = JSON.parse(
    readFileSync(
      join(REPO_ROOT, "packages", "design-tokens", "package.json"),
      "utf8",
    ),
  );
  assert.equal(pkg.name, "@monstruo/design-tokens");
  assert.deepEqual(pkg.monstruo.canonical_palette, ["forja", "graphite", "acero"]);
  assert.equal(pkg.monstruo.source_of_truth, "kernel/brand/brand_dna.py");
  assert.ok(pkg.monstruo.forbidden_naming.includes("primary"));
  assert.ok(pkg.monstruo.forbidden_naming.includes("secondary"));
  assert.ok(pkg.monstruo.forbidden_naming.includes("gray"));
});
