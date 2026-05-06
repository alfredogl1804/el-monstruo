/**
 * El Monstruo — Tokens de Color Canónicos
 *
 * Espejo TS de `kernel/brand/brand_dna.py` BRAND_DNA["visual"].
 * Paleta canónica firmada en DSC-MO-002:
 *   - forja    = #F97316  (Naranja Forja, primario, llama)
 *   - graphite = #1C1917  (Graphite oscuro, fondo, metal templado)
 *   - acero    = #A8A29E  (Acero, neutro medio, herramienta)
 *
 * Naming inviolable (DSC-G-004): NUNCA `primary`, `secondary`, `gray`, `dark`.
 * SIEMPRE `forja-500`, `graphite-700`, `acero-300`.
 *
 * Las escalas 50-900 derivan de cada hex base usando un algoritmo de
 * mezcla con blanco/negro y son verificables con `tests/scale_consistency.test.js`.
 */

// ── Paleta base (source of truth) ────────────────────────────────────
export const FORJA_BASE = "#F97316" as const;
export const GRAPHITE_BASE = "#1C1917" as const;
export const ACERO_BASE = "#A8A29E" as const;

// ── Escala forja (Naranja Forja) ─────────────────────────────────────
// 500 es el hex canónico del Brand DNA; ramas hacia tonos más claros
// (mezcla con blanco) y más oscuros (mezcla con graphite).
export const forja = {
  50: "#FFF4ED",
  100: "#FFE6D2",
  200: "#FFC8A0",
  300: "#FDA468",
  400: "#FB8B3C",
  500: "#F97316", // ← Brand DNA canónico
  600: "#D75D0C",
  700: "#A94609",
  800: "#7B3306",
  900: "#4D1F03",
} as const;

// ── Escala graphite (Graphite oscuro / Metal templado) ───────────────
// 900 es el más profundo (background absoluto); 50 tiende al humo claro.
export const graphite = {
  50: "#F4F3F2",
  100: "#E2E0DD",
  200: "#BFBBB5",
  300: "#8C857C",
  400: "#5A554E",
  500: "#3D3934",
  600: "#2C2925",
  700: "#1C1917", // ← Brand DNA canónico (background)
  800: "#14110F",
  900: "#0A0807",
} as const;

// ── Escala acero (Acero / Neutro medio / Herramienta) ────────────────
// 500 es el hex canónico del Brand DNA.
export const acero = {
  50: "#F7F7F6",
  100: "#EBEAE8",
  200: "#D2D0CD",
  300: "#BBB8B4",
  400: "#A8A29E", // ← Brand DNA canónico
  500: "#8C8682",
  600: "#6E6864",
  700: "#524C49",
  800: "#36322F",
  900: "#1A1816",
} as const;

// ── Tokens semánticos (siempre apuntan a la escala canónica) ─────────
// Se usan en componentes para no hardcodear `forja-500` en cada lugar.
export const semantic = {
  // Texto principal sobre fondo graphite-700
  "text-default": acero[100],
  "text-soft": acero[300],
  "text-muted": acero[500],
  // Texto sobre forja (botones, CTAs)
  "text-on-forja": graphite[800],
  // Backgrounds del Monstruo
  "bg-canvas": graphite[700],
  "bg-elevated": graphite[600],
  "bg-recessed": graphite[800],
  // Bordes
  "border-default": graphite[500],
  "border-strong": graphite[400],
  "border-forja": forja[500],
  // Estados
  "state-action": forja[500],
  "state-action-hover": forja[400],
  "state-action-pressed": forja[600],
  // Errores con identidad de marca
  "state-error": "#C0392B", // rojo forja-quemado, complementario
  "state-success": "#2D6A4F", // verde patina sobre acero
  "state-warn": forja[300], // ámbar de forja viva
} as const;

// ── Anti-patrón guard (export de los nombres prohibidos) ─────────────
// Si alguien intenta importar `primary` o `secondary` desde este módulo,
// se rompe en tiempo de typecheck. Documenta el contrato.
export const FORBIDDEN_NAMES = [
  "primary",
  "secondary",
  "tertiary",
  "gray",
  "grey",
  "dark",
  "light",
  "muted-base",
  "accent-1",
  "accent-2",
] as const;

// ── Type exports ─────────────────────────────────────────────────────
export type ForjaScale = keyof typeof forja;
export type GraphiteScale = keyof typeof graphite;
export type AceroScale = keyof typeof acero;
export type SemanticToken = keyof typeof semantic;

// ── Utility: obtener token por path canónico ─────────────────────────
export function getColor(path: string): string {
  // Acepta "forja.500" o "graphite-700" o "semantic.text-default"
  const normalized = path.replace("-", ".").split(".");
  const tables: Record<string, Record<string, string>> = {
    forja: forja as unknown as Record<string, string>,
    graphite: graphite as unknown as Record<string, string>,
    acero: acero as unknown as Record<string, string>,
    semantic: semantic as unknown as Record<string, string>,
  };
  const family = normalized[0];
  const key = normalized.slice(1).join("-");
  if (!tables[family]) {
    throw new Error(
      `tokens_color_get_unknown_family: '${family}' no es forja|graphite|acero|semantic`,
    );
  }
  const value = tables[family][key];
  if (!value) {
    throw new Error(
      `tokens_color_get_unknown_step: '${key}' no existe en escala '${family}'`,
    );
  }
  return value;
}
