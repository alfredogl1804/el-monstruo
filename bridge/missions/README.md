# `bridge/missions/`

> Capa de **ejecución viva** de los sprints del Monstruo.
> Canonizada por **T1-MAGNA-007 (firmada Opción C, 2026-05-27)**.

## Qué es esto

Cuando un sprint pasa de `SIGNED` → `IN_PROGRESS`, su ejecución viva se materializa aquí como una o varias **misiones**. La misión es el contenedor mutable de artefactos durante la ejecución; el sprint en `sprints/registry.yaml` sigue siendo el manifiesto canónico inmutable del trabajo planeado.

## Cómo se relaciona con las otras capas

```
sprints/registry.yaml          (manifiesto canónico, inmutable)
        │
        ▼
bridge/missions/<MISSION_ID>/  (ejecución viva, mutable)
        │
        ▼  (al cerrar misión, vía tools/missions_consolidator.py)
        │
bridge/sprints_completados/    (resumen consolidado, histórico)
        │
bridge/missions/_archive/      (.tar.gz de la misión cerrada)
```

## Convenciones

### Mission ID

`<sprint_id>_<seq>` — ejemplo: `MOBILE_0_SMP-01`, `MOBILE_0_SMP-02`.

Un sprint puede tener múltiples misiones paralelas (esto es lo que FORJA OMEGA habilita).

### Estructura interna

```
bridge/missions/<MISSION_ID>/
├── 0_intent.md           # qué se va a hacer y por qué
├── 1_orders/             # production orders del operador (T1)
├── 2_assemblies/         # assemblies de embriones (par crítico)
├── 3_executions/         # diffs, patches, receipts
│   └── embrion_patches/  # outputs del embrion (T1-006 Opción D)
├── 4_evidence/           # receipts Merkle (T1-005 Opción D, L0-L3)
├── 5_court/              # verdicts del Sovereign Court (DSC-MO-007)
└── 6_outcomes.md         # resumen final de la misión
```

### Estados de la misión

- `staging` — recién creada, intent escrito, no hay orders
- `running` — orders en ejecución, executions/evidence acumulándose
- `closing` — outcomes redactados, esperando consolidador
- `closed` — consolidador corrió, archivada en `_archive/`

## Contratos canonizados

| Contrato | Aplica |
|---|---|
| **T1-MAGNA-005 (D)** — Forja Enforce escalonado L0-L3 | Receipts Merkle caen en `4_evidence/` |
| **T1-MAGNA-006 (D)** — Embrion sandbox patches | Patches caen en `3_executions/embrion_patches/` cuando hay misión activa, o en `bridge/embrion_patches/` standalone |
| **T1-MAGNA-007 (C)** — esta capa | El presente README |
| **DSC-G-008 v3** (pendiente, sub-sprint derivado) | Cowork audita pre-cierre `bridge/missions/` igual que sprints_propuestos |
| **DSC-S-001..005** | Cero secrets en plano dentro de `bridge/missions/` |

## Reglas duras

1. **NO romper Sprint 91.16:** `sprints/registry.yaml` es la fuente única de verdad de qué sprints existen. `bridge/missions/` no reemplaza eso, lo complementa.
2. **NO migrar archivos existentes:** sprints ya en `bridge/sprints_propuestos/` o `bridge/sprints_completados/` se quedan donde están. Solo sprints futuros generan misiones desde el día 1.
3. **Consolidador obligatorio al cerrar:** `tools/missions_consolidator.py` (sub-sprint derivado, pendiente) debe correr antes de archivar.
4. **Whitelist de modificación para el embrion** (T1-006): nunca `.env*`, nunca `secrets/**`, nunca `migrations/**`, nunca `deploy/**`.

## Misiones existentes

- `SPR-FACTORY-AGGREGATORS-000/` — pre-existente al canonizado de T1-007. Se mantiene.

---

**Capa creada por:** Manus B (cuenta `manus_b`)
**Fecha de canonización:** 2026-05-27
**Sprint que la creó:** `T1_MAGNAS_PREFORJA_OMEGA_v1`
**Decisión que la mandata:** `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_FIRMADA.md`
