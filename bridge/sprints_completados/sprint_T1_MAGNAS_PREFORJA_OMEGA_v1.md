# Sprint T1-MAGNAS-PREFORJA-OMEGA v1 — Articulación de magnas pre-Forja Omega

**Estado:** PROPOSED — pendiente firmas T1 magnas de Alfredo + audit Cowork

**Objetivo:** Articular las T1 magnas pendientes pre-Forja-Omega y dejarlas listas para firma del operador, sin codear encima ni invadir competencias de Cowork o ChatGPT.

**ID:** `T1_MAGNAS_PREFORJA_OMEGA_v1`
**Status:** PROPOSED
**Paradigm:** decision_magna
**Capa transversal:** C0 (Cimientos Perpetuos / gobernanza)
**Objetivos Maestros impactados:** 1 (Soberanía), 3 (Mínima Complejidad), 7 (No Inventar Rueda), 9 (Transparencia)
**Articulado por:** Manus B (Hilo B — ejecutor técnico)
**Fecha de propuesta:** 2026-05-26
**Bloquea:** FORJA-OMEGA-VISUAL completo, autonomía agéntica del Monstruo, Factory Mode
**Precondición operativa:** issue `EMBRION_DOWN_2026_05_26_kimi_k2_6` en estado fix-nivel-1 aplicado

---

## Detonante

ChatGPT (sabio externo del Consejo) entregó al operador un prompt de 932 líneas titulado **FORJA OMEGA — Manifiesto Operativo de la Cadena de Producción Soberana del Monstruo**. La propuesta describe 12 motores cognitivo-ejecutivos para industrializar la producción del Monstruo (Intent Reactor, Production Order Engine, Embryo Assembly Lines, Sovereign Court, Evidence Conveyor, etc.).

Manus B audita el repo `el-monstruo`, el repo `tablero-campana`, y el kernel vivo en Railway antes de intentar cualquier ejecución. Hallazgos verificables:

