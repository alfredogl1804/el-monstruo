import next from "eslint-config-next";

/**
 * La Forja — ESLint flat config (Next 16 + ESLint 9).
 * Hereda eslint-config-next y agrega un guard de Brand Naming
 * (Regla Dura #4 + Brand Engine).
 *
 * Nota D3.0 hardening (F-D3.0-02): `eslint-config-next@16` exporta un
 * array de configs (no función). Spread directo, sin invocar.
 *
 * Nota D3.0 hardening (F-D3.0-09): regex con `\\b...\\b`. INSUFICIENTE.
 * Nota D3.1 hardening (F-D3.1-01, Perplexity): la regex anterior
 * dejaba pasar `UserService`, `AuthHandler`, `OnboardingFinishHandler`
 * porque `\\b` matchea entre minúscula y mayúscula. Verificado:
 *   /^(?!.*\\b(?:...)\\b).+$/.test('UserService') === true (ERROR)
 *
 * Nueva regex: rechaza si la palabra prohibida aparece como sufijo
 * antes de mayúscula o fin de string, o como sufijo precedido por
 * minúscula. Casos cubiertos:
 *   UserService            → reject (sufijo + EOS)
 *   OnboardingFinishHandler→ reject (idem)
 *   ServiceWorker          → reject (palabra + mayúscula)
 *   normalName, Tour, FORJA_TOUR_STEPS → pass
 */
const FORBIDDEN_SUFFIXES = "Service|Handler|Util|Helper|Misc|Manager";
const BRAND_NAMING_REGEX =
  `^(?!.*(?:${FORBIDDEN_SUFFIXES})(?:[A-Z]|$))` +
  `(?!.*[a-z](?:${FORBIDDEN_SUFFIXES})).+$`;

const config = [
  ...next,
  {
    rules: {
      "id-match": [
        "error",
        BRAND_NAMING_REGEX,
        { properties: false, classFields: true },
      ],
    },
  },
  {
    ignores: [".next/**", "node_modules/**", "dist/**", "out/**"],
  },
];

export default config;
