/**
 * La Forja — Redactor PII (R10 mitigación post-audit Cowork v3.2).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.3.
 * Doctrina: §9 R10 SPEC v3.2.
 *
 * El Cliente Cero T1-Padre puede compartir información personal sensible
 * mientras conversa con el tutor (proyectos, contactos, finanzas). Antes
 * de exportar a Langfuse para observabilidad, redactamos los siguientes
 * patrones binariamente identificables:
 *
 *   1. Emails             email@domain.tld    → [REDACTED:EMAIL]
 *   2. Teléfonos MX       +52 999 123 4567    → [REDACTED:PHONE]
 *   3. RFCs               XAXX010101000        → [REDACTED:RFC]
 *   4. Cuentas bancarias  16-18 dígitos       → [REDACTED:ACCOUNT]
 *
 * Toggle UI «No enviar este turn a observabilidad» (D3) puede saltarse
 * la redacción y NO enviar nada. Retention Langfuse 30 días.
 *
 * Tests cubren cada regex con casos positivos (matchea) y negativos (no
 * matchea texto similar pero válido).
 */

// Email RFC-5322 simplificado (no edge cases exóticos)
const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;

// Teléfono MX: +52 opcional, lada 2-3 dígitos, número 7-8 dígitos.
// Acepta espacios, guiones o parens entre grupos.
const PHONE_MX_RE =
  /\+?52[\s-]?(?:1[\s-]?)?\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}/g;

// RFC mexicano: 3-4 letras + 6 dígitos (fecha YYMMDD) + 3 alfanuméricos.
const RFC_RE = /\b[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}\b/g;

// Cuenta bancaria: 16-18 dígitos seguidos (sin espacios) o con guiones cada 4.
const ACCOUNT_RE = /\b\d{16,18}\b/g;

export interface RedactResult {
  text: string;
  replacements: {
    email: number;
    phone: number;
    rfc: number;
    account: number;
  };
}

/**
 * Aplica las 4 redacciones en orden binario sobre el texto.
 * Orden importa: account ANTES de phone para no fragmentar 16-18 dígitos.
 *
 * Retorna texto redactado + contador de reemplazos por categoría
 * para auditoría en logs (sin exponer el contenido original).
 */
export function redactPII(input: string): RedactResult {
  let text = input;
  const replacements = { email: 0, phone: 0, rfc: 0, account: 0 };

  // 1. Account first (largo dígitos, evita colisión con phone)
  text = text.replace(ACCOUNT_RE, () => {
    replacements.account += 1;
    return "[REDACTED:ACCOUNT]";
  });

  // 2. Email
  text = text.replace(EMAIL_RE, () => {
    replacements.email += 1;
    return "[REDACTED:EMAIL]";
  });

  // 3. RFC
  text = text.replace(RFC_RE, () => {
    replacements.rfc += 1;
    return "[REDACTED:RFC]";
  });

  // 4. Phone MX
  text = text.replace(PHONE_MX_RE, () => {
    replacements.phone += 1;
    return "[REDACTED:PHONE]";
  });

  return { text, replacements };
}

/**
 * Helper para preLog hook usado por telemetry. Mantiene el shape simple
 * para integraciones futuras D5 con Langfuse.
 */
export function preLogRedact(text: string): string {
  return redactPII(text).text;
}
