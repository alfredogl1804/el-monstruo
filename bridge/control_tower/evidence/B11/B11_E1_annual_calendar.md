# B11-E1 — Calendario Anual de Terna Sabios (DRAFT)

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Año aplicable propuesto:** 2027 (firma T1 antes de 1 enero 2027)
**Fuente normativa:** closure pack v0.2 §6 (B11)

> Este calendario es DRAFT. T1 debe firmar verbatim D-B11-1 antes de que entre en vigor.

---

## §1 Calendario base 2027

| Trimestre | Período | Sabio activo primario | Proveedor | Sabio suplente |
|-----------|---------|----------------------|-----------|----------------|
| Q1-2027 | 1 enero — 31 marzo | Opus 4.7 | Anthropic | Claude Sonnet 4.7 |
| Q2-2027 | 1 abril — 30 junio | DeepSeek R1 | DeepSeek | DeepSeek V3 |
| Q3-2027 | 1 julio — 30 septiembre | Gemini 3.1 Pro | Google | Gemini 3.0 Pro |
| Q4-2027 | 1 octubre — 31 diciembre | Kimi K2.6 | Moonshot | Kimi K2.5 |

---

## §2 Roles específicos no rotativos

| Rol | Sabio asignado | Razón |
|-----|----------------|-------|
| Auditor adversarial anual (B11-E5) | Grok 4 | Independencia del calendario rotativo + perspectiva contrarian |
| Arquitecto del enjambre / KL divergence (B11-E4) | GPT-5.4 | Familiaridad con métricas estadísticas + rol arquitecto en el ecosistema |
| Auditor de la matriz B9 (D-B9-3) | Sigue calendario rotativo trimestral | Coincide con Sabio activo del trimestre |
| Auditor B6-E2/E6 (key custody) | Sigue calendario rotativo trimestral | Coincide con Sabio activo del trimestre |
| Auditor B7-E1/E4/E5/E7 (fixture custody) | Sigue calendario rotativo trimestral | Coincide con Sabio activo del trimestre |

---

## §3 Validación de diversidad (B11.4)

En cualquier ventana de 4 trimestres consecutivos, los 4 Sabios provienen de proveedores distintos:

- Q1 Anthropic, Q2 DeepSeek, Q3 Google, Q4 Moonshot ⇒ 4 proveedores distintos. ✓ Cumple.

---

## §4 Set de calibración (B11.5)

Set fijo congelado de 20 fixtures DORY_BENCH canónicos que los 4 Sabios deben procesar al inicio de su trimestre. La distribución de veredictos resultante alimenta el cálculo de KL divergence en B11-E4.

El set vive en `bridge/control_tower/evidence/B11/calibration_set_2027.json` (no incluido en este DRAFT; producido por el custodio de fixtures B7 al inicio del año tras firma T1).

---

## §5 Triggers de revisión extraordinaria del calendario

- KL divergence promedio anual <0.15 ⇒ revisión obligatoria.
- Deprecación de modelo por proveedor ⇒ promover suplente y revisar calendario.
- Reporte adversarial Grok anual con findings de severidad crítica ⇒ revisión obligatoria.
- Cambio en costo/disponibilidad de API que impide acceso continuo ⇒ amendment T1.

---

## §6 Firma magna T1 requerida

Para que este calendario entre en vigor, T1 firma:

> "Firma magna: apruebo verbatim el calendario B11-E1 para el año 2027 según se documenta arriba. Autorizo a la terna rotativa Q1 Opus 4.7 / Q2 DeepSeek R1 / Q3 Gemini 3.1 Pro / Q4 Kimi K2.6 con suplentes designados. Autorizo a Grok 4 como auditor adversarial anual (B11-E5) y a GPT-5.4 como productor de KL divergence (B11-E4)."

Firma: ______________________ Fecha: ______________________

---

**Firma magna pendiente.** Hasta entonces, este calendario es DRAFT y NO está en vigor.
