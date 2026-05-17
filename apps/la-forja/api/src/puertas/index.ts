/**
 * La Forja — Enumerator canónico de las 5 puertas (LF-FIVE-DOORS-001).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.4.
 * Doctrina: §15 SPEC v3.2 — code policy enforcer.
 *
 *   "Exactamente 5 puertas: manus_apple, manus_google, cowork_local,
 *    kernel_monstruo, simulador. Sexta puerta requiere SPEC nuevo."
 *
 * El test puertas/index.test.ts verifica:
 *   - PUERTAS.length === 5 exact
 *   - Cada nombre coincide §2.5 SPEC
 *   - Cada puerta exporta función invoke<NombreCamelCase>()
 *
 * Si alguien intenta agregar una sexta puerta sin SPEC nuevo, este test
 * falla en CI y el commit no puede mergearse a main.
 */

import { invokeCoworkLocal } from "./cowork_local";
import { invokeKernelMonstruo } from "./kernel_monstruo";
import { invokeManusApple } from "./manus_apple";
import { invokeManusGoogle } from "./manus_google";
import { invokeSimulador } from "./simulador";

export const PUERTAS = [
  "manus_apple",
  "manus_google",
  "cowork_local",
  "kernel_monstruo",
  "simulador",
] as const satisfies readonly string[];

export type PuertaName = (typeof PUERTAS)[number];

export const PUERTA_INVOKERS: Readonly<Record<PuertaName, unknown>> = {
  manus_apple: invokeManusApple,
  manus_google: invokeManusGoogle,
  cowork_local: invokeCoworkLocal,
  kernel_monstruo: invokeKernelMonstruo,
  simulador: invokeSimulador,
};

export {
  invokeCoworkLocal,
  invokeKernelMonstruo,
  invokeManusApple,
  invokeManusGoogle,
  invokeSimulador,
};

export {
  COWORK_CONTEXT_FILE,
  type ForjaUserRole,
  type PuertaCoworkLocalInput,
  type PuertaCoworkLocalOutput,
} from "./cowork_local";
export type {
  PuertaKernelInput,
  PuertaKernelOutput,
} from "./kernel_monstruo";
export type {
  PuertaManusInput,
  PuertaManusOutput,
} from "./manus_apple";
export type {
  PuertaSimuladorInput,
  PuertaSimuladorOutput,
} from "./simulador";
export { SIMULADOR_BASE_URL } from "./simulador";
