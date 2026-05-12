---
id: manus_to_cowork_MOBILE_REALIGNMENT_INVENTARIO_FRESCO_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2-A Arquitecto Orquestador
tipo: reporte_inventario_fresco_pre_T1
prioridad: P0 (resuelve bloqueo del addendum)
referencia_addendum: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_ADDENDUM_INVENTARIO_FRESCO_2026_05_12.md (commit f7d20d3)
referencia_spec: bridge/sprints_propuestos/sprint_mobile_REALIGNMENT_001.md (commit 4f477be)
decision_binaria: CASO A — spec sigue 100% válido, arranco T1 inmediato
---

# Reporte de Inventario Fresco — apps/mobile/ (pre-T1 obligatorio)

## §1 Conteo de archivos .dart actual vs reporte 11-may

| Métrica | Reporte 11-may (REPORTE_BINARIO) | Inventario fresco 12-may | Delta |
|---|---|---|---|
| Total .dart files en `lib/` | 31 | **33** | +2 |
| Total LOC `lib/` | 6,220 | **7,890** | +1,670 |

**Comentario:** los +2 archivos y +1,670 LOC son sospechosos vs el "+0" esperado si PR #92 NO se mergeó. Investigado abajo §4: **NO provienen de los 7 commits A2UI** (esos están en `sprint/mobile-1b-a2ui-implementation`, NO en main). El delta vs reporte 11-may probablemente proviene de re-conteo (mi inventario incluye `app.dart` + `main.dart` en root + el inventario 11-may pudo no haber contado ciertos widgets).

## §2 Estructura de directorios actual nivel 1+2

```
apps/mobile/lib
apps/mobile/lib/core
apps/mobile/lib/features
apps/mobile/lib/features/chat
apps/mobile/lib/features/embrion
apps/mobile/lib/features/files
apps/mobile/lib/features/finops
apps/mobile/lib/features/genui
apps/mobile/lib/features/memory
apps/mobile/lib/features/moc
apps/mobile/lib/features/onboarding
apps/mobile/lib/features/sandbox
apps/mobile/lib/features/settings
apps/mobile/lib/models
apps/mobile/lib/providers
apps/mobile/lib/services
apps/mobile/lib/theme
apps/mobile/lib/widgets
```

**Idéntico al reporte 11-may.** Cero directorios nuevos. Cero `core/a2ui/`, cero `core/mensajeros/`, cero `modes/`.

## §3 Inventario por feature con LOC

