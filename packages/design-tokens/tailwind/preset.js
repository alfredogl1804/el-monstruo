/**
 * El Monstruo — Tailwind v3 Preset
 *
 * Para proyectos Tailwind v3.x:
 *   // tailwind.config.js
 *   module.exports = {
 *     presets: [require('@monstruo/design-tokens/tailwind/preset')],
 *     content: [...]
 *   };
 *
 * Para Tailwind v4 (recomendado, vigente al 2026-05-06): usar
 * `tailwind/theme.css` en lugar de este preset.
 *
 * NUNCA exponemos `primary`, `secondary`, `gray`. Solo `forja`, `graphite`, `acero`.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      black: "#000",
      white: "#fff",
      forja: {
        50: "#FFF4ED",
        100: "#FFE6D2",
        200: "#FFC8A0",
        300: "#FDA468",
        400: "#FB8B3C",
        500: "#F97316",
        600: "#D75D0C",
        700: "#A94609",
        800: "#7B3306",
        900: "#4D1F03",
      },
      graphite: {
        50: "#F4F3F2",
        100: "#E2E0DD",
        200: "#BFBBB5",
        300: "#8C857C",
        400: "#5A554E",
        500: "#3D3934",
        600: "#2C2925",
        700: "#1C1917",
        800: "#14110F",
        900: "#0A0807",
      },
      acero: {
        50: "#F7F7F6",
        100: "#EBEAE8",
        200: "#D2D0CD",
        300: "#BBB8B4",
        400: "#A8A29E",
        500: "#8C8682",
        600: "#6E6864",
        700: "#524C49",
        800: "#36322F",
        900: "#1A1816",
      },
      // Solo dos colores de estado (rojo forja-quemado, verde patina)
      "forja-quemado": "#C0392B",
      "patina-acero": "#2D6A4F",
    },
    fontFamily: {
      display: [
        "Bebas Neue",
        "Bebas",
        "Impact",
        "system-ui",
        "sans-serif",
      ],
      body: [
        "Inter",
        "-apple-system",
        "BlinkMacSystemFont",
        "Segoe UI",
        "Roboto",
        "Helvetica Neue",
        "Arial",
        "sans-serif",
      ],
      mono: [
        "JetBrains Mono",
        "Fira Code",
        "ui-monospace",
        "SFMono-Regular",
        "Menlo",
        "Consolas",
        "monospace",
      ],
    },
    fontSize: {
      xs: "0.75rem",
      sm: "0.875rem",
      base: "1rem",
      lg: "1.125rem",
      xl: "1.25rem",
      "2xl": "1.5rem",
      "3xl": "2rem",
      "4xl": "2.5rem",
      "5xl": "3.5rem",
      "6xl": "4.5rem",
    },
    lineHeight: {
      tight: "1.0",
      snug: "1.25",
      normal: "1.5",
      relaxed: "1.65",
      loose: "1.85",
    },
    letterSpacing: {
      tighter: "-0.04em",
      tight: "-0.02em",
      normal: "0",
      wide: "0.025em",
      wider: "0.05em",
      widest: "0.1em",
    },
    spacing: {
      0: "0",
      0.5: "0.125rem",
      1: "0.25rem",
      1.5: "0.375rem",
      2: "0.5rem",
      3: "0.75rem",
      4: "1rem",
      5: "1.25rem",
      6: "1.5rem",
      8: "2rem",
      10: "2.5rem",
      12: "3rem",
      16: "4rem",
      20: "5rem",
      24: "6rem",
      32: "8rem",
    },
    borderRadius: {
      none: "0",
      sm: "0.25rem",
      md: "0.5rem",
      lg: "0.75rem",
      xl: "1rem",
      "2xl": "1.5rem",
      full: "9999px",
    },
    boxShadow: {
      none: "0 0 0 0 transparent",
      "ember-1": "0 1px 2px 0 rgba(0, 0, 0, 0.4)",
      "ember-2":
        "0 4px 8px -2px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
      "ember-3":
        "0 12px 24px -6px rgba(0, 0, 0, 0.55), 0 6px 12px -6px rgba(0, 0, 0, 0.35)",
      brasa:
        "0 0 0 1px rgba(249, 115, 22, 0.25), 0 0 16px -4px rgba(249, 115, 22, 0.4)",
      "brasa-strong":
        "0 0 0 2px rgba(249, 115, 22, 0.55), 0 0 32px -4px rgba(249, 115, 22, 0.55)",
      "inset-tool": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.45)",
    },
    transitionDuration: {
      instant: "60ms",
      quick: "120ms",
      steady: "240ms",
      ample: "400ms",
      massive: "640ms",
      forge: "960ms",
    },
    transitionTimingFunction: {
      flat: "cubic-bezier(0, 0, 1, 1)",
      ingot: "cubic-bezier(0.16, 0.84, 0.44, 1)",
      extract: "cubic-bezier(0.55, 0, 0.84, 0.16)",
      standard: "cubic-bezier(0.4, 0, 0.2, 1)",
      spark: "cubic-bezier(0.7, 0, 0.3, 1)",
    },
    extend: {},
  },
  plugins: [],
};
