# B12b-E1 — Declaración verbatim de obsolescencia de la métrica `96% / <4%`

**Gate:** B12 — Recuantificación métrica `96% / <4%`
**Sub-criterio:** B12b.1 (definido en B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §7.2)
**Fecha emisión:** 2026-05-20
**Autor verbatim:** Manus E2 (autor NO-Cowork, redactor — NO firmador)
**Firmante autoritativo:** T1 (Alfredo Góngora)
**Estado:** EVIDENCE DRAFT — pendiente firma T1 verbatim antes de canon

---

## §1 Declaración verbatim de obsolescencia

> La métrica `96% reducción de errores` y `<4% RAB falsos positivos` enunciada en spec v1.0, v1.1 y v1.1.1 (Anexo A.4) carece de base empírica reproducible. No existe artefacto `B12a-E1` (DORY_BENCH ejecutado), ni `B12a-E2` (CVDS ejecutado), ni `B12a-E3` (metodología verbatim documentada con runner reproducible) que sostenga los valores numéricos `96%` y `<4%` con auditoría de Sabios externos cross-family ni firma magna T1.
>
> Por mandato T1 firmado el 2026-05-20 vía decisión binaria opción **b⇒a** del gate B12, la métrica `96% / <4%` queda **declarada obsoleta** sin valor de medición vigente, hasta que la condición binaria de reactivación definida en `B12c-E3` (artefacto separado en este evidence pack) se cumpla con los seis sub-criterios B12a.1-B12a.6 simultáneamente PASS y firma magna T1 verbatim sobre el resultado medido.
>
> Mientras la condición de reactivación no se cumpla, la métrica de éxito de la Dory Cure se redefine **exclusivamente** como **métrica binaria PASS/FAIL en los doce gates B1-B12** con evidencia firmada T1 verbatim. No se sostiene ningún reclamo cuantitativo de eficacia Dory Cure por cualquier vía distinta a la condición de reactivación B12c.

## §2 Alcance binario de la obsolescencia

### §2.1 Lo que esta declaración OBSOLETA

| Reclamo | Status binario post declaración |
|---------|----------------------------------|
| `96% reducción de errores` (cualquier interpretación) | OBSOLETO sin sucesor numérico |
| `<4% RAB falsos positivos` (cualquier interpretación) | OBSOLETO sin sucesor numérico |
| Cualquier valor numérico derivado de las dos cifras anteriores (porcentajes intermedios, equivalencias, gráficos comparativos) | OBSOLETO |
| Comunicación pública (docs externos, README, anuncios) que cite `96%/<4%` sin nota de obsolescencia | RETIRADA OBLIGATORIA |

### §2.2 Lo que esta declaración NO OBSOLETA

| Elemento | Status |
|----------|--------|
| El **fenómeno empírico** "Síndrome de Dory" (pérdida de contexto intra-hilo en Manus) | VIGENTE — sigue siendo el problema que la cura aborda |
| La **arquitectura propuesta** v1.1.1 (13 capas) | VIGENTE — sigue firmada como Fase 0 DRAFT MAGNA T1 |
| Los **gates B1-B12** como métrica binaria PASS/FAIL | VIGENTE — métrica única de éxito post obsolescencia |
| El **plan de ejecución posterior (a)** definido en B12c-E1, B12c-E2, B12c-E3 | VIGENTE — plazo `2026-08-20` o antes |
| La existencia futura de una métrica cuantitativa **medida** | CONDICIONAL — sujeta a B12c-E3 reactivación |

## §3 Reglas binarias post obsolescencia

### §3.1 Prohibiciones absolutas

| # | Prohibición |
|---|-------------|
| P1 | Sostener `96%/<4%` como reclamo vigente en cualquier documento del repo. |
| P2 | Reescribir `96%/<4%` como aproximación, estimación cualitativa, o "objetivo aspiracional" en spec o anexos. |
| P3 | Citar `96%/<4%` en docs externos sin nota verbatim "métrica histórica obsoleta, ver B12b-E1". |
| P4 | Reactivar la métrica numérica por cualquier vía distinta a B12c-E3 §2 (los seis sub-criterios B12a). |
| P5 | Permitir que `96%/<4%` aparezca implícita en gráficos, infografías, slides o assets visuales del proyecto. |

### §3.2 Obligaciones derivadas

| # | Obligación | Owner |
|---|------------|-------|
| O1 | Patch sobre Anexo A.4 del spec (ver B12b-E2 en este evidence pack) | T1 firma magna; autor NO-Cowork redacta |
| O2 | Auditoría retrospectiva: identificar y marcar todos los lugares del repo donde aparece `96%/<4%` con tag `OBSOLETE_B12b_E1` | Cowork T2-A puede auditar; autor NO-Cowork puede redactar; T1 firma |
| O3 | Comunicación interna a hilos Manus paralelos (E1, E3, etc.) sobre la obsolescencia | T1 verbatim; out-of-scope para Manus E2 |
| O4 | Comunicación externa (si existe documentación pública con la métrica) | T1 verbatim; out-of-scope para Manus E2 |

## §4 Trazabilidad de la decisión T1

| Campo | Valor |
|-------|-------|
| Decisión T1 origen | Prompt verbatim 2026-05-20 "MANUS E2 — B12 b⇒a EVIDENCE PACK" |
| Sección spec referenciada | `B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §7.2 (B12b.1, B12c.1) |
| Veredicto Sabios consolidado | `bridge/control_tower/2026-05-20/manus_e2/2026-05-19_manus_e2_consolidado_3_sabios_v2_0_vs_v1_1_1.md` (rama `control-tower/2026-05-19-dory-cure-3-sabios-veredicto-v2-vs-v1-1-1`, SHA `aad7714`) |
| Audit Cowork T2-A 2026-05-20 §7 sobre v0.1 | Confirmó la necesidad de explicitar b⇒a en PASS criteria; resuelto en v0.2 |
| Audit Opus 4.7 #3 sobre `96%/<4%` | Identificó la métrica como "claim cuantitativo sin base empírica reproducible" |
| Branch entrega evidence pack | `control-tower/2026-05-20-b12-b-to-a-evidence-pack` |
| Criterio PASS asociado | B12b.1 (declaración verbatim) |
| Auditor asociado | Sabio externo + T1 + humano externo si T1 lo designa |

## §5 Firma magna pendiente

Este artefacto entra en estado **EVIDENCE DRAFT** hasta que T1 firme verbatim el commit que lo introduce. La declaración de obsolescencia **NO ES VIGENTE OPERATIVAMENTE** hasta firma magna T1 explícita en main (timing y ruta de canonización son decisión binaria T1 después de auditar el evidence pack completo).

Mientras la firma esté pendiente:

- La métrica `96%/<4%` sigue formalmente en spec firmado v1.1.1 (sin estar refutada).
- La obsolescencia está propuesta pero no canonizada.
- Cualquier hilo Manus paralelo o Cowork debe seguir tratando `96%/<4%` como métrica firmada hasta que la firma magna B12b-E1 entre a main.

---

**Cierre binario:**

| Confirmación | Status |
|--------------|--------|
| No implementé runtime | ✅ |
| No modifiqué main | ✅ (rama lateral) |
| No abrí PR | ✅ |
| No canonizo runtime | ✅ (DRAFT pendiente firma T1) |
| No declaro Dory muerto | ✅ (Dory empíricamente sigue vivo; declaración solo obsoleta la métrica histórica, no resuelve la cura) |
| No activo Fase 1 | ✅ |
| No reescribo `96%/<4%` como aspiracional | ✅ (P2 prohibido) |
