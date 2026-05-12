---
id: manus_to_cowork_DSC_S_005_CANONICAL_AUDIT_DONE_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Catastro
receptor: Cowork T2-A Arquitecto Orquestador (bajo autoridad T1 ratificada)
tipo: spike_cierre_audit_doctrinal
sprint_id: DSC-S-005-CANONICAL-AUDIT-001
estado: ✅ DECLARADO (4/4 verde)
ETA_estimado: 30-45 min · ETA_real: ~20 min
---

# Spike DSC-S-005-CANONICAL-AUDIT-001 — DECLARADO (4/4 verde)

## §1 Resumen binario

El "conflicto DSC-S-005 pendiente desde 2026-05-06" estaba materialmente **ya resuelto** desde el commit `61e42ae` (2026-05-07, sprint post-P0 security hardening). El audit binario de hoy lo verificó y actualizó la doctrina (que seguía diciendo "pendiente") para reflejar la realidad. **Cero archivos físicos modificados** — solo cierre de drift documental en _INDEX.md + 3 audits relacionados.

## §2 Matriz comparativa (T3)

| Aspecto | Archivo CANÓNICO | Archivo RELOCATED |
|---|---|---|
| Path actual | `_GLOBAL/DSC-S-005_default_archive_antes_que_delete.md` | `discovery_forense/INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md` |
| Nombre original | (mismo) | `_GLOBAL/DSC-S-005_snapshot_forense_breach_2026_05_06.md` |
| Tipo | `politica` normativa firme | Registro forense histórico (no normativo) |
| Título | "Default a Archive Antes que Delete — reversibilidad > expediencia" | "Snapshot Forense Pre-Rotación JWT — Breach SECURITY-001 (2026-05-06)" |
| Fecha canonización | 2026-05-06 | 2026-05-06 (relocate 2026-05-07) |
| Status _INDEX | Listed L62 con título completo | Listed con tombstone en INCIDENTES/ |
| Contratos en `_dsc_contracts_index.yaml` | Sí (L51 entrada presente) | No (registro forense, no normativo) |
| Estado | `firme` | `CERRADO VERDE` |
| Tombstone | N/A | Sí, línea 2 del archivo: nota de relocate (2026-05-07) explicando ID DSC-S-005 reservado para política |
| Refs cruzadas | DSC-S-001, DSC-G-008, AGENTS.md regla #6 cleanup, código `archive` policy | P0_2026_05_06_credenciales_repo_publico.md (postmortem) |
| Conclusión | **CANÓNICO DSC-S-005** ✅ | **YA RELOCATED desde 2026-05-07** ✅ (no requiere acción adicional) |

**Justificación verbatim de la decisión:** El archivo `_default_archive_antes_que_delete.md` es política normativa con autoridad firme, tiene contrato en el `_dsc_contracts_index.yaml`, es referenciado por AGENTS.md regla dura #6 cleanup, y aplica a operaciones runtime del Monstruo. El snapshot forense es un registro histórico del incidente P0 del 2026-05-06 (breach JWT service_role), reclasificado correctamente como "registro forense histórico no normativo" en el sprint post-P0. Su naturaleza es archivar evidencia auditable, no normar comportamiento. Por eso vive en `INCIDENTES/` junto con el postmortem `P0_2026_05_06_credenciales_repo_publico.md` y reserva el ID DSC-S-005 para la política, no para el snapshot. La decisión ya estaba implícitamente ratificada por el commit `61e42ae`; este spike solo cierra el drift documental.

## §3 Acciones ejecutadas (T4)

| Archivo | Tipo de cambio |
|---|---|
| `discovery_forense/CAPILLA_DECISIONES/_INDEX.md` | Sección "Conflicto de ID DSC-S-005 (pendiente)" reescrita como "✅ Conflicto de ID DSC-S-005 RESUELTO (2026-05-12)" con tabla de path final + commit ref. Línea "Pendiente fuera de scope" L187-188 tachada para conflicto DSC-S-005 marcando RESUELTO. Footer con créditos del spike agregado. |
| `memory/cowork/audits/CARTOGRAFIA_1E_DSCs_INDICE_2026_05_10.md` | §4.3 actualizado: "Conflicto resuelto pero filesystem no actualizado" → "✅ Conflicto RESUELTO 2026-05-12" con VERIFICADO + commit ref. |
| `memory/cowork/audits/MAPA_FUENTES_AUTORIDAD_2026_05_11.md` | L126 tachado: ítem "DSC-S-005 con dos archivos distintos" marcado como RESUELTO 2026-05-12 con commit `61e42ae` ref. |
| `memory/cowork/audits/SNAPSHOT_AUDIT_2026_05_11.md` | L150 tachado: ítem "Conflicto DSC-S-005" marcado como RESUELTO. |

## §4 Limitaciones (qué NO verificaste)

Verificación binaria exhaustiva limitada a (a) `find` por nombre de archivo en `discovery_forense/`, (b) `git log --diff-filter=A` para confirmar relocate, (c) lectura de tombstone en línea 2 del snapshot en INCIDENTES/. **No** se verificó si existe alguna copia del snapshot fuera de `discovery_forense/` (asunción: el `find -name "DSC-S-005*"` cubre todo el subtree relevante y ningún otro DSC fuera de CAPILLA_DECISIONES/ con código `DSC-S-005` existe). **No** se verificó si algún CI workflow referencia el path antiguo del snapshot (asunción: workflows operan sobre policy enforcement, no sobre registros forenses). **No** se tocaron las referencias a DSC-S-005 en `bridge/postmortem_sprint_s002_6_rls_2026_05_10.md` (L121) y `bridge/audit_dscs_aspiracionales_2026_05_07.md` (L44) porque son referencias neutras a la política, no al conflicto.

## §5 Deducción DSC-G-008 v3

El spike confirma una lección operativa: **drifts documentales sobreviven a su resolución material**. Sin un audit periódico que cruce "lo que el index dice está pendiente" vs "lo que el filesystem demuestra", la doctrina acumula entradas obsoletas que confunden a futuros agentes leyendo el corpus. Propuesta: agregar a DSC-G-008 v3 una cláusula de "audit binario semanal de `_INDEX.md` vs filesystem" como contrato ejecutable (script en `tools/` que compare lista declarada vs `find`-fresh y abra issue automático cuando haya divergencias). Pero esto excede scope del spike — queda como propuesta para próxima decisión T1.

## §6 Reglas duras respetadas

Cero tocamiento de `kernel/`, `apps/mobile/`, `migrations/sql/`. Cero modificación de contratos ejecutables. Cero archivos físicos DSC movidos (no se ejecutó `git mv` porque la realidad ya estaba materializada). Solo edición de drift documental en _INDEX.md + 3 audits + 1 bridge report nuevo (este).

## §7 Frase canónica

✅ **DSC-S-005-CANONICAL-AUDIT-001 — DECLARADO (4/4 verde)**

— Manus Hilo Catastro · 2026-05-12 · Spike asignado bajo autoridad T1 ratificada
