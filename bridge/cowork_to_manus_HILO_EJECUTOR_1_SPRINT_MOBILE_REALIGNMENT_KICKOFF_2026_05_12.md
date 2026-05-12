---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre tras cerrar S89 v2 Opción B VERDE commits 1bcb2c0 + a384df0)
tipo: kickoff_tarea_grande_flutter
prioridad: P1 (pre-requisito de Mobile 2-5 según REPORTE_BINARIO §VIII)
duracion_estimada: 4-6 horas reales (200-400 LOC refactor + 600-800 LOC scaffolding + 8+ tests)
autoridad_T1: Alfredo autorizó 2026-05-12 ("dale tarea grande a hilo ejecutor 1 de la app de flutter")
autoridad_T2: Cowork T2-A firma kickoff bajo delegación T1
spec_firmado: bridge/sprints_propuestos/sprint_mobile_REALIGNMENT_001.md (commit 4f477be, recién canonizado — cerraba deuda _INDEX.md §7.2 + REPORTE_BINARIO §IX)
fuentes_doctrinales:
  - memory/cowork/REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md §I divergencias detectadas + §VIII Camino A recomendación
  - docs/EL_MONSTRUO_APP_VISION_v1.md (1116 LOC — visión magna)
  - apps/mobile/lib/ (6,220 LOC en 31 archivos actuales — base que se reorganiza, NO se rewrite)
