<!-- lint_strict -->

# Sprint Mobile Realignment 001 — Reorganización Estructural App Flutter

**estado:** firme
**fecha_firma_T1:** 2026-05-12
**autor_borrador:** Cowork T2-A (cierre de deuda canonizada — REPORTE_BINARIO §IX declara este spec como pendiente)
**autorización_T1:** Alfredo 2026-05-12 ("dale tarea grande a hilo ejecutor 1 de la app de flutter")
**Hilo principal:** Manus Ejecutor 1 (refactor + reorg) + Cowork (audit pre-merge)
**ETA recalibrado:** 4-6 horas reales (200-400 LOC refactor + 600-800 LOC scaffolding nuevo)
**Objetivo Maestro:** #2 (Calidad Apple/Tesla) + #3 (Mínima complejidad necesaria) + #6 (Velocidad sin sacrificar calidad) + #14 (Guardián de los Objetivos — alinea código real con doctrina canonizada)
**Bloqueos pre-arranque:** ninguno — todos los inputs en main. Pre-requisito para Mobile 2-5 (sin Realignment, Mobile 2 daily fase 1 colisionaría con `features/chat/` actual)
**Resultado esperado:** App Flutter con estructura canonizada de Mobile 1 + APP_VISION v1.3, los 6,220 LOC existentes reorganizados a paths canónicos + toggle Daily/Cockpit operativo + naming alineado con DSC-G-004.

---

## 0. Procedencia

`memory/cowork/REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` §VIII Camino A verbatim:

> "Realignment Incremental (RECOMENDADO). Mantener los 6,220 LOC. Agregar lo crítico que falta sin destruir lo que funciona. Sprint 'Mobile Realignment 001': [...] ETA estimada: 1-2 sesiones Manus. 200-400 LOC refactor + 600-800 LOC nuevas."

`memory/cowork/REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` §IX verbatim:

> "Voy a producir en próximo turno (o este mismo si tengo turnos disponibles): Doc operativo: `bridge/sprint_MOBILE_REALIGNMENT_001.md` [...]"

`bridge/sprints_propuestos/_INDEX.md` §7.2 verbatim:

> "Sprint Mobile Realignment. REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md §VIII recomienda 'Camino A — Realignment Incremental' antes de continuar Mobile 2-5. Esto NO está en `sprints_propuestos/`. Necesita redacción explícita como `sprint_mobile_REALIGNMENT_001.md` antes de continuar Mobile."

Este spec cierra esa deuda. Es **pre-requisito obligatorio para Mobile 2-5** según REPORTE_BINARIO.

---

## 1. Audit pre-sprint — Divergencias detectadas

Resumen binario de divergencias canonizadas (REPORTE_BINARIO §I):

| Path canonizado (Mobile 1 spec) | Estado real | Acción Realignment |
|---|---|---|
| `core/transport/kernel_websocket.dart` | ❌ existe `services/kernel_service.dart` (389 LOC) | Move + rename |
| `core/a2ui/renderer.dart` | ❌ existe `features/genui/genui_renderer.dart` (48 LOC) | Move + rename |
| `core/mensajeros/` (DSC-G-004) | ❌ existe `services/` (3 archivos) | Rename directorio |
| `core/theme/brand_dna.dart` | ❌ existe `theme/monstruo_theme.dart` (237 LOC) | Move + rename O symlink |
| `core/crypto/` | ❌ NO existe | Crear stub (SMP queda para sprint posterior) |
| `core/state/mode_provider.dart` | ❌ NO existe | **Crear NUEVO con toggle Daily/Cockpit** |
| `modes/daily/home_screen.dart` | ❌ existe `features/chat/chat_screen.dart` (206 LOC) | Move + wrap |
| `modes/cockpit/moc_dashboard_screen.dart` | ❌ existe `features/moc/moc_screen.dart` (646 LOC) | Move + rename |
| `routing/mode_router.dart` | ❌ existe `core/router.dart` (91 LOC) sin distinción | Refactor + agregar Daily/Cockpit |

**Cero rewrite. 100% reorganización + scaffolding faltante.**

---

## 2. Tareas del Sprint (T1-T7)

### T1 — Renames físicos DSC-G-004 (45 min)

**perfil_riesgo:** write-safe (renames son reversibles + import updates atómicos)