1. **Forja v4 ya está construida al 70-80%** en `tablero-campana/server/forja/` (2,549 líneas TS, 4 archivos test E2E firmados, 8 tablas Drizzle, Ed25519 operativo, Power Lanes L0-L6 canonizados). Lo que ChatGPT presenta como "moonshot a construir" es en gran medida **redescubrimiento** del trabajo ya hecho.
2. **El Sprint Registry recién cerrado en Sprint 91.16** (PRs #213 #214 mergeados hace <24h) define `sprints/registry.yaml` como fuente única. La propuesta de ChatGPT de migrar todo a `bridge/missions/<MISSION_ID>/` rompe esa canonización si se acepta sin disciplina.
3. **El `embrion_loop` está caído** (8+ ciclos consecutivos fallando con `kimi-k2-6` catalog key mismatch). Activar cualquier flujo agéntico autónomo encima de un embrion roto es construir sobre arena.
4. **Faltan 3 firmas T1 magnas no delegables** que la propuesta FORJA OMEGA asume firmadas: (a) Forja shadow→enforce, (b) embrion creando PRs autónomos, (c) estructura del Evidence Pack (sprints vs missions).
5. **Falta DSC-S-012** (auth fail-closed + key rotation + revocación coordinada) como precondición de seguridad para enforce.

Conclusión de auditoría: **el ecosistema NO está listo para ejecutar FORJA OMEGA tal como ChatGPT la propuso**. Faltan firmas, hay un incidente P1 abierto, y hay riesgo alto de duplicar trabajo. La acción correcta es **articular las decisiones magnas pendientes** y dejarlas listas para firma, no codear encima.

## Objetivo

Garantizar que las decisiones T1 magnas pendientes pre-FORJA-OMEGA queden articuladas, registradas en el Sprint Registry, y commiteadas al repo `el-monstruo` con audit trail trazable, sin firmar por nadie distinto del operador ni invadir competencias canonizadas.

## Detalle del objetivo

Empacar en un solo entregable canonizable (este sprint) los 5 documentos que cierran los gaps de gobernanza pre-Forja-Omega:

1. **T1-MAGNA-005** — Forja v4 shadow → enforce (4 opciones A/B/C/D para firma Alfredo).
2. **T1-MAGNA-006** — Embrion crea Pull Requests Draft autónomos (4 opciones A/B/C/D para firma Alfredo).
3. **T1-MAGNA-007** — Estructura Evidence Pack: sprints vs missions (4 opciones A/B/C/D para firma Alfredo).
4. **Incidente P1** — `EMBRION_DOWN_2026_05_26_kimi_k2_6` con causa raíz, 4 niveles de fix, recomendación operativa.
5. **Anexo DSC-S-012** — Propuesta de auth fail-closed + key rotation + revocación coordinada para que Cowork audite y firme.

Total: 1,259 líneas de articulación rigurosa, schema-first, sin pirotecnia narrativa.

## Alcance

### Dentro del alcance

- Articular las 3 decisiones magnas con tabla comparativa criterio a criterio, recomendación detractor de Hilo B con justificación numerada, lo que se espera de Cowork como canonizador y de ChatGPT en iteración 002.
- Documentar el incidente embrion-down con evidencia técnica trazable (cycle_count, error literal, rutas de código).
- Preparar la propuesta DSC-S-012 con cláusulas concretas, tests de aceptación y matriz de cambios de código.
- Registrar este sprint en `sprints/registry.yaml` como `T1_MAGNAS_PREFORJA_OMEGA_v1` en estado PROPOSED.
- Abrir PR al repo `el-monstruo` con los 5 archivos en working tree.

### Fuera del alcance

- Firmar las T1 magnas (responsabilidad exclusiva de Alfredo).
- Firmar DSC-S-012 (responsabilidad de Cowork).
- Implementar fix nivel 3 del embrion-down (responsabilidad de Hilo B en sprint separado tras fix nivel 1 aplicado).
- Codear cualquier componente de Factory Mode / FORJA OMEGA (bloqueado hasta firmas T1).
- Migrar `bridge/sprints_*` a `bridge/missions/` (depende de T1-MAGNA-007 firmada).
- Activar enforce sobre Forja v4 (depende de T1-MAGNA-005 firmada).
- Habilitar PR autónomos del embrion (depende de T1-MAGNA-006 firmada y embrion sano).

## Tareas

1. Articular T1-MAGNA-005 con 4 opciones, recomendación detractor de Hilo B y bloque YAML para firma.
2. Articular T1-MAGNA-006 con 4 opciones, recomendación detractor y bloque YAML para firma.
3. Articular T1-MAGNA-007 con 4 opciones, recomendación detractor y bloque YAML para firma.
4. Documentar incidente P1 `EMBRION_DOWN_2026_05_26_kimi_k2_6` con causa raíz, evidencia y 4 niveles de fix.
5. Articular propuesta DSC-S-012 (anexo) como insumo para audit Cowork.
6. Registrar el sprint en `sprints/registry.yaml` como id `T1_MAGNAS_PREFORJA_OMEGA_v1` con paradigm `transversal` y capa `C0`.
7. Validar registry localmente con `python3 scripts/validate_sprint_registry.py`.
8. Crear branch `sprint-t1-magnas-preforja-omega-v1`, commit, push y abrir PR al repo `el-monstruo`.
9. Cerrar Thread Immunity Session con `CLOSE_CANONIZED` y canon registrado.
10. Entregar al operador los 5 archivos como input para sus firmas T1.

## Entregables (working tree → PR)

| # | Path | Líneas | Tipo |
|---|---|---|---|
| 1 | `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md` | 249 | Magna pendiente firma Alfredo |
| 2 | `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_PARA_FIRMA.md` | 303 | Magna pendiente firma Alfredo |
| 3 | `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_PARA_FIRMA.md` | 324 | Magna pendiente firma Alfredo |
| 4 | `discovery_forense/INCIDENTES/EMBRION_DOWN_2026_05_26_kimi_k2_6_catalog_key_mismatch.md` | 207 | Incidente P1 |
| 5 | `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/ANEXO_DSC_S_012_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md` | 176 | Propuesta para audit Cowork |
| 6 | `bridge/sprints_propuestos/sprint_T1_MAGNAS_PREFORJA_OMEGA_v1.md` | (este archivo) | Sprint canon |
| 7 | Entrada en `sprints/registry.yaml` | n/a | Manifiesto |

## Recomendación de orden de firma (Hilo B)

1. **Aplicar fix nivel 1 al embrion-down** (operativo, no requiere firma): Railway env var `EMBRION_CATASTRO_ENABLED=false`. 5 minutos. Desbloquea precondición operativa.
2. **Firmar T1-MAGNA-007 Opción C** (coexistencia jerárquica entre `sprints/registry.yaml` y `bridge/missions/`). Sin precondiciones, desbloquea las otras dos.
3. **Firmar T1-MAGNA-005 Opción D** (Forja escalonada por Power Lane: enforce L0-L3, shadow L4-L6 hasta DSC-S-012). Habilita receipts Merkle reales con riesgo controlado.
4. **Firmar T1-MAGNA-006 Opción D** (embrion produce patches en sandbox `bridge/embrion_patches/`, humano aplica). Empieza autonomía con riesgo bajo.
5. **Cowork audita y firma DSC-S-012** basado en el Anexo. Habilita ampliar Forja a L4-L6.
6. **30 días después**, evaluar migración T1-MAGNA-006 D → C con datos empíricos (¿el embrion produjo 30 patches útiles consecutivos?).

## Criterio de éxito del sprint

- Los 5 documentos en working tree del repo `el-monstruo`, commiteados en una rama y abiertos como PR.
- Entrada en `sprints/registry.yaml` con id `T1_MAGNAS_PREFORJA_OMEGA_v1`, status `PROPOSED`, paradigm `decision_magna`, capa transversal `C0`, OMs [1, 3, 7, 9].
- Validación local con `python3 scripts/validate_sprint_registry.py` retorna verde.
- PR mergeado a `main` (con audit Cowork si aplica DSC-G-008 v2).
- El operador recibe los 5 archivos como input para sus firmas T1.

## Criterios para pasar a estado SIGNED

Este sprint pasa a `SIGNED` cuando Alfredo firma **al menos una** de las tres T1 magnas con bloque YAML completado en el documento correspondiente. Si en 14 días no hay firmas, el sprint regresa a `BACKLOG` y se replantea.

## Criterios para pasar a estado DONE

Este sprint pasa a `DONE` cuando:

1. Las 3 T1 magnas están firmadas (cada una con su `decision_t1_magna_*` YAML completado).
2. El incidente embrion-down está cerrado (30 ciclos consecutivos sin error de modelo).
3. DSC-S-012 firmado por Cowork e indexado en `_dsc_contracts_index.yaml`.
4. Postmortem del sprint commiteado en `bridge/sprints_completados/sprint_T1_MAGNAS_PREFORJA_OMEGA_v1_<fecha>.md`.

## Lo que NO debe pasar al ejecutar este sprint

- **No firmar por Alfredo**. Manus B articula opciones, no decide magnas.
- **No firmar por Cowork**. La propuesta DSC-S-012 es insumo, no fait accompli.
- **No commitear claves privadas** (DSC-S-001..005). Todo lo commiteado es metadata pública.
- **No tocar `sprints/registry.yaml` para alterar sprints existentes**. Solo se agrega la entrada nueva del sprint.
- **No hacer claims sobre estado de FORJA OMEGA hasta que las T1 estén firmadas.** Aunque Forja v4 esté construida, sin firma queda en shadow.

## Justificación doctrinal

Este sprint cumple:

- **Obj #1 (Soberanía)**: rescata el orden de firma magna del operador como prerrogativa intransferible.
- **Obj #3 (Mínima Complejidad)**: empaca 5 documentos correlacionados en una sola unidad de trabajo en lugar de 5 sprints separados.
- **Obj #7 (No Inventar Rueda)**: detecta que ChatGPT propuso reinventar Forja v4 sin auditarlo y bloquea esa duplicación.
- **Obj #9 (Transparencia)**: documenta evidencia trazable del incidente P1 que el observatorio no detectó automáticamente.
- **DSC-G-008 v2**: aplicable al cierre del sprint con audit Cowork pre-cierre antes de mergear PR.
- **AGENTS.md Paso 0**: este sprint solo pudo articularse porque Manus B leyó el genome vivo `/v1/genome/now` antes de tocar nada.

## Anti-doctrina explícita

Este sprint NO ejecuta:

- ❌ Construir Factory Mode con datos vivos (requiere T1-MAGNA-005 firmada).
- ❌ Activar embrion para crear PRs (requiere T1-MAGNA-006 firmada + embrion sano).
- ❌ Migrar evidence pack (requiere T1-MAGNA-007 firmada).
- ❌ Reescribir Forja v4 (ya está construida; solo falta sacarla de shadow).
- ❌ Aceptar nomenclatura `mission` como canónica (depende de T1-MAGNA-007).
- ❌ Listar `kimi-k2-6` como modelo activo del Monstruo (anti-autoboicot — ya en producción rompiendo el embrion).

## Notas finales

Este sprint canoniza una verdad incómoda: **antes de codear FORJA OMEGA, debemos cerrar lo que ya construimos**. Es disciplina pre-construcción, no parálisis. La inversión total (artículación + PR) cabe en menos de 4 horas de Hilo B; el ROI es desbloquear 3 decisiones magnas y un incidente P1 que de otra manera quedan en estado fantasma.

El sprint asume que **Alfredo es el único que puede firmar T1**, **Cowork es el único que puede firmar DSCs**, y **Hilo B es quien articula y ejecuta**. Cualquier intento de subvertir esa división dejaría una firma huérfana sin trazabilidad doctrinal — eso es exactamente lo que `THREAD_IMMUNITY_GATE_v1` busca prevenir.

---

**Articulado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Thread Immunity Session de articulación:** 8af84475-598b-4d14-aa79-7d5e0c0c589c (cerrado con CLOSE_CANONIZED)
**Tiempo estimado de ejecución:** ~30 minutos (commit + PR; la articulación ya está hecha)
**Tiempo estimado para que el sprint cierre completo:** depende de cuándo Alfredo firma las T1 (no hay deadline impuesto)