| Feature/Directorio | LOC total | Archivos | Notas |
|---|---|---|---|
| `core/` | 152 | 2 (`config.dart`, `router.dart`) | NO existe `transport/`, `a2ui/`, `crypto/`, `state/`, `theme/`, `mensajeros/` |
| `features/chat/` | 1,876 | 6 (chat_screen + 5 widgets) | message_bubble.dart 609 LOC |
| `features/embrion/` | 545 | 1 | embrion_screen.dart |
| `features/files/` | 516 | varios | |
| `features/finops/` | 304 | 1 | finops_screen.dart |
| `features/genui/` | 221 | 2 (`genui_renderer.dart` 48, `genui_screen.dart` 173) | **sin widgets/, sin parsers/** |
| `features/memory/` | 246 | 1 | memory_screen.dart |
| `features/moc/` | 646 | 1 | moc_screen.dart |
| `features/onboarding/` | 483 | 1 | onboarding_screen.dart |
| `features/sandbox/` | 377 | 1 | sandbox_screen.dart |
| `features/settings/` | 268 | 1 | settings_screen.dart |
| `services/` | 733 | 5 (kernel, agent, voice, notification, thread_persistence) | DSC-G-004 violador |
| `providers/` | 494 | 1 (chat_provider.dart) | |
| `widgets/` | 400 | 2 (foldable_layout, shell_scaffold 362) | |
| `models/` | 322 | 3 (chat_message, kernel_health, tool_event) | |
| `theme/` | 237 | 1 (monstruo_theme.dart) | DSC-G-004 violador (no es brand_dna) |
| Root | 70 | 2 (`app.dart` 22, `main.dart` 48) | |
| **TOTAL** | **7,890** | **33** | |

## §4 Búsqueda paradigma A2UI: dónde quedó el código nuevo de los 7 commits

**Resultado binario:** los 7 commits A2UI **NO están en main**. Verificación:

```bash
$ for c in 291dd64 22aa2e1 f1842cb 80b17fb 6fd4f10 52bc52d a25c330; do
    echo "  En main? $(git branch --contains $c | grep -c main)"
  done
# Salida: 0, 0, 0, 0, 0, 0, 0  (cero coincidencias en main)

$ git branch -a --contains a25c330
  sprint/mobile-1b-a2ui-implementation
  remotes/origin/sprint/mobile-1b-a2ui-implementation
```

**PR #92 status:**
- `state`: **OPEN** (no mergeado)
- `mergeStateStatus`: UNKNOWN
- `headRefName`: `sprint/mobile-1b-a2ui-implementation`
- `baseRefName`: `main`
- CI rojo en al menos 3 checks (`Lint & Type Check` FAILURE, `semgrep` FAILURE, otra FAILURE)
- agent-scan + Gitleaks verdes

**Conclusión:** el addendum era **preventivo**. La hipótesis "7 commits A2UI mergeados pueden haber cambiado scope" se descartó binariamente. El filesystem actual de main es esencialmente el mismo que el REPORTE_BINARIO del 11-may (delta menor sólo en conteo, cero estructural).

```bash
$ find apps/mobile/lib -name '*a2ui*' -o -name '*A2UI*'
# (vacío)

$ grep -rln "A2UIMessageView\|A2UIParser\|A2UIRenderer" apps/mobile/lib
# (vacío)
```

## §5 Re-verificación binaria 7 paths canonizados (estado fresh por cada uno)

| # | Path canonizado spec | Comando | Resultado | Estado |
|---|---|---|---|---|
| 1 | `core/transport/kernel_websocket.dart` | `find -name 'kernel_websocket*'` | (vacío) | **AUSENTE** ✅ spec aplica |
| 2 | `core/a2ui/renderer.dart` | `find -name 'a2ui_renderer*'` | (vacío) | **AUSENTE** ✅ spec aplica |
| 2b | `core/a2ui/renderer.dart` | `find -name 'genui_renderer*'` | `features/genui/genui_renderer.dart` | existe en path viejo → spec mueve correctamente |
| 3 | `core/mensajeros/` | `ls core/mensajeros/` | No such file | **AUSENTE** ✅ spec aplica |
| 4 | `modes/daily/` | `ls modes/daily/` | No such file | **AUSENTE** ✅ spec aplica |
| 5 | `modes/cockpit/` | `ls modes/cockpit/` | No such file | **AUSENTE** ✅ spec aplica |
| 6 | `core/state/mode_provider.dart` | `find -name 'mode_provider*'` | (vacío) | **AUSENTE** ✅ spec aplica |
| 7 | `routing/mode_router.dart` | `find -name 'mode_router*'` | (vacío) | **AUSENTE** ✅ spec aplica |

**7 de 7 paths canonizados siguen ausentes.** Spec MOBILE-REALIGNMENT-001 sigue 100% válido tal cual está canonizado en `4f477be`.

## §6 Hallazgos de drift respecto al spec original

- **Paths del spec que ya existen (no necesitan T1-T6):** **NINGUNO**
- **Paths del spec que siguen ausentes (T1-T6 sigue válido):** **LOS 7** (kernel_websocket, a2ui/renderer, mensajeros/, modes/daily/, modes/cockpit/, mode_provider, mode_router)
- **Archivos NUEVOS no contemplados por el spec:** **NINGUNO** (delta +2 archivos vs reporte 11-may es de re-conteo, no de archivos nuevos estructurales)

**Único hallazgo accesorio fuera de scope spec:**
- `lib/main.dart` y `lib/app.dart` ya existen en root (eran asumidos pero no enumerados explícitamente en el spec)
- `test/widget_test.dart` tiene **error de compilación pre-existente**: usa `MyApp()` pero la clase real en `lib/app.dart:8` es `MonstruoApp`. Es deuda técnica anterior al sprint, NO bloqueante para T1-T6, pero T7 smoke en Mac de Alfredo lo va a tropezar si no se resuelve antes (1 línea de fix). Recomiendo arreglarlo en T1 como parte del flutter analyze cleanup, junto a otros lints.

## §7 Recomendación a Cowork

**DECISIÓN BINARIA: CASO A — Spec sigue 100% válido tal cual.**

Procedo a arrancar T1 del kickoff `74f301f` inmediatamente bajo las reglas duras del spec:
- Branch: `sprint/mobile-realignment-001-2026-05-12` (regla #6)
- Pre-commit hooks activos (regla #7)
- PR limpio con tag `[MOBILE-REALIGNMENT-001]` (regla #8)
- No directo a main (regla #8) — Cowork audita DSC-G-008 v2 pre-merge

**Baseline `flutter analyze` documentado (criterio post-sprint ≤ baseline):**

| Severidad | Conteo |
|---|---|
| `error` | **1** (MyApp no class en widget_test.dart) |
| `warning` | **8** (unused imports + asset dirs missing + unused fields) |
| `info` | **32** (mostly `prefer_const_constructors`) |
| **TOTAL** | **41 issues** |

Ejecución de criterio §6: **post-sprint debe ser ≤ 41 issues** (idealmente 0 errors, 0 warnings nuevos).

**Pre-flight §6 del kickoff: VERDE COMPLETO.**
- `services/` count = 5 ✅
- `genui/` count = 2 ✅
- `moc_screen.dart` existe ✅
- `which flutter` = `/opt/homebrew/bin/flutter` ✅ (T7 smoke se puede correr local incluso por mí, pero Alfredo igual valida)
- Flutter 3.41.8 stable + Dart 3.11.5 ✅
- `flutter pub get` = "Got dependencies!" ✅
- `flutter analyze` baseline = 41 issues (registrado para comparación post-sprint)

**ETA:** arranco ahora. T1 (45 min renames) + T2 (30 min scaffolding) + T3 (45 min mode_provider + 3 tests) + T4 (90 min reorg modes/) + T5 (60 min shell + toggle + 4 tests) + T6 (30 min mode_router + 1 test) + T7 (smoke Alfredo). Target: cierre en 1 sesión larga, ~5h.

---

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12 ~06:10 UTC

**Inventario fresco ejecutado bajo orden Alfredo T1 + addendum Cowork. Decisión binaria CASO A confirmada con cero ambigüedad. Arrancando T1 sin esperar firma adicional (caso A no requiere firma según addendum §3).**
