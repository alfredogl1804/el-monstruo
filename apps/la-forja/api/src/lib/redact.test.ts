/**
 * La Forja — Tests redactor PII (R10 SPEC v3.2 §9, D2.3).
 *
 * Validación binaria de los 4 patrones:
 *   1. Email
 *   2. Teléfono MX
 *   3. RFC mexicano
 *   4. Cuenta bancaria 16-18 dígitos
 *
 * Cada patrón con casos positivos (debe redactar) y negativos (no toca).
 */

import { describe, expect, it } from "vitest";
import { preLogRedact, redactPII } from "./redact.js";

describe("redactPII — emails", () => {
  it("redacta email simple", () => {
    const r = redactPII("contacto: alfredo@gmail.com");
    expect(r.text).toBe("contacto: [REDACTED:EMAIL]");
    expect(r.replacements.email).toBe(1);
  });

  it("redacta varios emails en el mismo texto", () => {
    const r = redactPII("escribe a a@b.com o c+d@e.org.mx");
    expect(r.text).toBe("escribe a [REDACTED:EMAIL] o [REDACTED:EMAIL]");
    expect(r.replacements.email).toBe(2);
  });

  it("no toca texto que parece pero no es email", () => {
    const r = redactPII("dame el @ que tienes");
    expect(r.text).toBe("dame el @ que tienes");
    expect(r.replacements.email).toBe(0);
  });
});

describe("redactPII — teléfonos MX", () => {
  it("redacta +52 con espacios", () => {
    const r = redactPII("llámame al +52 999 123 4567");
    expect(r.text).toBe("llámame al [REDACTED:PHONE]");
    expect(r.replacements.phone).toBe(1);
  });

  it("redacta +52 1 (móvil) con guiones", () => {
    const r = redactPII("móvil: +52-1-999-123-4567");
    expect(r.text).toBe("móvil: [REDACTED:PHONE]");
    expect(r.replacements.phone).toBe(1);
  });

  it("redacta sin signo + (52 directo)", () => {
    const r = redactPII("tel 52 555 1234567");
    expect(r.text).toBe("tel [REDACTED:PHONE]");
    expect(r.replacements.phone).toBe(1);
  });

  it("no redacta números cortos no-MX", () => {
    const r = redactPII("la edad es 5567");
    expect(r.replacements.phone).toBe(0);
  });
});

describe("redactPII — RFC mexicano", () => {
  it("redacta RFC persona física (4 letras)", () => {
    const r = redactPII("RFC: GOAL890101ABC");
    expect(r.text).toBe("RFC: [REDACTED:RFC]");
    expect(r.replacements.rfc).toBe(1);
  });

  it("redacta RFC persona moral (3 letras)", () => {
    const r = redactPII("empresa RFC: ABC900101XYZ");
    expect(r.text).toBe("empresa RFC: [REDACTED:RFC]");
    expect(r.replacements.rfc).toBe(1);
  });

  it("no redacta texto similar pero no-RFC", () => {
    const r = redactPII("código ABCDE12345");
    expect(r.replacements.rfc).toBe(0);
  });
});

describe("redactPII — cuentas bancarias", () => {
  it("redacta cuenta de 16 dígitos", () => {
    const r = redactPII("cuenta 1234567812345678");
    expect(r.text).toBe("cuenta [REDACTED:ACCOUNT]");
    expect(r.replacements.account).toBe(1);
  });

  it("redacta CLABE de 18 dígitos", () => {
    const r = redactPII("CLABE 012345678901234567");
    expect(r.text).toBe("CLABE [REDACTED:ACCOUNT]");
    expect(r.replacements.account).toBe(1);
  });

  it("no redacta números de menos de 16 dígitos", () => {
    const r = redactPII("código 12345");
    expect(r.replacements.account).toBe(0);
  });
});

describe("redactPII — combinatorias", () => {
  it("redacta los 4 tipos juntos en orden binario", () => {
    const input =
      "soy alfredo@example.com, tel +52 999 123 4567, RFC GOAL890101ABC, cuenta 1234567812345678";
    const r = redactPII(input);
    expect(r.text).toBe(
      "soy [REDACTED:EMAIL], tel [REDACTED:PHONE], RFC [REDACTED:RFC], cuenta [REDACTED:ACCOUNT]",
    );
    expect(r.replacements.email).toBe(1);
    expect(r.replacements.phone).toBe(1);
    expect(r.replacements.rfc).toBe(1);
    expect(r.replacements.account).toBe(1);
  });

  it("texto sin PII no se modifica", () => {
    const r = redactPII("Hola, ¿cómo estás hoy?");
    expect(r.text).toBe("Hola, ¿cómo estás hoy?");
    expect(r.replacements).toEqual({
      email: 0,
      phone: 0,
      rfc: 0,
      account: 0,
    });
  });
});

describe("preLogRedact helper", () => {
  it("retorna solo el texto redactado (sin replacements)", () => {
    expect(preLogRedact("a@b.com")).toBe("[REDACTED:EMAIL]");
  });
});
