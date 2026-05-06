/**
 * El Monstruo — Tokens de Shadow / Elevación
 *
 * Filosofía: las sombras del Monstruo no son neblina sutil — son
 * emanaciones de forja (resplandor anaranjado tenue) sobre graphite.
 * Capas de elevación discretas (3 pasos), no continuas.
 *
 * Naming: "ember-1" / "ember-2" / "ember-3" en lugar de elevation-1/2/3.
 */

// Sombras genéricas (caja oscura sobre graphite)
export const shadow = {
  none: "0 0 0 0 transparent",
  // Capa baja — botón en estado normal
  "ember-1": "0 1px 2px 0 rgba(0, 0, 0, 0.4)",
  // Capa media — card flotante, popover
  "ember-2": "0 4px 8px -2px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
  // Capa alta — modal, dropdown abierto
  "ember-3":
    "0 12px 24px -6px rgba(0, 0, 0, 0.55), 0 6px 12px -6px rgba(0, 0, 0, 0.35)",
  // Brasa — resplandor forja sutil (estados activos, focus rings)
  brasa:
    "0 0 0 1px rgba(249, 115, 22, 0.25), 0 0 16px -4px rgba(249, 115, 22, 0.4)",
  // Brasa-fuerte — focus-visible, drag activo
  "brasa-strong":
    "0 0 0 2px rgba(249, 115, 22, 0.55), 0 0 32px -4px rgba(249, 115, 22, 0.55)",
  // Inset — recessed surfaces (input field hundido)
  "inset-tool": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.45)",
} as const;

export type ShadowToken = keyof typeof shadow;
