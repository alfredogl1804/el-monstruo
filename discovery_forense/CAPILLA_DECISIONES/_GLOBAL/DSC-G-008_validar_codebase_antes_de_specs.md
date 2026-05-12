---
id: DSC-G-008
proyecto: GLOBAL
tipo: antipatron
titulo: "Validar estado actual del codebase ANTES de escribir specs, ANTES de firmar cierre de sprints, Y al auditar PRs Cowork DEBE deducir consecuencias materiales de §3 limitaciones declaradas — no solo enumerarlas."
estado: firme (v3 ampliado post-incidente PR #115 PBA convergencia)
fecha: 2026-05-06 (v1) / 2026-05-06 (v2 ampliación post-P0) / 2026-05-12 (v3 ampliación post-PBA PR #115)
fecha_firma_T1: 2026-05-12 (v3 bajo autoridad delegada T1 + canonización Cowork T2-A)
fuentes:
  - repo:bridge/sprints_propuestos/sprint_mobile_1_esqueleto_flutter.md (incidente v1: detonó "validar antes de specs")
  - repo:apps/mobile/ (codebase ya avanzado que Cowork no investigó en v1)
  - repo:scripts/run_migration_*.py (incidente v2: scripts pusheados con DSN hardcoded firmados verdes en Sprint 51.5 sin audit de contenido)
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md (postmortem v2)
  - repo:bridge/perplexity_to_cowork_T2B_VERIFICACION_PR_115_S_CONTRATOS_001_2026_05_12.md (incidente v3 — Cowork omitió deducir 4 consecuencias materiales que T2-B extrajo)
cruza_con: [TODOS, DSC-S-001, DSC-S-002, DSC-S-003, DSC-S-004, DSC-S-005, DSC-MO-006 v1.1 PBA, DSC-G-010, DSC-S-016]
---

# Validar estado actual del codebase ANTES de specs, ANTES de cierre, Y deducir consecuencias materiales de §3 limitaciones en audits

## Decisión

**v1 (original 2026-05-06):** Antes de escribir spec de cualquier sprint que toque código existente, Cowork (o quien especifique) DEBE auditar el estado actual del codebase relevante con bash + Read. Sin audit explícito, las specs asumen incorrectamente "from scratch" cuando el código ya existe — produciendo trabajo ficticio que pierde tiempo de Manus al ejecutar y descubrir que la mitad del scope ya está hecho.

**v2 (ampliación 2026-05-06 post-incidente P0):** El audit obligatorio se extiende también al **cierre de sprint**. Cowork (o quien firme cierre) DEBE auditar el contenido de los archivos pusheados — no solo leer el reporte de Manus — antes de firmar verde. Sin audit de contenido, los cierres son falsos.

**v3 (ampliación 2026-05-12 post-incidente PR #115 PBA):** Al auditar PRs bajo PBA (DSC-MO-006 v1.1), **Cowork DEBE deducir consecuencias materiales de las §3 limitaciones declaradas** — no solo enumerarlas honestamente. Estructura mínima v3 del audit:

1. **§1 Audit pre-sprint** (v1 mantiene)
2. **§2 Audit de contenido pre-cierre** (v2 mantiene)
3. **§3 Limitaciones declaradas honestamente** — qué Cowork NO pudo verificar (sandbox sin DB, env vars faltantes, archivos no leídos, etc.)
4. **§4 Consecuencias materiales deducidas de §3** — NUEVA CLÁUSULA v3 — para cada limitación §3, Cowork DEBE responder explícitamente:
   - ¿Qué hallazgos materiales podrían existir y NO se detectarían bajo esta limitación?
   - ¿Qué tickets follow-up correspondería abrir?
   - ¿Qué condiciones T2-B (Perplexity) o T1 (Alfredo) deberían cerrar la limitación antes/después del merge?

Sin §4 explícito en el audit, **Cowork queda como pensador único bajo limitaciones honestas pero sin guardrail estructural** — PBA convergencia T2-B termina extrayendo lo que Cowork sin par no ve, y eso es derrota arquitectónica de Cowork como Arquitecto T2.

## Por qué v3

Detonado por PBA T2-B PR #115 S-CONTRATOS-001 2026-05-12 ~08:05 UTC. Cowork audit DSC-G-008 v2 reportó 6/6 VERDE con §3 declarado honestamente ("no verifiqué Supabase prod read-only desde sandbox, no ejecuté tests locales"). Perplexity T2-B verificó independientemente y **extrajo 4 caveats P1+P2+P2+P3** que Cowork NO había deducido de sus propias limitaciones:

- **P1 informativo** — CI rojo heredado de main (verificable con `gh pr checks` que Cowork no corrió pero podía deducir mencionar)
- **P2 doctrinal** — Parser `_check_e2e_evidence.py` permite FP `abc1234`, `Todo OK`, `0 passed` (deducible con `grep` del parser que Cowork no hizo)
- **P2 doctrinal** — Workflow trigger mal descrito por Cowork (`ready_for_review` inexistente — F2+F21 reincidente menor — deducible con `head` al YAML)
- **P3 menor** — Bypass label sin enforcement justificación body (deducible leyendo el workflow YAML completo)

Cowork tuvo TODAS las herramientas para deducir estos 4 caveats antes del PBA. Lo que faltó fue la disciplina estructural de **deducir consecuencias materiales de §3 limitaciones, no solo enumerarlas**. v3 canoniza esa disciplina.

## Implicaciones v3

### §4 Consecuencias materiales deducidas — formato obligatorio en audits

Formato verbatim en cada audit Cowork DSC-G-008:

```markdown
### §3 Limitaciones declaradas honestamente
- Limitación A: no verifiqué X desde sandbox.
- Limitación B: no ejecuté Y tests locales.
- Limitación C: no leí archivo Z completo (>500 LOC).

### §4 Consecuencias materiales deducidas de §3
Para cada limitación §3, qué podría existir y no se detectaría:

- **Limitación A → consecuencia material:** podría haber inconsistencia entre migration aplicada en prod y schema esperado. Mitigación: ejecutar query read-only Supabase MCP (15 segundos) verificando tabla+columnas+RLS+constraints. Si MCP no disponible, condición de merge: T2-B verifica.
- **Limitación B → consecuencia material:** tests podrían fallar localmente por dependency missing. Mitigación: pedir T2-B ejecutar tests en sandbox propio.
- **Limitación C → consecuencia material:** patrones prohibidos podrían existir en bytes no leídos. Mitigación: grep dirigido por patrón (`postgresql://`, `eyJ...`, `sk-`) más rápido que Read completo.

Las mitigaciones §4 DEBEN ejecutarse pre-merge o declararse como condición T2-B/T1 explícita post-merge.
```

### Aplicación retroactiva v3

- **PR #115 S-CONTRATOS-001 (2026-05-12 ~08:05 UTC):** ya mergeado commit `b59bc2a6` con 4 caveats T2-B verbatim — este DSC v3 canoniza la lección. Audit Cowork futuro de PRs análogos debe ejecutar §4 deducción antes de pedir T2-B PBA.
- **PRs futuros bajo PBA:** sin §4 explícito Cowork → ítem de audit → status candidato a regresión. T2-B PBA convergencia puede revertir si §4 omitido.
- **No retroactiva pre-PBA (antes 2026-05-12 ~07:00 UTC):** sin PBA activo §4 no era requisito estructural. PRs anteriores quedan con caveats post-mortem documentados.

## Estado de validación

**firme — v1 + v2 + v3 ampliados.** v1 fruto del incidente 2026-05-06 ("manus ejecuta sprints en 15 min ajusta tus estimaciones son magna y la aplicación de flutter no está en ceros ya está avanzada lo investigaste?"). v2 fruto del incidente P0 del mismo día (secrets hardcoded en repo público). v3 fruto del incidente PBA PR #115 del 2026-05-12 (Cowork omitió deducir 4 consecuencias materiales de §3 limitaciones, T2-B PBA las extrajo).

**Lección magna canonizada en v3:** ser honesto sobre limitaciones (§3) NO sustituye deducir consecuencias materiales de esas limitaciones (§4). Pensador único sin par no ve esas consecuencias estructuralmente. PBA convergencia detecta el gap. Cowork debe internalizar §4 antes del PBA, no después.
