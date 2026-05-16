import next from "eslint-config-next";

/**
 * La Forja — ESLint flat config (Next 16 + ESLint 9).
 * Hereda eslint-config-next y agrega un guard de Brand Naming
 * (Regla Dura #4 + Brand Engine).
 *
 * Nota D3.0 hardening (F-D3.0-02): eslint-config-next@16 exporta un
 * array de configs (no función). Spread directo, sin invocar.
 *
 * Nota D3.0 hardening (F-D3.0-09): regex con \\b...\\b. INSUFICIENTE.
 *
 * Nota D3.1 hardening (F-D3.1-01, Perplexity): la regex anterior dejaba
 *   pasar UserService, AuthHandler, OnboardingFinishHandler. Reemplazada
 *   por lookahead "(?:[A-Z]|$)".
 *
 * Nota D3.1.1 hardening (R-D3.1-05, Perplexity regression): la versión
 *   D3.1 hardening seguía dejando pasar USERSERVICE, FORMAT_UTIL,
 *   AUTH_MANAGER (ALL_CAPS y snake_UPPER). Verificado binariamente con
 *   .regex_verify_r05_v2.mjs en la raíz del repo.
 *
 * Versión actual: dos lookaheads — uno para PascalCase (sufijo seguido
 * de mayúscula o EOS), otro para ALL_CAPS (sufijo en mayúsculas seguido
 * de mayúscula, underscore, dígito o EOS).
 *
 * Casos cubiertos:
 *   UserService, OnboardingFinishHandler, ServiceWorker  → reject
 *   USERSERVICE, FORMAT_UTIL, AUTH_MANAGER               → reject
 *   ForjaTourSteps, getUserById, FORJA_TOUR_STEPS, service → pass
 *
 * Falso positivo conocido y aceptado: ServiceMash (prefijo Service +
 * otra palabra) sería rechazado. En la práctica nadie en La Forja
 * usaría ese nombre — el valor de banear ServiceManager (sufijo) es
 * mayor que el coste teórico de ServiceMash (jamás usado).
 */
const FORBIDDEN_SUFFIXES = "Service|Handler|Util|Helper|Misc|Manager";
const FORBIDDEN_SUFFIXES_UPPER = FORBIDDEN_SUFFIXES.toUpperCase();
const BRAND_NAMING_REGEX =
  `^(?!.*(?:${FORBIDDEN_SUFFIXES})(?:[A-Z]|$))` +
  `(?!.*(?:${FORBIDDEN_SUFFIXES_UPPER})(?:[A-Z_0-9]|$)).+$`;

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