Renombrar directorios + archivos violadores de DSC-G-004 ("NUNCA: service, handler, utils, helper, misc"):

```
apps/mobile/lib/
  services/ → core/mensajeros/
    kernel_service.dart → kernel_messenger.dart
    agent_service.dart → agent_messenger.dart
    voice_service.dart → voice_messenger.dart (stub)
    notification_service.dart → notification_messenger.dart
    thread_persistence.dart → thread_persistence.dart (no requiere rename, no es "service")
  theme/monstruo_theme.dart → core/theme/brand_dna.dart
  features/genui/ → core/a2ui/
    genui_renderer.dart → a2ui_renderer.dart
    genui_screen.dart → a2ui_screen.dart
```

**Criterios de cierre:** `cd apps/mobile && flutter analyze` retorna 0 errores tras renames. Todos los imports actualizados. Tests existentes siguen pasando (ej: si hay `test/widget_test.dart`).

### T2 — Crear scaffolding `core/` faltante (30 min)

**perfil_riesgo:** write-safe (archivos nuevos, no rompen nada existente)

```
apps/mobile/lib/core/
  transport/
    kernel_websocket.dart  (proxy hacia core/mensajeros/kernel_messenger.dart, mantiene API actual)
  a2ui/
    renderer.dart  (proxy o re-export de a2ui_renderer.dart movido en T1)
    components/   (directorio vacío con __init__-equivalent comment para futura expansión)
  crypto/
    smp_placeholder.dart  (stub con TODO Sprint Mobile-SMP-001, NO implementar SMP en este sprint)
  state/
    mode_provider.dart  (ver T3 — Riverpod provider para Daily/Cockpit)
```

**Criterios de cierre:** archivos creados + imports válidos + `flutter analyze` verde.

### T3 — `mode_provider.dart` con toggle Daily/Cockpit (45 min)

**perfil_riesgo:** write-safe (state management nuevo, no toca existente)

`apps/mobile/lib/core/state/mode_provider.dart`:

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

enum AppMode { daily, cockpit }

class ModeNotifier extends StateNotifier<AppMode> {
  ModeNotifier() : super(AppMode.daily);  // Default: Daily

  void toggle() => state = state == AppMode.daily ? AppMode.cockpit : AppMode.daily;
  void setMode(AppMode mode) => state = mode;
}

final modeProvider = StateNotifierProvider<ModeNotifier, AppMode>(
  (ref) => ModeNotifier(),
);
```

**Tests:** `test/core/state/mode_provider_test.dart` con 3 tests (default state, toggle, setMode).

**Criterios de cierre:** 3 tests verdes + provider importable desde features.

### T4 — Reorganizar features actuales en `modes/` (90 min)

**perfil_riesgo:** write-risky (mueve archivos productivos — más cuidado con imports)

```
apps/mobile/lib/modes/
  daily/
    home_screen.dart  (wrap de features/chat/chat_screen.dart actual)
    threads/
      threads_screen.dart  (NEW — placeholder con TextField "Coming soon Sprint Mobile-2")
    pendientes/
      pendientes_screen.dart  (NEW — placeholder)
    conexiones/
      conexiones_screen.dart  (NEW — placeholder)
    perfil/
      perfil_screen.dart  (proxy desde features/settings/settings_screen.dart)
  cockpit/
    moc_dashboard_screen.dart  (move desde features/moc/moc_screen.dart, RENAME)
    finops_screen.dart  (proxy desde features/finops/finops_screen.dart)
    sandbox_screen.dart  (proxy desde features/sandbox/sandbox_screen.dart)
    memory_screen.dart  (proxy desde features/memory/memory_screen.dart)
    embrion_screen.dart  (proxy desde features/embrion/embrion_screen.dart)
