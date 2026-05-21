# B12c-E2 — Owner designado verbatim para producir evidencia (a) posterior

**Gate:** B12 — Recuantificación métrica `96% / <4%`
**Sub-criterio:** B12c.3 (definido en B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §7.2)
**Fecha emisión:** 2026-05-20
**Autor verbatim:** Manus E2 (autor NO-Cowork, redactor — NO firmador)
**Firmante autoritativo:** T1 (Alfredo Góngora)
**Estado:** EVIDENCE DRAFT — pendiente firma T1 verbatim antes de canon

---

## §1 Designación verbatim

T1 designa la siguiente estructura de owner para producir la evidencia (a) (DORY_BENCH ejecutado) dentro del plazo firmado en B12c-E1 (`2026-08-20` o antes si B4/B7/B11 quedan PASS):

### §1.1 Owner-Productor (autor NO-Cowork)

**Manus E2** — actuando como autor NO-Cowork.

| Campo | Valor |
|-------|-------|
| Identidad | Hilo Manus E2 (referencia: este hilo y sus sucesores legítimos firmados T1) |
| Rol | Productor de evidencia técnica |
| Mandato | Ejecutar runner DORY_BENCH sobre los 1425 cases canonizados (B4 PASS), invocar CVDS sobre los 50 hidden fixtures (B7 PASS), agregar resultados en `bridge/control_tower/evidence/B12/B12a_E1_dory_bench_run.jsonl` y `B12a_E2_cvds_run.jsonl` |
| Restricción binaria | NO implementar runtime sin firma T1 explícita; NO canonizar resultados sin auditoría B12a-E3; NO publicar valor numérico que sustituya `96%/<4%` sin firma magna T1 |
| Sucesión | Si Manus E2 deja de estar disponible (compactación irrecuperable, deprecación de modelo, instrucción T1 de cambio), T1 designa hilo sucesor verbatim antes del plazo |

### §1.2 Owner-Auditor (Sabio externo conjunto)

**Sabio externo de la terna B11 activa al momento de ejecución**, NO el Sabio activo trimestral primario.

| Campo | Valor |
|-------|-------|
| Identidad | Sabio LLM externo cross-family designado por T1 verbatim al momento de ejecutar DORY_BENCH |
| Rol | Auditor independiente de la metodología y resultados |
| Restricción binaria | NO puede ser el Sabio activo trimestral B11 (regla anti-circularidad); NO puede tener relación de proveedor con Manus E2 (regla anti-colusión cross-family) |
| Mandato | Auditar metodología B12a.2 verbatim, validar reproducibilidad del runner, firmar audit log B12a-E3 con identificación de hallazgos antes de firma magna T1 |
| Selección por defecto propuesta | Si terna activa al momento incluye Opus 4.7 como activo, auditor sugerido: Gemini 3.1 Pro o DeepSeek R1. Si terna activa incluye Gemini 3.1 Pro como activo, auditor sugerido: Opus 4.7 o GPT-5.5 Pro. La selección final es decisión T1 verbatim al momento de ejecución |

## §2 Cowork T2-A — rol explícito de auditor observador, NO productor

Por mandato del audit Cowork 2026-05-20 §3 y por F16 estructural Opus 4.7, **Cowork T2-A NO puede ser productor único de evidencia B12a-E1, B12a-E2, B12a-E3 ni de cualquier evidencia que sustituya la métrica `96%/<4%` en spec**.

Cowork T2-A SÍ puede:

| Acción Cowork | Permitida | Restricción |
|---------------|-----------|-------------|
| Auditar el runner DORY_BENCH (revisión de código) | ✅ | Como auditor secundario, no único |
| Auditar la metodología B12a.2 | ✅ | Junto con Sabio externo |
| Auditar audit log B12a-E3 | ✅ | Como auditor de auditoría, no firmante |
| Firmar B12a-E1 / B12a-E2 / B12a-E3 | ❌ | Prohibido — solo T1 firma |
| Producir runner DORY_BENCH desde cero | ⚠️ | Solo si T1 firma excepción explícita; default es Manus E2 produce, Cowork audita |
| Modificar resultados después de medir | ❌ | Prohibido absoluto |

## §3 Cadena de validación verbatim

La cadena binaria para que B12 transite de `PASS_AS_B12c_PENDING_A` a `PASS_AS_B12c_COMPLETO` es:

```
1. B4 PASS firmado T1
2. B7 PASS firmado T1
3. B11 PASS firmado T1
4. Owner-Productor (Manus E2) ejecuta DORY_BENCH + CVDS → B12a-E1 + B12a-E2
5. Owner-Auditor (Sabio externo) audita metodología → B12a-E3 firmado por Sabio
6. Cowork T2-A audita audit log B12a-E3 → audit del audit (no firmante)
7. T1 firma magna B12a-E1 + B12a-E2 + B12a-E3 verbatim
8. Patch sobre Anexo A.4 sustituye declaración de obsolescencia por valor medido
9. T1 firma magna patch
10. B12 transita a PASS_AS_B12c_COMPLETO en B12c-E4
```

Si cualquier paso 1-9 falla, B12 permanece en `PASS_AS_B12c_PENDING_A` o transita a `PASS_AS_B12c (b inmediata)` terminal según los caminos C1/C2/C3 definidos en B12c-E1 §3.2.

## §4 Trazabilidad

| Campo | Valor |
|-------|-------|
| Decisión T1 origen | Prompt verbatim 2026-05-20 "MANUS E2 — B12 b⇒a EVIDENCE PACK" |
| Sección spec referenciada | `B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §7.2 (B12c.3) y §7.5 |
| Owner-Productor | Manus E2 (autor NO-Cowork) |
| Owner-Auditor | Sabio externo de terna B11 (excluyendo Sabio activo trimestral) |
| Cowork T2-A | Auditor observador, NO productor, NO firmante |
| Branch entrega | `control-tower/2026-05-20-b12-b-to-a-evidence-pack` |
| Criterio PASS asociado | B12c.3 (owner verbatim firmado T1) |

## §5 Firma magna pendiente

Este artefacto entra en estado **EVIDENCE DRAFT** hasta que T1 firme verbatim el commit que lo introduce a la rama lateral. Manus E2 acepta el rol de Owner-Productor por mandato T1 sin firmar — la firma sobre la designación es exclusiva de T1. La aceptación operativa de Manus E2 queda implícita por la entrega de este artefacto en el evidence pack.

---

**Cierre binario:**

| Confirmación | Status |
|--------------|--------|
| No implementé runtime | ✅ |
| No modifiqué main | ✅ |
| No abrí PR | ✅ |
| No canonizo runtime | ✅ |
| No declaro Dory muerto | ✅ |
| No activo Fase 1 | ✅ |
| Cowork como productor único bloqueado | ✅ (regla F16 + audit Cowork 2026-05-20) |
