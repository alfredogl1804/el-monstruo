import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  loadRequireValidation,
  saveRequireValidation,
  FORJA_TUTOR_PREF_KEYS,
} from "./preferences";

/**
 * La Forja — tests preferences.ts
 * Sprint LA-FORJA-001 D3.3.
 *
 * Doctrina: happy-dom 20.x expone window.localStorage como un objeto plano
 * sin prototype Storage real, por lo que estos tests instalan un mock
 * Map-backed compatible con la API Web Storage para validar contratos
 * de save/load/SSR/fail-soft sin acoplarse a la implementación interna
 * del entorno.
 *
 * Cubre:
 *   - Default false cuando localStorage está vacío
 *   - Round-trip true/false vía save → load
 *   - Valor corrupto en localStorage → default + warn fail-loud namespace
 *   - getItem/setItem throws → fail-soft (default + warn)
 */

interface StorageMock {
  store: Map<string, string>;
  getItem: ReturnType<typeof vi.fn>;
  setItem: ReturnType<typeof vi.fn>;
  removeItem: ReturnType<typeof vi.fn>;
  clear: ReturnType<typeof vi.fn>;
}

function buildStorageMock(): StorageMock {
  const store = new Map<string, string>();
  return {
    store,
    getItem: vi.fn((k: string) => (store.has(k) ? store.get(k)! : null)),
    setItem: vi.fn((k: string, v: string) => {
      store.set(k, String(v));
    }),
    removeItem: vi.fn((k: string) => {
      store.delete(k);
    }),
    clear: vi.fn(() => store.clear()),
  };
}

describe("tutor preferences", () => {
  let mock: StorageMock;

  beforeEach(() => {
    mock = buildStorageMock();
    Object.defineProperty(window, "localStorage", {
      value: mock,
      configurable: true,
      writable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loadRequireValidation devuelve false por default cuando no hay valor", () => {
    expect(loadRequireValidation()).toBe(false);
    expect(mock.getItem).toHaveBeenCalledWith(
      FORJA_TUTOR_PREF_KEYS.requireValidation,
    );
  });

  it("save/load round-trip funciona binario para true", () => {
    saveRequireValidation(true);
    expect(mock.store.get(FORJA_TUTOR_PREF_KEYS.requireValidation)).toBe("true");
    expect(loadRequireValidation()).toBe(true);
  });

  it("save/load round-trip funciona binario para false", () => {
    saveRequireValidation(true);
    saveRequireValidation(false);
    expect(mock.store.get(FORJA_TUTOR_PREF_KEYS.requireValidation)).toBe(
      "false",
    );
    expect(loadRequireValidation()).toBe(false);
  });

  it("valor corrupto en localStorage → default + warn fail-loud", () => {
    mock.store.set(
      FORJA_TUTOR_PREF_KEYS.requireValidation,
      "garbage-value",
    );
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(loadRequireValidation()).toBe(false);
    expect(warnSpy).toHaveBeenCalledWith(
      expect.stringContaining("[la-forja:tutor_pref_corrupt]"),
    );
  });

  it("setItem throws → save no propaga, log fail-soft", () => {
    mock.setItem.mockImplementation(() => {
      throw new Error("QuotaExceededError");
    });
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(() => saveRequireValidation(true)).not.toThrow();
    expect(warnSpy).toHaveBeenCalledWith(
      expect.stringContaining("[la-forja:tutor_pref_write_failed]"),
    );
  });

  it("getItem throws → load devuelve default + warn fail-soft", () => {
    mock.getItem.mockImplementation(() => {
      throw new Error("SecurityError");
    });
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(loadRequireValidation()).toBe(false);
    expect(warnSpy).toHaveBeenCalledWith(
      expect.stringContaining("[la-forja:tutor_pref_read_failed]"),
    );
  });
});
