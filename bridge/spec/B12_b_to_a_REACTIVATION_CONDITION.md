# B12c-E3 — Condición binaria de reactivación de métrica cuantitativa

**Gate:** B12 — Recuantificación métrica `96% / <4%`
**Sub-criterio:** B12c.4 (definido en B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §7.2)
**Fecha emisión:** 2026-05-20
**Autor verbatim:** Manus E2 (autor NO-Cowork, redactor — NO firmador)
**Firmante autoritativo:** T1 (Alfredo Góngora)
**Estado:** EVIDENCE DRAFT — pendiente firma T1 verbatim antes de canon
**Canon target:** `bridge/spec/` (cuando T1 firme magna)

---

## §1 Objeto

Este artefacto canoniza la **condición binaria única** bajo la cual la métrica cuantitativa de la Dory Cure se reactiva en spec, sustituyendo verbatim la declaración de obsolescencia firmada en B12b-E1 (artefacto separado). Sin esta condición cumplida, la métrica numérica permanece declarada obsoleta sin sucesor.

## §2 Condición binaria verbatim

> Cuando los seis sub-criterios B12a.1, B12a.2, B12a.3, B12a.4, B12a.5 y B12a.6 estén **simultáneamente PASS** con firma magna T1 verbatim sobre cada uno, la métrica cuantitativa medida (resultado verbatim de DORY_BENCH + CVDS) **sustituye** la declaración de obsolescencia en el Anexo A.4 del spec vigente, y B12 transita de `PASS_AS_B12c_PENDING_A` a `PASS_AS_B12c_COMPLETO` en el audit log B12c-E4.

### §2.1 Tabla de los seis sub-criterios B12a (verbatim B6_B12_v0.2 §7.2)

| ID | Sub-criterio | Verificable por |
|----|--------------|-----------------|
| **B12a.1** | DORY_BENCH ejecutado sobre los 1425 cases canonizados de B4 | Log VERIFICADOR-001 |
| **B12a.2** | Métrica medida con metodología verbatim documentada (definición de error, definición de FP-RAB, scope, runner reproducible) | Spec metodología B12_DORY_BENCH_METHODOLOGY.md |
| **B12a.3** | CVDS ejecutado con los 50 hidden fixtures de B7 (terna rotativa B11 activa) | Audit log B7-E5 |
| **B12a.4** | Resultado numérico verbatim publicado en spec v(N+1) sustituyendo `96%/<4%` por valor medido. Si <96%, se actualiza al valor real, no se sostiene el reclamo histórico | Diff spec |
| **B12a.5** | Auditoría metodológica por al menos 2 Sabios externos cross-family | Audit firmado |
| **B12a.6** | Firma magna T1 sobre resultado y actualización spec | Commit signature |

## §3 Estados binarios y transiciones de B12

```
                            (T1 firma b⇒a en 2026-05-20)
                                       │
                                       ▼
                    ┌───────────────────────────────────┐
                    │  PASS_AS_B12c_PENDING_A           │
                    │  (estado actual post firma T1)    │
                    └───────────────────────────────────┘
                                       │
       ┌───────────────────────────────┼─────────────────────────────────┐
       │                               │                                 │
       ▼                               ▼                                 ▼
B12a.1-B12a.6 PASS         Plazo 2026-08-20 vence con          Plazo vence sin
todos firmados T1          C1 ejecutado parcial / fallido      ningún camino
       │                               │                       firmado T1
       ▼                               ▼                                 ▼
PASS_AS_B12c_COMPLETO    T1 firma C2 (extender plazo)          NO-GO BINARIO
métrica numérica         o C3 (terminal cualitativo)           (ver B12c-E1 §3.3)
sustituye obsolescencia            │
                                   ▼
                  PASS_AS_B12c (b inmediata) terminal
                  o nuevo plazo con ciclo reiniciado
```

## §4 Reglas de no-reactivación silenciosa

Está **prohibido binariamente** reactivar la métrica cuantitativa por cualquier vía distinta a §2:

| Vía prohibida | Razón |
|---------------|-------|
| Reactivar métrica `96%/<4%` histórica sin medición B12a.1-B12a.6 | Métrica heredada sin base empírica reproducible (audit Opus 4.7 #3) |
| Publicar valor medido parcial (B12a.1 sin B12a.3) | CVDS sobre fixtures B7 es pre-requisito anti-overfit a simulador |
| Firmar B12a.6 sin B12a.5 (auditoría 2 Sabios externos) | Anti-autoauditoría F16 estructural Opus 4.7 |
| Firmar B12a.6 con auditoría de un solo Sabio | Regla 2 Sabios cross-family minima |
| Anunciar valor numérico en docs externos antes de B12a.4 verbatim en spec | Anti-fabricación recurrente (lección Perplexity 5 citas) |
| Mantener métrica numérica residual fuera del Anexo A.4 si plazo vence sin B12a PASS | Coherencia spec única |

## §5 Reglas de no-degradación silenciosa

Si la métrica medida en B12a.4 resulta **inferior** al `96%` reclamado históricamente (p.ej. 80%, 65%, 40%), las reglas binarias son:

| Resultado medido | Regla binaria |
|------------------|---------------|
| ≥96% reducción de errores **y** <4% RAB falsos positivos | Métrica histórica validada empíricamente. Sustituir reclamo cualitativo con valor verbatim medido. T1 firma magna. |
| <96% **o** ≥4% (cualquiera de los dos) | Métrica histórica refutada empíricamente. Sustituir `96%/<4%` por valor real verbatim. NO sostener reclamo histórico. T1 firma magna sobre valor menor. |
| DORY_BENCH falla (runner crashea, datos corruptos, irreproducible) | B12a.1 NO PASS. Volver a `PASS_AS_B12c_PENDING_A` con razón verbatim. Renegociar plazo o aceptar terminal cualitativo. |
| Fixtures B7 no auditables (Sabio externo identifica fuga) | B12a.3 NO PASS. Suspender ejecución. Re-instanciar B7 PASS antes de re-ejecutar. |

## §6 Trazabilidad

| Campo | Valor |
|-------|-------|
| Decisión T1 origen | Prompt verbatim 2026-05-20 "MANUS E2 — B12 b⇒a EVIDENCE PACK" |
| Sección spec referenciada | `B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §7.2 (B12c.4) y §7.4 (B12c-E3) |
| Path canon target (post firma T1) | `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md` |
| Branch entrega | `control-tower/2026-05-20-b12-b-to-a-evidence-pack` |
| Criterio PASS asociado | B12c.4 (condición de reactivación firmada T1) |
| Auditor asociado | Sabio externo + T1 (firma final) |

## §7 Firma magna pendiente

Este artefacto entra en estado **EVIDENCE DRAFT** hasta que T1 firme verbatim el commit que lo introduce. La canonización efectiva del artefacto a `bridge/spec/` requiere firma magna T1 explícita y commit firmado en main (cuyo timing y ruta NO están en mi scope, son decisión binaria T1 después de auditar el evidence pack completo).

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
| No reactivo métrica silenciosamente | ✅ (§4 prohíbe binariamente) |
