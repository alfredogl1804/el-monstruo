import next from "eslint-config-next";

/**
 * La Forja — ESLint flat config (Next 16 + ESLint 9).
 * Hereda eslint-config-next y agrega un guard de Brand Naming
 * (Regla Dura #4 + Brand Engine).
 *
 * Nota D3.0 hardening (F-D3.0-02): `eslint-config-next@16` exporta un
 * array de configs (no función). Spread directo, sin invocar.
 *
 * Nota D3.0 hardening (F-D3.0-09): el regex anterior solo bloqueaba
 * identificadores literalmente iguales a `Service|Handler|Util|Helper|
 * Misc|Manager`. Ahora usa `\\b...\\b` para detectar el sufijo en
 * compuestos como `UserService`, `AuthHandler`, `CacheManager`.
 */
const config = [
  ...next,
  {
    rules: {
      "id-match": [
        "error",
        "^(?!.*\\b(?:Service|Handler|Util|Helper|Misc|Manager)\\b).+$",
        { properties: false, classFields: true },
      ],
    },
  },
  {
    ignores: [".next/**", "node_modules/**", "dist/**", "out/**"],
  },
];

export default config;
