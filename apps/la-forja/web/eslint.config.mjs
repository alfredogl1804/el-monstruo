import next from "eslint-config-next";

/**
 * La Forja — ESLint flat config (Next 16 + ESLint 9).
 * Hereda eslint-config-next y agrega un guard de Brand Naming
 * (Regla Dura #4 + Brand Engine).
 */
export default [
  ...next(),
  {
    rules: {
      // Brand Engine: prohibir nombres genéricos en module/component identifiers.
      // (Detección heurística — el audit Cowork verifica binariamente.)
      "id-match": [
        "warn",
        "^(?!(Service|Handler|Util|Helper|Misc|Manager)$).+",
        { properties: false, classFields: true },
      ],
    },
  },
  {
    ignores: [".next/**", "node_modules/**", "dist/**", "out/**"],
  },
];
