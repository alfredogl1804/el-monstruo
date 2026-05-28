<!-- aspiracional -->

**Estado:** Firmada (T1 magna).

> Nota: este archivo es el **contrato canónico firmado** del T1-MAGNA-007. La articulación canónica vive en `T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_PARA_FIRMA.md` (Manus B, 2026-05-26). El instrumento de firma binaria que llevó a la decisión vive en `MANIFIESTO_FIRMA_T1_PREFORJA_BINARIO.md` (Manus B, 2026-05-27). El marcador aspiracional satisface DSC-G-017 para que el hook no lo trate como contrato ejecutable pendiente.

---

id: T1-MAGNA-007-FIRMADA
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica_magna_firmada
referencia_articulacion: discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_PARA_FIRMA.md
referencia_instrumento_firma: discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/MANIFIESTO_FIRMA_T1_PREFORJA_BINARIO.md
estado: firmada
fecha_firma: 2026-05-27
firmante: alfredo_gongora (T1 magna, no delegable)
emitido_por: manus_b (Hilo B — sesión Cabina post-rebase #227 + smoke E2E)
validacion_tiempo_real: completada (2026-05-27 21:37 UTC sobre kernel /v1/genome/now/health binario_100=true)

---

# T1-MAGNA-007 — FIRMADA: Coexistencia jerárquica registry + missions + sprints_completados

## Decisión firmada

**Opción C — Coexistencia jerárquica.**

La unidad canónica de trabajo del Monstruo es el **SPRINT** (atado a `sprints/registry.yaml`, fuente única de verdad de Sprint 91.16). La **MISIÓN** (`bridge/missions/<MISSION_ID>/`) es la capa de ejecución viva que acompaña a un sprint cuando pasa a estado IN_PROGRESS. El histórico consolidado vive en `bridge/sprints_completados/`.

**No se rompe Sprint 91.16. No se reescribe doctrina. Se acepta la riqueza semántica de FORJA OMEGA en la capa de ejecución.**

## Bloque YAML firmado

```yaml
decision_t1_magna_007:
  evidence_pack_estructura_ganadora: C
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  justificacion_corta: |
    No rompe Sprint 91.16 ni la GitHub Action sprint-registry-validate.yml
    recién mergeada en PRs #213/#214. Permite captura de riqueza semántica
    FORJA OMEGA (un sprint con múltiples misiones paralelas) en la capa de
    ejecución sin tocar el manifiesto. Trazabilidad clara con 3 niveles.
  mission_id_schema: "<sprint_id>_<seq>"  # ej: MOBILE_0_SMP-01, MOBILE_0_SMP-02
  consolidador_obligatorio_al_cerrar: true
  dsc_g_008_v3_anexo_requerido: true
  rollback_si_falla: |
    Si el consolidador (que genera resumen sprints_completados al cerrar misión)
    falla 3 veces consecutivas, vuelta a Opción A (statu quo, solo bridge/sprints_*).
    Evento: rollback_t1_007_to_A registrado en bridge/control_tower.

estructura_canonica_3_niveles:
  nivel_1_manifiesto:
    archivo: sprints/registry.yaml
    rol: Fuente única de verdad de qué sprints existen, status, paradigm, OM, capa transversal
    validacion: GitHub Action sprint-registry-validate.yml (Sprint 91.16)
    intocable: true

  nivel_2_ejecucion_viva:
    directorio: bridge/missions/<MISSION_ID>/
    rol: Artefactos vivos de una ejecución concreta de un sprint
    estructura_subdirectorios:
      - 0_intent.md           # qué se va a hacer y por qué
      - 1_orders/             # production orders del operador
      - 2_assemblies/         # assemblies de embriones (par crítico)
      - 3_executions/         # diffs, patches, receipts, evidencia
      - 4_evidence/           # receipts Merkle (de T1-005 Opción D enforce L0-L3)
      - 5_court/              # verdicts del Sovereign Court
      - 6_outcomes.md         # resumen final de la misión
    creacion: cuando un sprint pasa de SIGNED a IN_PROGRESS

  nivel_3_historico:
    directorio: bridge/sprints_completados/
    archivo: <sprint_id>_<fecha>.md
    rol: Resumen consolidado del cierre + apuntadores a las misiones que lo ejecutaron
    archivo_misiones: bridge/missions/_archive/<MISSION_ID>.tar.gz
    generacion: automática vía consolidador al cerrar misión
```

## Cómo se ejecuta T1-007 C

### Sub-sprint A — Construir el consolidador (~150 líneas Python)

1. **Manus B abre sub-sprint** `sprint_T1_007_CONSOLIDADOR_MISSIONS.md` con scope:
   - `tools/missions_consolidator.py` que toma una misión cerrada y produce el resumen `sprints_completados/<sprint_id>_<fecha>.md`
   - Test: simula cierre de misión `T1_007_TEST_001`, verifica generación correcta del resumen
   - Hook git pre-merge: si una misión tiene status `closing`, exigir consolidador haya corrido

2. **Plazo objetivo:** 1 día tras merge de este sprint.

### Sub-sprint B — Anexo DSC-G-008 v3

1. **Cowork redacta y firma** DSC-G-008 v3 que extiende scope de audit pre-cierre a:
   - `bridge/sprints_completados/`
   - `bridge/missions/`
   - `bridge/embrion_patches/` (también desbloqueado por T1-006)

2. **Plazo objetivo:** 3-5 días.

### Sub-sprint C — Migración cero, adopción gradual

- **NO se mueven** archivos existentes en `bridge/sprints_propuestos/` ni `bridge/sprints_completados/`.
- **Se crea** `bridge/missions/` vacío con README explicando la nueva capa.
- **Sprints futuros** que arranquen post-merge de este T1-007 pueden generar misiones desde el día 1.

## Cruza con

- **T1-MAGNA-005 (firmada Opción D)** — Receipts Merkle de envelopes L0-L3 caen en `bridge/missions/<MISSION_ID>/4_evidence/`.
- **T1-MAGNA-006 (firmada Opción D)** — Patches del embrion caen en `bridge/missions/<MISSION_ID>/3_executions/embrion_patches/` cuando hay misión activa, o `bridge/embrion_patches/` cuando son standalone (sin sprint asignado).
- **Sprint 91.16** — `sprints/registry.yaml` sigue siendo el manifiesto canónico, intocable.
- **DSC-G-008 v2 → v3** — Cowork redacta v3 como sub-sprint derivado.
- **DSC-S-001..005** — cero secrets en bridge/missions/ (mismo enforcement que bridge/sprints_*).

## Estado verificado al momento de firma

| Item | Estado |
|---|---|
| `sprints/registry.yaml` | ✅ Sprint 91.16 canonizado, CI activa |
| `bridge/sprints_propuestos/` | ✅ ~50 archivos canonizados |
| `bridge/sprints_completados/` | ✅ existente |
| `bridge/missions/` | ⏳ pendiente creación post-merge |
| GitHub Action `sprint-registry-validate.yml` | ✅ mergeada PR #214 |
| FORJA OMEGA visual prompt | ⏳ desbloqueado tras merge de este T1-007 |

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de emisión:** 2026-05-27
**Sesión:** Cabina dual + post-rebase #227 + manifiesto T1 binario
**Articulación canónica original:** `T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_PARA_FIRMA.md` (Manus B, 2026-05-26)
**Recomendación de Hilo B (modo detractor):** Opción C — aceptada por firmante.
