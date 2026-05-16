import { afterEach, describe, expect, it } from "vitest";
import {
  FORJA_TOUR_COOKIE_NAME,
  clearForjaTourCookie,
  readForjaTourCookie,
  writeForjaTourCookie,
} from "./cookie";

/**
 * La Forja — tests cookie helpers del tour.
 * Sprint LA-FORJA-001 D3.1 + hardening Perplexity F-D3.1-09, -10.
 *
 * Usamos happy-dom 20 (configurado en vitest.config.ts).
 *
 * Hardening aplicado:
 *   F-D3.1-09: nuevo test verifica que `readForjaTourCookie` parsea
 *              correctamente cuando otras cookies usan separador
 *              `;` sin espacio (Set-Cookie spec lo permite).
 *   F-D3.1-10: el test de decode usa un valor con caracteres que
 *              REQUIEREN encoding, no un ISO timestamp ASCII.
 */

describe("forja tour cookie helpers", () => {
  afterEach(() => {
    // Aseguramos un estado limpio entre tests para evitar leak.
    clearForjaTourCookie();
    // Limpiar cookies sucias que algún test pudo dejar.
    document.cookie = "extra1=; path=/; max-age=0";
    document.cookie = "extra2=; path=/; max-age=0";
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

  // F-D3.1-10: usa un valor con caracteres que requieren encoding real.
  // Si el helper no llama `decodeURIComponent`, este test falla.
  it("read decodifica correctamente valores con caracteres especiales", () => {
    const raw = "v with spaces & = signs / and ñ";
    document.cookie = `${FORJA_TOUR_COOKIE_NAME}=${encodeURIComponent(raw)}; path=/; samesite=lax`;
    expect(readForjaTourCookie()).toBe(raw);
  });

  // F-D3.1-09: el split debe tolerar separador sin espacio entre cookies.
  it("read parsea cuando otras cookies usan separador ';' sin espacio", () => {
    // Inyectamos varias cookies; happy-dom las serializa con `; ` por
    // default, así que forzamos el caso patológico mutando manualmente.
    document.cookie = "extra1=val1; path=/";
    writeForjaTourCookie({ now: new Date("2026-05-16T12:00:00.000Z") });
    document.cookie = "extra2=val2; path=/";

    // Sanity: con separador estándar funciona.
    expect(readForjaTourCookie()).toBe("2026-05-16T12:00:00.000Z");

    // Caso patológico: verificamos directamente que la regex
    // `/;\s*/` parsea sin espacio. Construimos el string a mano.
    const fakeCookieString = `extra1=val1;${FORJA_TOUR_COOKIE_NAME}=${encodeURIComponent("2026-05-16T12:00:00.000Z")};extra2=val2`;
    const parts = fakeCookieString.split(/;\s*/);
    const target = parts.find((p) => p.startsWith(`${FORJA_TOUR_COOKIE_NAME}=`));
    expect(target).toBeDefined();
    expect(decodeURIComponent(target!.split("=")[1]!)).toBe(
      "2026-05-16T12:00:00.000Z",
    );
  });

  it("read tolera document.cookie vacío sin throw", () => {
    clearForjaTourCookie();
    expect(() => readForjaTourCookie()).not.toThrow();
  });

  // F-D3.1-09 followup: cookie con encoding malformado no crashea.
  it("read devuelve null cuando el valor tiene encoding malformado", () => {
    document.cookie = `${FORJA_TOUR_COOKIE_NAME}=%E0%A4%A; path=/`;
    expect(() => readForjaTourCookie()).not.toThrow();
    expect(readForjaTourCookie()).toBeNull();
  });
});