delta_esperado_obj_global: +2-3 pts (Obj #2 Calidad Apple/Tesla + Obj #14 Guardián por alineación código-doctrina)
---

# Kickoff Sprint Mobile Realignment 001 — Reorganización Estructural App Flutter

## §1 ¿Por qué este kickoff existe?

Cerraste S89 v2 Opción B con calidad ejemplar (1 tabla nueva + 3 vistas semánticas + scaffolding kernel/catastros/ + cero fragmentación de las 9 tablas productivas + handoff explícito a Catastro). Cascada D-3→D-4→D-5→D-6→S89 v2 completa.

**Próxima asignación: tarea grande Flutter.** Alfredo T1 lo ordenó binariamente. Spec recién canonizado en `bridge/sprints_propuestos/sprint_mobile_REALIGNMENT_001.md` (commit `4f477be`) cierra deuda explícita del `_INDEX.md §7.2` + REPORTE_BINARIO §IX que declaraban este spec como pendiente.

**Este documento NO duplica el spec.** Te apunta + reglas duras NO-CRUCE fresco + skill heads-up.

## §2 Documento principal a leer ANTES de tocar código

**Spec firmado completo (14.8 KB):** [`bridge/sprints_propuestos/sprint_mobile_REALIGNMENT_001.md`](sprints_propuestos/sprint_mobile_REALIGNMENT_001.md)

Contiene:
- §1 Audit pre-sprint: 9 divergencias canonizadas vs realidad (tabla binaria)
- §2 Tareas T1-T7 con perfil_riesgo + ETAs específicos
- §3 10 reglas duras
- §4 Pre-flight obligatorio (verificá ANTES de codear)
- §5 Heads-up de skill Dart explícito
- §6 Criterios de cierre verde

**Lectura adicional obligatoria:**
1. `memory/cowork/REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` §I tabla divergencias + §II inventario real 6,220 LOC + §VIII Camino A
2. `docs/EL_MONSTRUO_APP_VISION_v1.md` para entender por qué Daily/Cockpit existen como modos canónicos

## §3 Resumen ejecutivo del scope (para que veas la forma)

7 tareas T1-T7, ~4-6h reales:

| Tarea | Scope | LOC aprox | Tests | Riesgo |
|---|---|---|---|---|
| T1 | Renames DSC-G-004: `services/` → `core/mensajeros/`, `theme/monstruo_theme.dart` → `core/theme/brand_dna.dart`, `features/genui/` → `core/a2ui/` | +0 / refactor | ninguno nuevo | write-safe |
| T2 | Scaffolding `core/` faltante: `transport/`, `a2ui/`, `crypto/` (stub), `state/` | +100 | 0 | write-safe |
| T3 | `mode_provider.dart` con toggle Daily/Cockpit (Riverpod) | +50 | 3 | write-safe |
| T4 | Reorganizar features → `modes/daily/` + `modes/cockpit/` con proxies | +200 (placeholders) / refactor | 0 | write-risky |
| T5 | `BottomNavigationBar Daily 5 tabs` + Cockpit Drawer + toggle gestual en `shell_scaffold.dart` | refactor 362 LOC | 4 | write-risky |
| T6 | `routing/mode_router.dart` refactor de `core/router.dart` | +60 / refactor | 1+ | write-safe |
| T7 | Smoke binario en Mac Alfredo (bloqueante humano — vos NO podés ejecutar) | — | — | humano |

Total tests nuevos esperados: 8+.

## §4 Reglas duras NO-CRUCE (estado fresco 2026-05-12 ~05:25 UTC)

**5 hilos activos. NO tocar:**

1. **Ejecutor 2 trabajando en ROTOR-001** (kickoff `27c4568`, disparado por mí ahora) — `kernel/rotor/`, `kernel/embrion_loop.py`, `kernel/embrion_budget.py`, `kernel/embrion_scheduler.py`, `kernel/embrion_routes.py`. NO tocar nada del kernel.
2. **Perplexity T2-B verificación migration 0020** (prompt `d531ddd`) — `migrations/sql/0020*`, `embrion_validation_log` table. NO tocar.
3. **Catastro esperando handoff S89 v2 → Catastro-A v2** (kickoff `2a5dbc5`) — `kernel/catastros/`, `catastro_suppliers_humanos` table. NO tocar.
4. **PR #110 Perplexity** (`feat/t1-pre-response-hook-observe-only`) — `kernel/cowork_runtime/`. NO tocar.
5. **Brand Engine** (post-PAR_BICEFALO_001) — `kernel/embriones/brand_engine*`. NO tocar.

**SÍ podés tocar (TODO Flutter, cero kernel):**
- `apps/mobile/lib/` completo (refactor + reorg)
- `apps/mobile/test/` (tests nuevos)
- `apps/mobile/pubspec.yaml` (si necesitás agregar package — pero NO debería ser necesario)
- `bridge/` para reportes intermedios

**Cero overlap con kernel.** Es la primera asignación tuya 100% Flutter — territorio limpio.

## §5 Heads-up de skill Dart/Flutter (CRÍTICO)

Tu skill primaria demostrada en estos sprints es **Python kernel + scheduler + migrations SQL + vistas semánticas Postgres**. Hiciste D-2 a D-6 + Sprint 89 v2 con calidad ejemplar.

**Dart/Flutter es nuevo dominio para vos.** Diferencias clave que debés tener presentes:

- **Imports relativos vs absolutos:** Flutter usa `package:el_monstruo_app/...` no `from .modulo import x`
- **Riverpod state management:** `StateNotifier` + `ProviderScope` — similar a hooks de React pero típico Flutter
- **Widget tree composition:** todo es widget. `BottomNavigationBar`, `Scaffold`, `Drawer`, `IndexedStack` (para preservar state al cambiar tab)
- **flutter analyze** es tu equivalente a `mypy` + `ruff` combinados — ejecutalo ANTES de cada commit

**Patrón anti-autoboicot a respetar:**

Si **15-30 min en T1** sentís cualquiera de estos síntomas:
- No entendés cómo Flutter resuelve un import después del rename
- Riverpod state se siente extraño y no podés escribir el provider en 10 min
- Widget composition de BottomNavigationBar + IndexedStack te confunde

→ **Reportá honestamente** al bridge `bridge/manus_to_cowork_MOBILE_REALIGNMENT_SKILL_BLOCKED_2026_05_12.md` con scope específico que no podés. NO inventes código Dart adivinando.

**Patrón ejemplar reciente:** Hilo Catastro al recibir MOBILE-2A se auto-evaluó como skill medio-bajo Dart y rechazó honestamente (commit del 2026-05-12 ~04:35 UTC). Esa misma honestidad aplica acá. Cowork puede partir el sprint a otro hilo si vos no podés ejecutar T4-T6.

**Lo que SÍ debés saber:** la mayoría de T1+T2+T6 son renames + scaffolding + refactor de router (poco código nuevo). T3+T5 son los más Flutter-heavy. Si tu honestidad dice "puedo T1+T2+T6 pero no T3+T5", reportá y Cowork parte el sprint.

## §6 Pre-flight obligatorio (NO arrancar sin verde)

```bash
cd ~/el-monstruo
git status && git pull origin main
test -d apps/mobile/lib
ls apps/mobile/lib/services/ | wc -l               # esperado: 5
ls apps/mobile/lib/features/genui/ | wc -l         # esperado: 2
ls apps/mobile/lib/features/moc/moc_screen.dart    # esperado: existe
which flutter || echo "FLUTTER NO DISPONIBLE — T7 será bloqueante humano"
cd apps/mobile && flutter pub get 2>&1 | tail -5
flutter analyze 2>&1 | tail -20
```

**Si pre-flight rojo:** reportá `bridge/manus_to_cowork_MOBILE_REALIGNMENT_PREFLIGHT_BLOCKED_2026_05_12.md` con razón binaria. NO arranques en pre-flight rojo (lección que vos mismo viviste en S89 v1).

**Si `flutter` no disponible en sandbox:** podés ejecutar T1-T6 (todos los renames + tests con `flutter test` quizás vía CI), pero T7 smoke binario lo hace Alfredo en su Mac local. Reportá esto al bridge antes de codear para que Alfredo se prepare.

## §7 Cadencia esperada

- **Después de T1 cerrada** (renames): `bridge/manus_to_cowork_MOBILE_REALIGNMENT_T1_DONE_2026_05_12.md` con `flutter analyze` post-T1 verde
- **Después de T3 cerrada** (mode_provider + 3 tests): bridge intermedio
- **Después de T5 cerrada** (shell_scaffold con toggle + BottomNav): bridge intermedio + screenshot si podés generar
- **Antes de T7** (smoke Alfredo): `bridge/manus_to_cowork_MOBILE_REALIGNMENT_LISTO_PARA_SMOKE_ALFREDO_2026_05_12.md` con instrucciones de cómo Alfredo verifica + PR número
- **Sprint cerrado:** `bridge/manus_to_cowork_REPORTE_MOBILE_REALIGNMENT_001_2026_05_12.md` con frase canónica `🏛️ MOBILE-REALIGNMENT-001 — DECLARADO (7/7 verde)` solo si las 4 condiciones del spec §6 están verdes.

## §8 Permiso de merge

**Bajo regla evolucionada del merge 2026-05-11**:
- PR limpio con tag `[MOBILE-REALIGNMENT-001]`
- Cowork T2-A audita DSC-G-008 v2 antes de merge (G1 diff + G2 N/A + G3 + G4 + G5 + G6)
- **No directo a main** porque scope es grande (>200 LOC efectivos + tests + refactor widgets)
- **Self-merge prohibido** — Cowork mergea post-audit

## §9 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint MOBILE-REALIGNMENT-001 CERRADO. App Flutter reorganizada de paradigma chat-con-agente-IA a paradigma Daily/Cockpit canonizado por APP_VISION v1.3. 6,220 LOC existentes preservados via renames + proxies. Estructura nueva: core/mensajeros/ + core/a2ui/ + core/theme/brand_dna.dart + core/state/mode_provider.dart + modes/daily/ (5 tabs) + modes/cockpit/ (5 features). Toggle gestual operativo. flutter analyze verde. 8+ tests nuevos. Smoke binario Mac Alfredo confirmado. Mobile 2-5 DESBLOQUEADOS para próximos sprints.',
  'manus-hilo-ejecutor-1',
  9
);
```

## §10 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 ("dale tarea grande a hilo ejecutor 1 de la app de flutter")
- T2-A (Cowork) firma kickoff + canonización del spec ausente bajo delegación T1
- T3 (Hilo Ejecutor 1) ejecuta bajo reglas duras §4 + heads-up skill §5
- ETA realista: 4-6h reales con tu velocity demostrada (target: terminar en 1 sesión larga)

**Si en pre-flight detectás bloqueante de skill Dart o de filesystem (ej: `flutter` no en sandbox), reportá honestamente.** Cero presión para ejecutar más allá de tu skill real — la regla anti-autoboicot que vos mismo aplicaste en S89 v1 ("pre-flight rojo, NO arranco") aplica acá idéntica.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:30 UTC

**Sprint MOBILE-REALIGNMENT-001 cierra deuda canonizada del _INDEX.md §7.2 + REPORTE_BINARIO §IX. Es pre-requisito obligatorio para Mobile 2-5 (Daily fase 1 stubs + Cockpit fase 1-3). Sin esta reorganización, la app Flutter sigue divergente de APP_VISION v1.3 — el corazón visual del Monstruo. Tu skill kernel + tests demostrada permite refactor estructural limpio si la lógica Dart no te bloquea; si te bloquea, reportá honesto.**

**Encadenamiento canónico:**
```
Ejecutor 1: D-3 ✅ → D-4 ✅ → D-5 ✅ → D-6 ✅ → S89 v2 ✅ → MOBILE-REALIGNMENT-001 ⏳
Después del Realignment: Mobile 2 Daily Fase 1 stubs queda desbloqueado
```
