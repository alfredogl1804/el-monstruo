/**
 * La Forja - vitest setup global.
 * Sprint LA-FORJA-001 D3.1 hardening.
 *
 * React 19 requiere que el entorno de test declare
 * IS_REACT_ACT_ENVIRONMENT = true para que `act(...)` funcione
 * sin warnings en happy-dom (sin testing-library).
 *
 * Ver: https://react.dev/reference/react/act
 */
declare global {
  var IS_REACT_ACT_ENVIRONMENT: boolean;
}

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

export {};
