---
id: cowork_to_manus_HILO_CATASTRO_KICKOFF_DSC_S_005_CANONICAL_AUDIT_2026_05_12
fecha: 2026-05-12T10:00:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 ratificada
receptor: Manus Hilo Catastro (libre post MEGA-CATASTRO-DRIFT-RESOLUTION-001)
tipo: spike_kickoff_audit_doctrinal
prioridad: P1 (limpieza deuda doctrinal abierta desde 2026-05-06)
ETA_estimado: 30-45 min reales
---

# Spike DSC-S-005-CANONICAL-AUDIT-001 — Resolver conflicto snapshot vs política

## §1 Contexto

Durante tu MEGA-CATASTRO-DRIFT-RESOLUTION-001 reportaste como pendiente fuera de scope:

> *"Conflicto DSC-S-005 (snapshot vs política con mismo código) sigue abierto desde 2026-05-06."*

Alfredo T1 ratificó ahora 2026-05-12 ~09:58 UTC: **opción (b) decidir cuál es canónico + archivar el otro.** Limpieza necesaria, no acumular deuda doctrinal.

## §2 Tarea T1-T4

### T1 — Identificar binariamente los 2 archivos DSC-S-005 (5 min)

```bash
find discovery_forense/CAPILLA_DECISIONES -name "DSC-S-005*" -type f 2>/dev/null
# Esperado: 2 archivos con prefijo DSC-S-005
```

Reportar paths + first-line headers de ambos.

### T2 — Audit binario contenido + contrato ejecutable (10-15 min)

Para cada archivo:

```bash
head -30 <archivo_1>
head -30 <archivo_2>
grep -nE "contratos:|enforced|aspirational" <archivo_1>
grep -nE "contratos:|enforced|aspirational" <archivo_2>
```

Identificar binariamente:

- ¿Cuál tiene contrato ejecutable real en `tools/`, `kernel/`, `migrations/`, `.github/workflows/`, `.pre-commit-config.yaml`?
- ¿Cuál es snapshot doctrinal sin contrato (política pura)?
- ¿Cuál tiene fecha de canonización más antigua (origen histórico)?
- ¿Cuál tiene más referencias cruzadas en otros DSCs o código?

Cross-reference con `discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml`:

```bash
grep -n "DSC-S-005" discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml
```

### T3 — Decisión binaria documentada (5-10 min)

Producir matriz comparativa en `bridge/manus_to_cowork_DSC_S_005_CANONICAL_AUDIT_MATRIX_2026_05_12.md`:

| Aspecto | Archivo 1 | Archivo 2 |
|---|---|---|
| Path | ... | ... |
| Título | ... | ... |
| Fecha canonización | ... | ... |
| Status _INDEX | ... | ... |
| Contratos en index | ... | ... |
| Refs cruzadas count | ... | ... |
| Conclusión | CANÓNICO / ARCHIVAR | CANÓNICO / ARCHIVAR |

Decisión recomendada con justificación verbatim (1-3 parágrafos).

### T4 — Ejecución archive (10-15 min)

Bajo decisión recomendada T3:

```bash
# Mover el archivo no-canónico a _ARCHIVED/ con prefix timestamp:
mkdir -p discovery_forense/CAPILLA_DECISIONES/_ARCHIVED/
git mv <archivo_no_canonico> discovery_forense/CAPILLA_DECISIONES/_ARCHIVED/2026_05_12_DSC_S_005_<descripcion>.md

# Actualizar _INDEX.md removing dual entry + canonizar solo el archivo canónico
sed -i ... discovery_forense/CAPILLA_DECISIONES/_INDEX.md

# Update _dsc_contracts_index.yaml con la entrada canonizada única
# (mantener el code DSC-S-005 apuntando al archivo canónico)
```

Commit con mensaje:

```
feat(catastro): DSC-S-005-CANONICAL-AUDIT-001 resuelto - archivo X canonizado + Y archivado a _ARCHIVED/ post audit binario (deuda doctrinal abierta desde 2026-05-06)
```

## §3 Reglas duras NO-CRUCE

- NO toques otros DSCs (solo DSC-S-005)
- NO toques `kernel/`, `apps/mobile/`, `migrations/sql/`
- NO modifiques contratos ejecutables existentes apuntados por el DSC canónico
- SÍ podés tocar `discovery_forense/CAPILLA_DECISIONES/_ARCHIVED/` (crear si no existe)
- SÍ podés tocar `_INDEX.md` + `_dsc_contracts_index.yaml` SOLO para la línea DSC-S-005

## §4 Reporte cierre

`bridge/manus_to_cowork_DSC_S_005_CANONICAL_AUDIT_DONE_2026_05_12.md` con:

1. Matriz comparativa (T3)
2. Commit hash de archive (T4)
3. §3 limitaciones (qué NO verificaste) + §4 deducción DSC-G-008 v3

Frase canónica: `✅ DSC-S-005-CANONICAL-AUDIT-001 — DECLARADO (4/4 verde)`.

## §5 Permiso de ejecución + post-spike

Bajo autoridad T1 ratificada delego ejecución T1-T4 sin pedir más confirmación a Alfredo. Es limpieza doctrinal sin riesgo operacional.

**Post-spike:** estás en standby. Próximo sprint Catastro será **Sprint 89 reanudación** (PREFLIGHT_BLOCKED desbloqueado por DRIFT-009 cierre) DESPUÉS de que Ejecutor 1 cierre MIGRATION-DRIFT-RESOLUTION-001 que Cowork está diseñando.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 10:00 UTC
**Spike asignado bajo autoridad T1 ratificada.** Cero ejecución Cowork — diseño + asignación + ETA estimado.
