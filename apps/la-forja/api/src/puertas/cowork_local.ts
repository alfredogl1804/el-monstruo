/**
 * La Forja — Puerta `cowork_local`.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.4.
 * Doctrina: §2.5 + AC5 SPEC v3.2.
 *
 * Escribe archivo de contexto en `.monstruo/COWORK_CONTEXT_INJECTION.md`
 * que será leído por Claude Code (Cowork) en su próximo turn.
 *
 * Solo opera para usuario T1-Alfredo (acceso al Mac vía Manus My Computer).
 * Para T1-Padre la puerta retorna `not_available_in_environment` salvo que
 * él instale Claude Code en su máquina.
 *
 * El path es relativo al cwd del proceso La Forja API (que en Railway
 * NO tiene .monstruo/), pero el caller puede sobrescribirlo con baseDir
 * para tests deterministas y para futuro D5 con NFS share T1-Alfredo.
 */

import { promises as fs } from "node:fs";
import path from "node:path";

export type ForjaUserRole = "T1-Alfredo" | "T1-Padre";

export interface PuertaCoworkLocalInput {
  /** Rol del usuario invocando la puerta */
  userRole: ForjaUserRole;
  /** Contenido a escribir en el archivo de contexto */
  contextMarkdown: string;
  /** Override del directorio base (default: cwd) */
  baseDir?: string;
}

export interface PuertaCoworkLocalOutput {
  status: "written" | "not_available_in_environment";
  path?: string;
  bytesWritten?: number;
}

export const COWORK_CONTEXT_FILE = ".monstruo/COWORK_CONTEXT_INJECTION.md";

/**
 * Invoca la puerta cowork_local. Retorna `not_available_in_environment`
 * cuando el rol no es T1-Alfredo (binariamente; sin error). Esto permite al
 * frontend mostrar UI distinta sin manejar exceptions.
 */
export async function invokeCoworkLocal(
  input: PuertaCoworkLocalInput,
): Promise<PuertaCoworkLocalOutput> {
  if (input.userRole !== "T1-Alfredo") {
    return { status: "not_available_in_environment" };
  }

  const baseDir = input.baseDir ?? process.cwd();
  const filePath = path.join(baseDir, COWORK_CONTEXT_FILE);

  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, input.contextMarkdown, "utf8");

  return {
    status: "written",
    path: filePath,
    bytesWritten: Buffer.byteLength(input.contextMarkdown, "utf8"),
  };
}
