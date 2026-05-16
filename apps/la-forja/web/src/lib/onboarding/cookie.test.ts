import { afterEach, describe, expect, it } from "vitest";
import {
  FORJA_TOUR_COOKIE_NAME,
  clearForjaTourCookie,
  readForjaTourCookie,
  writeForjaTourCookie,
} from "./cookie";

/**
 * La Forja — tests cookie helpers del tour.
 * Sprint LA-FORJA-001 D3.1.
 *
 * Usamos happy-dom 20 (configurado en vitest.config.ts).
 */

describe("forja tour cookie helpers", () => {
  afterEach(() => {
    // Aseguramos un estado limpio entre tests para evitar leak.
    clearForjaTourCookie();
  });

  it("readForjaTourCookie devuelve null cuando no existe", () => {
    expect(readForjaTourCookie()).toBeNull();
  });

  it("writeForjaTourCookie escribe la cookie con el name canónico", () => {
    const ts = new Date("2026-05-16T10:30:00.000Z");
    writeForjaTourCookie({ now: ts });
    expect(document.cookie).toContain(FORJA_TOUR_COOKIE_NAME);
    const read = readForjaTourCookie();
    expect(read).toBe("2026-05-16T10:30:00.000Z");
  });

  it("clearForjaTourCookie elimina el valor", () => {
    writeForjaTourCookie({ now: new Date("2026-05-16T11:00:00.000Z") });
    expect(readForjaTourCookie()).not.toBeNull();
    clearForjaTourCookie();
    expect(readForjaTourCookie()).toBeNull();
  });

  it("read soporta valores con caracteres encodeados", () => {
    // Forzamos una escritura con un valor que requiere decode.
    document.cookie = `${FORJA_TOUR_COOKIE_NAME}=${encodeURIComponent("2026-05-16T12:00:00.000Z")}; path=/; samesite=lax`;
    expect(readForjaTourCookie()).toBe("2026-05-16T12:00:00.000Z");
  });

  it("read tolera document.cookie vacío sin throw", () => {
    clearForjaTourCookie();
    expect(() => readForjaTourCookie()).not.toThrow();
  });
});
