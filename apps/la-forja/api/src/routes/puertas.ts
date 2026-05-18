/**
 * La Forja — Rutas /api/puertas (D2.6).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: LF-FIVE-DOORS-001 + §2.5 SPEC v3.2.
 *
 * GET  /api/puertas               → enumerator con las 5 puertas canónicas
 * POST /api/puertas/:nombre       → invoca puerta con payload pasado en body
 *
 * Si nombre no está en PUERTAS → 404 puerta_not_found.
 * cowork_local: el wrapper enforza userRole automáticamente desde c.var.user.
 */

import { Hono } from "hono";
import {
  PUERTAS,
  invokeCoworkLocal,
  invokeKernelMonstruo,
  invokeManusApple,
  invokeManusGoogle,
  invokeSimulador,
  type PuertaName,
} from "../puertas/index.js";
import { recordEvent } from "../lib/telemetry.js";
import type { ForjaAuthContext } from "../middleware/auth.js";

export function puertasRoutes() {
  const app = new Hono<ForjaAuthContext>();

  app.get("/", (c) => {
    return c.json({ ok: true, puertas: PUERTAS });
  });

  app.post("/:nombre", async (c) => {
    const nombre = c.req.param("nombre") as PuertaName;
    if (!PUERTAS.includes(nombre as PuertaName)) {
      return c.json(
        {
          ok: false,
          error: `[la-forja:puerta_not_found] '${nombre}' no es puerta canónica. Disponibles: ${PUERTAS.join(", ")}`,
        },
        404,
      );
    }
    const body = (await c.req.json().catch(() => ({}))) as Record<
      string,
      unknown
    >;
    const user = c.var.user;

    let result: unknown;
    try {
      switch (nombre) {
        case "manus_apple":
          result = await invokeManusApple(
            body as unknown as Parameters<typeof invokeManusApple>[0],
          );
          break;
        case "manus_google":
          result = await invokeManusGoogle(
            body as unknown as Parameters<typeof invokeManusGoogle>[0],
          );
          break;
        case "cowork_local":
          // cowork_local enforza role desde c.var.user (AC5 + R5 mitigación)
          result = await invokeCoworkLocal({
            userRole: user.role === "t1_alfredo" ? "T1-Alfredo" : "T1-Padre",
            contextMarkdown: (body.contextMarkdown as string) ?? "",
            baseDir: body.baseDir as string | undefined,
          });
          break;
        case "kernel_monstruo":
          result = await invokeKernelMonstruo(
            body as unknown as Parameters<typeof invokeKernelMonstruo>[0],
          );
          break;
        case "simulador":
          result = await invokeSimulador(
            body as unknown as Parameters<typeof invokeSimulador>[0],
          );
          break;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      await recordEvent({
        userId: user.id,
        type: "puerta_invoked",
        metadata: { puerta: nombre, ok: false, error: message },
      });
      return c.json({ ok: false, error: message }, 500);
    }

    await recordEvent({
      userId: user.id,
      type: "puerta_invoked",
      metadata: { puerta: nombre, ok: true },
    });
    return c.json({ ok: true, puerta: nombre, result });
  });

  return app;
}
