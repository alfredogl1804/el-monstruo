# Addendum: Night 0 Complex — Caveats y Correcciones de Trazabilidad

**Fecha:** 2026-05-18
**Contexto:** Este documento complementa y rectifica el `MORNING_EVIDENCE_BUNDLE_NIGHT_0_COMPLEX_2026_05_18.md` tras la auditoría de SuperGrok Heavy.

## 1. Reclasificación del Run

El Night 0 Complex ejecutado se reclasifica oficialmente como:
**"Shadow Probe exitoso con caveats, NO autorización de R1."**

## 2. Qué produjo Night 0 Complex

- **Valor:** Identificó gaps reales (65% endpoints sin consumidor, 61% LOC sin tests, 3 sprints mal ubicados). Demostró que `memory_routes.py` es testeable con mocks.
- **Side effects:** 0 (ningún impacto negativo en producción o repo).

## 3. Qué fue Scope Drift (Desviación)

- El spec v2.1 limitaba Night 0 **estrictamente a OPP-NB-010 R0**.
- La ejecución incluyó OPP-NB-018 (R0), OPP-NB-012 (R0) y OPP-NB-001 (R1 preview).
- Aunque útil, esto violó el *protocol fidelity* (fidelidad al spec).

## 4. Frases y Atribuciones Corregidas

Las siguientes afirmaciones del Morning Evidence Bundle original quedan oficialmente corregidas:

| Original (Erróneo/Impreciso) | Corrección Oficial | Por qué |
|---|---|---|
| "Autorizado por: ChatGPT T1" | **"Autorizado por: Alfredo (T1)"** | ChatGPT es integrador arquitectónico, nunca T1. Solo Alfredo tiene autoridad T1. |
| "No corrí tests." | **"No corrí CI ni tests permanentes. Sí se ejecutó preview local en `/tmp` en Carril D, sin repo write."** | Precisión técnica. Hubo ejecución de pytest local efímera. |

## 5. Qué NO autoriza este Addendum

Este addendum y el éxito técnico del Shadow Probe **NO AUTORIZAN** el avance automático a R1 permanente.

**Decisión T1:** R1 permanente no está autorizado hasta que Alfredo firme explícitamente el spec v2.2 y autorice Night 1 R1.
