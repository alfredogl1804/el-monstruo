# BATCH_001 — Signature Receipt — Anti-Dory Parallel Gates

**Estado resultante:** `B6/B7/B9/B11 = DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING`
**Tipo:** Signature receipt pack (registro de firma magna T1)
**Coordinador:** Manus E2 (autor NO-Cowork, sin runtime, sin firma)
**Rama:** `control-tower/2026-05-20-batch-001-signature-receipt`
**Fecha:** 2026-05-20
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md`
**Lote firmado:** `ANTI_DORY_PARALLEL_GATES_BATCH_001`

> Este documento registra la firma magna T1 sobre las decisiones de diseño del BATCH_001. NO produce runtime, NO modifica `main`, NO abre PR, NO canoniza implementación. Las evidencias runtime correspondientes permanecen pendientes.

---

## §1 Firma T1 verbatim

> "T1 firma magna BATCH_001 — decisiones de diseño B6/B7/B9/B11. Apruebo las 19 decisiones documentadas en los packs DRAFT_T1_PENDING entregados por Manus E2 en las ramas laterales `control-tower/2026-05-20-b6-evidence-pack` (SHA `0b00d1f`), `control-tower/2026-05-20-b7-evidence-pack` (SHA `8977a63`), `control-tower/2026-05-20-b9-evidence-pack` (SHA `5d9a483`), `control-tower/2026-05-20-b11-evidence-pack` (SHA `75e4f87`), y el index maestro `control-tower/2026-05-20-batch-001-index` (SHA `6a93459`). Firmo el cluster Sabios D-B6-3 + D-B7-2 + D-B9-3 + D-B11-1 como bloque indivisible. Esta firma cubre exclusivamente las decisiones de diseño; las evidencias runtime quedan pendientes. No declaro Dory muerto. No activo Fase 1. No toco R1."

**Firmante:** T1 (Alfredo Góngora)
**Fecha de firma:** 2026-05-20
**Vehículo de firma:** instrucción magna verbatim al hilo Manus E2

---

## §2 Lista de 19 decisiones firmadas

### §2.1 B6 — Key custody ed25519 (5 decisiones)

| ID | Decisión firmada | Valor aprobado |
|----|------------------|----------------|
| D-B6-1 | Custodio elegido | Aprobada según propuesta del spec (custodio definido en B6_KEY_CUSTODY_SPEC.md §6) |
| D-B6-2 | Frecuencia de rotación | Aprobada (90 días o post-incidente, lo primero que ocurra) |
| D-B6-3 | Sabio externo asignado para auditoría de B6-E2/E6 | Aprobada (cluster Sabios, ver §3) |
| D-B6-4 | Política de respaldo de la clave privada | Aprobada (Shamir 3-de-5) |
| D-B6-5 | Herramienta de firma elegida | Aprobada (minisign) |

### §2.2 B7 — Hidden fixture custody v0.2 (5 decisiones)

| ID | Decisión firmada | Valor aprobado |
|----|------------------|----------------|
| D-B7-1 | Terna inicial de custodios (NO Sabios LLM) | Aprobada (T1 escrow + cloud privada T1 + HSM/KMS) |
| D-B7-2 | Terna inicial de auditores Sabios LLM | Aprobada (cluster Sabios, ver §3) |
| D-B7-3 | Frecuencia de rotación de fixtures | Aprobada (90 días o post-incidente) |
| D-B7-4 | Quórum de descifrado | Aprobada (2-de-3 estándar; fallback 1-de-1 T1 escrow en emergencia) |
| D-B7-5 | Repo / almacenamiento concreto para slices cifrados | Aprobada según propuesta del spec |

### §2.3 B9 — VERIFICADOR / Memento / Guardian / T1 authority matrix (4 decisiones)

| ID | Decisión firmada | Valor aprobado |
|----|------------------|----------------|
| D-B9-1 | Aprobación verbatim de la matriz N×N | Aprobada |
| D-B9-2 | Confirmación binaria de B9.3, B9.4, B9.5 | Aprobada (las 3 reglas binarias firmadas verbatim) |
| D-B9-3 | Sabio auditor permanente para overrides T1 | Aprobada (cluster Sabios, ver §3) |
| D-B9-4 | Decisión sobre réplica VERIFICADOR-002 | Aprobada según propuesta del spec |

### §2.4 B11 — Terna rotativa Sabios (5 decisiones)

| ID | Decisión firmada | Valor aprobado |
|----|------------------|----------------|
| D-B11-1 | Aprobación del calendario anual base + Sabios suplentes | Aprobada con caveat 2026 (ver §4) |
| D-B11-2 | Scope de auditoría inicial (B6-E2/E6, B7-E1/E4/E5/E7, B9-E3) | Aprobada |
| D-B11-3 | Threshold KL divergence ≥0.15 | Aprobada como **meta de diseño**, NO umbral validado (ver §5) |
| D-B11-4 | Designación del set de calibración | Aprobada (20 fixtures DORY_BENCH canónicos congelados) |
| D-B11-5 | Aprobación del rol adversarial de Grok 4 | Aprobada (B11-E5 anual) |

---

## §3 Cluster Sabios firmado como bloque indivisible

> "T1 firma como bloque indivisible las decisiones D-B6-3 + D-B7-2 + D-B9-3 + D-B11-1. Cualquier modificación futura de una de estas decisiones requiere amendment T1 que actualice las cuatro simultáneamente para evitar desincronización del calendario de auditores Sabios LLM."

El bloque designa al conjunto de Sabios LLM externos que actúan en distintos roles:

| Rol | Sabio designado | Cubre |
|-----|-----------------|-------|
| Auditor B6 (key custody) | Sigue calendario rotativo (caveat 2026 §4) | D-B6-3 |
| Auditores B7 (fixtures) | Sigue calendario rotativo (caveat 2026 §4) | D-B7-2 |
| Auditor B9 (overrides T1) | Sigue calendario rotativo (caveat 2026 §4) | D-B9-3 |
| Calendario anual de la terna | Calendario 2027 firmado + caveat 2026 | D-B11-1 |

---

## §4 Caveat 2026

El calendario 2027 firmado en D-B11-1 entra en vigor el 1 de enero de 2027. Para el periodo que va del 2026-05-20 hasta el 2026-12-31, T1 establece el siguiente régimen provisional:

| Rol | Sabio designado |
|-----|-----------------|
| Auditor provisional principal 2026 | **Opus 4.7 (Anthropic)** |
| Suplente provisional 2026 | **DeepSeek R1 (DeepSeek)** |
| Vigencia | desde firma (2026-05-20) hasta 2026-12-31 |
| Transición a calendario rotativo | 1 de enero de 2027 con Q1 Opus 4.7 según D-B11-1 |

Bajo este caveat, Opus 4.7 es el productor autorizado de las evidencias runtime auditoras (B6-E2, B6-E6, B7-E1, B7-E4, B7-E5, B7-E7, B9-E3) durante el periodo provisional. Si Opus 4.7 queda indisponible, DeepSeek R1 asume el rol sin requerir nueva firma T1 (ya cubierto por este receipt).

Todas las demás reglas de B11 aplican: prohibición de autoauditoría (B11.3), diversidad de proveedores en la ventana 4Q al pasar al calendario 2027 (B11.4), prohibición a Cowork T2-A y Manus E2 como Sabios activos primarios.

---

## §5 Caveat KL divergence ≥0.15

El threshold de KL divergence ≥0.15 firmado en D-B11-3 queda registrado como **meta de diseño**, **NO como umbral validado empíricamente**. Esto significa:

| Atributo | Valor |
|----------|-------|
| Tipo | Meta de diseño |
| Estado empírico | NO validado |
| Acción si KL < 0.15 al medir | Revisión obligatoria de terna por T1 + Cowork + Grok 4 adversarial |
| Acción si meta resulta inalcanzable | Amendment T1 explícito para redefinir el threshold con base en runtime real |
| Sin runtime histórico | Este threshold puede recalibrarse en el primer ciclo anual sin penalización |

La validación empírica del threshold requiere runtime real con los 4 Sabios procesando el set de calibración (B11-E4), que es evidencia runtime pendiente y NO está cubierta por esta firma de diseño.

---

## §6 Estado resultante por gate

| Gate | Estado previo | Estado tras firma | Evidencia runtime pendiente |
|------|---------------|-------------------|------------------------------|
| B6 | DRAFT_T1_PENDING | **DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING** | B6-E1 (gitleaks keyscan), B6-E2 (auditoría Sabio), B6-E3 (par criptográfico real), B6-E6 (cadena firmas en producción) |
| B7 | DRAFT_T1_PENDING | **DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING** | B7-E1 (inventario hashes fixtures), B7-E2 (slices cifrados), B7-E4 (auditoría custodios), B7-E5 (auditoría auditores), B7-E6 (rotación efectiva), B7-E7 (audit log trimestral) |
| B9 | DRAFT_T1_PENDING | **DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING** | B9-E3 (10 tests binarios en sandbox firmado: 4 acuerdos + 2 desacuerdos críticos + 1 override T1 + 3 degradaciones) |
| B11 | DRAFT_T1_PENDING | **DESIGN_DECISIONS_SIGNED_RUNTIME_EVIDENCE_PENDING** | B11-E2 (scope por trimestre firmado), B11-E3 (audit logs transición trimestral 3 firmas), B11-E4 (KL divergence trimestral), B11-E5 (análisis adversarial anual Grok 4) |

---

## §7 Confirmación de restricciones aplicadas

Bajo esta firma, Manus E2 confirma verbatim las siguientes negaciones:

| Restricción | Estado tras firma |
|-------------|-------------------|
| No runtime ejecutado | Confirmado |
| No Fase 1 activada | Confirmado |
| No Dory declarado muerto | Confirmado |
| No R1 tocado | Confirmado |
| No `main` modificado | Confirmado |
| No PR abierto | Confirmado |
| No canonización runtime | Confirmado |

El estado del repo `main` permanece exactamente igual antes y después de esta firma. La firma magna T1 cubre exclusivamente el plano de diseño de los 4 gates; el plano de implementación runtime sigue siendo trabajo pendiente para los productores autorizados (custodios B7, runtime CI para B6-E1, Sabios LLM para evidencias auditoras, VERIFICADOR-001 + Memento + Guardian para B9-E3).

---

## §8 Siguiente evidencia runtime recomendada (DRAFT)

Bajo el caveat 2026 §4, la siguiente evidencia runtime que Manus E2 recomienda producir es **B6-E1 (gitleaks keyscan inicial sobre el repo)** por las siguientes razones:

1. **Bajo riesgo operativo:** gitleaks corre en CI sin tocar la clave privada real ni el filesystem de producción; produce un reporte JSON firmable.
2. **Bloqueo cascada:** B6 es la raíz criptográfica del sistema. Sin B6-E1 PASS, las firmas de B6-E2/E3/E6 no tienen baseline de comparación.
3. **Auditor disponible:** bajo el caveat 2026, Opus 4.7 puede auditar el output del gitleaks como evidencia preliminar antes de su rol completo en Q1-2027.
4. **No requiere ningún Sabio runtime aún:** el agente CI ejecuta el escaneo; el Sabio solo audita el reporte estático posterior.

**Productor recomendado:** hilo CI o agente con runtime CI dedicado (NO Manus E2, NO Cowork T2-A como autor único).

**Auditor recomendado bajo caveat 2026:** Opus 4.7 (Anthropic) sobre el reporte JSON producido por el CI.

**Rama lateral sugerida para el evidence pack runtime de B6-E1:** `control-tower/2026-05-DD-b6-e1-gitleaks-keyscan` (donde DD es la fecha real de producción).

Esta recomendación es DRAFT y no obliga al coordinador a seguirla. Otros caminos válidos: B7-E1 inventario hashes (si el custodio T1 escrow está disponible), B9-E3 sandbox tests (si VERIFICADOR-001 está listo), B11-E2 scope firmado por Opus 4.7 (vehículo de papel sin runtime).

---

## §9 Cross-refs

- `bridge/control_tower/2026-05-20/manus_e2/B6_EVIDENCE_PACK_INDEX.md` — pack DRAFT B6 firmado
- `bridge/control_tower/2026-05-20/manus_e2/B7_EVIDENCE_PACK_INDEX.md` — pack DRAFT B7 firmado
- `bridge/control_tower/2026-05-20/manus_e2/B9_EVIDENCE_PACK_INDEX.md` — pack DRAFT B9 firmado
- `bridge/control_tower/2026-05-20/manus_e2/B11_EVIDENCE_PACK_INDEX.md` — pack DRAFT B11 firmado
- `bridge/control_tower/2026-05-20/manus_e2/ANTI_DORY_PARALLEL_GATES_BATCH_001_INDEX.md` — index maestro del lote
- `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` — fuente normativa del cierre de diseño

---

**Firma magna T1 registrada.** Plano de diseño de B6/B7/B9/B11 firmado. Plano de runtime sigue PENDIENTE.