```

**Estrategia:** usar **proxy files** (re-export) en lugar de mover físicamente para preservar git history limpia y permitir rollback trivial. Archivos `features/` ORIGINALES quedan intactos hasta verificar que la app funciona.

**Criterios de cierre:** los 5 placeholders Daily + 5 proxies Cockpit creados, `flutter analyze` verde.

### T5 — `BottomNavigationBar Daily 5 tabs + Cockpit Dashboard` + Toggle gestual (60 min)

**perfil_riesgo:** write-risky (toca shell + navigation)

Refactor de `widgets/shell_scaffold.dart` (362 LOC actual) para:

1. Leer `modeProvider` de Riverpod
2. Si `AppMode.daily`: mostrar BottomNavigationBar con 5 tabs (Home, Threads, Pendientes, Conexiones, Perfil)
3. Si `AppMode.cockpit`: mostrar MOC Dashboard como home + Cockpit drawer con 5 features (finops/sandbox/memory/embrion/+ extensible)
4. **Toggle gestual:** swipe-down con 2 dedos OR long-press en logo → invoca `ref.read(modeProvider.notifier).toggle()`

**Tests:** `test/widgets/shell_scaffold_mode_test.dart` con 4 tests (default daily, toggle a cockpit, BottomNav rendering, gestos).

**Criterios de cierre:** app levanta en Daily mode por default + toggle funciona + 4 tests verdes.

### T6 — `routing/mode_router.dart` (30 min)

**perfil_riesgo:** write-safe (refactor de `core/router.dart` actual)

Refactor de `core/router.dart` (91 LOC) para que las rutas dependan del `modeProvider`:

- `/` → si Daily: HomeScreen del daily; si Cockpit: MOC Dashboard
- `/threads`, `/pendientes`, `/conexiones`, `/perfil` → solo accesibles en Daily
- `/cockpit/finops`, `/cockpit/sandbox`, etc → solo accesibles en Cockpit
- Si user navega a ruta no-disponible del modo actual: silent redirect con toggle implícito

**Criterios de cierre:** routing tests pasan + navegación cross-mode preservada.

### T7 — Smoke binario en Mac Alfredo (30 min — bloqueante humano)

**perfil_riesgo:** write-safe (operación local Alfredo)

```bash
cd ~/el-monstruo/apps/mobile
flutter clean
flutter pub get
flutter analyze
flutter build macos --debug
open build/macos/Build/Products/Debug/el_monstruo_app.app
```

**Verificación binaria Alfredo:**
- ¿App levanta sin crashes?
- ¿Toggle Daily/Cockpit responde a gesto?
- ¿BottomNavigationBar Daily muestra 5 tabs?
- ¿MOC Dashboard accesible vía toggle?

**Criterios de cierre:** Alfredo confirma "smoke verde" en chat O reporta bug específico al bridge.

---

## 3. Reglas duras del sprint

1. **NO tocar lógica de negocio** — solo movimiento de archivos + renames + scaffolding. El comportamiento observable debe ser idéntico post-sprint.
2. **NO borrar `features/` originales** hasta T7 verde — usar proxy/re-export para reversibilidad.
3. **NO implementar SMP** (queda para Sprint Mobile-SMP-001).
4. **NO implementar voice/ambient** (queda para Sprint Mobile-6).
5. **NO implementar Cronos** (queda para sprint magno posterior).
6. **Branch dedicada:** `sprint/mobile-realignment-001-2026-05-12` desde main HEAD actual.
7. **Pre-commit hooks obligatorios** (gitleaks + trufflehog + private-key).
8. **Permiso de merge:** PR limpio + tag `[MOBILE-REALIGNMENT-001]` + Cowork T2-A audita DSC-G-008 v2 antes de merge. **No directo a main** porque scope es grande (>200 LOC efectivos).
9. **Tests obligatorios** para T3 (mode_provider) + T5 (shell_scaffold modes) + T6 (mode_router).
10. **Si en pre-flight detectás bloqueante de skill Dart no resoluble en 30min, reportá honestamente al bridge** — regla anti-autoboicot canonizada por Hilo Catastro 2026-05-12 (75% reducción LOC por leer antes de inventar).

---

## 4. Pre-flight obligatorio

```bash
cd ~/el-monstruo
git status && git pull origin main
test -d apps/mobile/lib                          # esperado: existe
ls apps/mobile/lib/services/ | wc -l             # esperado: 5 archivos
ls apps/mobile/lib/features/genui/ | wc -l       # esperado: 2 archivos
ls apps/mobile/lib/features/moc/ | wc -l         # esperado: 1 archivo (moc_screen.dart 646 LOC)
which flutter                                     # SI NO DISPONIBLE en sandbox, T7 requiere Alfredo Mac
flutter --version                                 # esperado: stable channel 3.x+
cd apps/mobile && flutter pub get                # esperado: deps actualizadas
flutter analyze                                   # esperado: 0 issues PRE-sprint (baseline)
```

**Si pre-flight rojo:**
- Si `flutter` no disponible en sandbox: arrancá T1-T6 (no requieren build local), reportá T7 como bloqueante humano para Alfredo Mac
- Si `flutter analyze` muestra issues PRE-sprint: reportá baseline al bridge antes de tocar nada (los issues nuevos en post-sprint deben ser ≤ baseline)

---

## 5. Heads-up de skill Dart/Flutter

Tu skill primaria demostrada es **Python kernel + scheduler + migrations SQL**. Este sprint es **Dart/Flutter puro** — nuevo dominio para vos.

Reconocé honestamente al iniciar:
- Si **15-30 min en T1** sentís que no entendés cómo Flutter resuelve imports / Riverpod state / widget composition → reportá al bridge `bridge/manus_to_cowork_MOBILE_REALIGNMENT_SKILL_BLOCKED_2026_05_12.md` con scope específico que no podés ejecutar.
- Si avanzás bien T1+T2+T3 pero T4 con widgets complejos te traba → reportá honesto. Cowork puede partir T4-T6 a otro hilo o re-asignar.
- **NO inventes código Dart adivinando.** Mejor consultar docs Flutter oficial (https://docs.flutter.dev/) que producir código que no compila.

Patrón ejemplar reciente: Hilo Catastro al recibir MOBILE-2A se auto-evaluó como skill medio-bajo Dart y rechazó honestamente. Esa misma honestidad aplica acá.

---

## 6. Criterios de cierre verde (Sprint completo)

- Las 7 tareas en exit 0 con artifacts en `reports/` (donde aplique) o tests verdes.
- `flutter analyze` retorna ≤ issues baseline (ideal: 0).
- App levanta en Mac de Alfredo en modo Daily por default.
- Toggle gestual cambia a Cockpit.
- BottomNavigationBar Daily renderiza 5 tabs.
- MOC Dashboard accesible en Cockpit.
- `flutter test` pasa al menos 3+4+1 = 8 tests nuevos (T3 mode_provider + T5 shell + T6 router).
- Sprint cierra con frase canónica: `🏛️ MOBILE-REALIGNMENT-001 — DECLARADO (7/7 verde)`.
- `bridge/manus_to_cowork_REPORTE_MOBILE_REALIGNMENT_001_2026_05_12.md` con §1 Diff aplicado + §2 Tests + §3 Smoke binario Mac + §4 Side-effects + §5 Recomendación próximo sprint (Mobile 2 Daily Fase 1 ahora desbloqueado).

---

## 7. Owner

**Owner técnico principal:** Manus Hilo Ejecutor 1 (T1-T6 implementación)
**Owner arquitectónico:** Cowork T2-A (audit DSC-G-008 v2 pre-merge)
**Owner humano final:** Alfredo T1 (T7 smoke binario en Mac local — único con Xcode + Apple Developer cert)

---

## 8. Trazabilidad

- **Origen:** REPORTE_BINARIO §VIII Camino A (recomendación T2-A 2026-05-11) + _INDEX.md §7.2 (deuda declarada explícita)
- **Sprints anteriores que habilitan este:** Sprint MOBILE_1B A2UI (PR #92 mergeado) — el `genui_renderer.dart` que se mueve a `core/a2ui/` ya está testeado
- **Sprints que destraba después:** Mobile 2 (Daily Fase 1 stubs) + Mobile 3-5 (Cockpit Fase 1-3) — todos requieren estructura `modes/daily/` + `modes/cockpit/` que este sprint canoniza
- **Delta esperado Obj global:** +2-3 pts (Obj #2 Calidad Apple/Tesla + Obj #14 Guardián por alineación código-doctrina)

---

**Firma propuesta de cierre:** sólo válida si las 7 tareas pasan + flutter analyze verde + smoke binario Mac Alfredo confirmado + Cowork audita DSC-G-008 v2 verde. Sin las 4 condiciones, cierre queda en `🏛️ MOBILE-REALIGNMENT-001 — PIPELINE TÉCNICO DECLARADO` (DSC-G-014 distinción) y Mobile 2-5 sigue bloqueado.

---

**estado:** firme — autorización T1 Alfredo 2026-05-12 ("dale tarea grande a hilo ejecutor 1 de la app de flutter"). Kickoff a Manus Hilo Ejecutor 1 producido en `bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_KICKOFF_2026_05_12.md`.
