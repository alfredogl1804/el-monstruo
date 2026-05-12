## Sprint MOBILE-REALIGNMENT-001 — Reorganización estructural app Flutter

Cierra deuda canonizada de `_INDEX.md §7.2` + `REPORTE_BINARIO §IX`. Pre-requisito obligatorio para Mobile 2-5.

**Spec firmado:** `bridge/sprints_propuestos/sprint_mobile_REALIGNMENT_001.md` (commit `4f477be`)
**Kickoff:** `bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_KICKOFF_2026_05_12.md`
**Addendum pre-T1 (inventario fresco):** `bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_ADDENDUM_INVENTARIO_FRESCO_2026_05_12.md`

## Resumen ejecutivo

Reorganización 100 por ciento sin rewrite. 6,220 LOC existentes preservados via renames + proxy/re-export. Estructura nueva canónica:

- `core/mensajeros/` (DSC-G-004 — services renombrados)
- `core/a2ui/` (paradigma A2UI vs GenUI antiguo)
- `core/theme/brand_dna.dart`
- `core/state/mode_provider.dart` (Riverpod toggle Daily/Cockpit)
- `core/transport/`, `core/crypto/` (stubs)
- `modes/daily/` (5 pantallas: Home, Threads, Pendientes, Conexiones, Perfil)
- `modes/cockpit/` (5 pantallas: MOC dashboard, FinOps, Sandbox, Memory, Embrion)
- `routing/mode_router.dart` (rutas dependen de modeProvider + 8 aliases legacy)
- `widgets/shell_scaffold.dart` refactor (BottomNav 5 tabs Daily / Drawer Cockpit + toggle gestual swipe-down 2 dedos)

## Tareas T1-T6 cerradas

| Tarea | Estado | Detalle |
|---|---|---|
| Inventario fresco | VERDE | CASO A — spec sigue 100 por ciento válido (PR 92 NO mergeado, 7 commits A2UI ausentes en main) |
| T1 renames DSC-G-004 | VERDE | 7 archivos `git mv` + 21 imports actualizados + 2 clases renombradas |
| T2 scaffolding core/ | VERDE | 5 paths canonizados creados (transport, a2ui proxy, components/, crypto stub, state) |
| T3 mode_provider | VERDE | 3/3 tests verde |
| T4 modes/ proxies | VERDE | 5 Daily + 5 Cockpit (proxy/re-export, features/ originales intactas) |
| T5 shell_scaffold | VERDE | 4/4 tests verde + toggle gestual + Cockpit Drawer |
| T6 mode_router | VERDE | 5/5 tests verde + 8 aliases legacy + redirect cross-mode |

## Verificación binaria

```
flutter analyze: 39 issues (CERO errores, 2 warnings preexistentes, 37 infos preexistentes)
flutter test: 13/13 verde
```

Baseline pre-sprint era 41 issues con 1 error (`MyApp` no class). Post-sprint: 39 issues, 0 errores. Mejora neta -2 issues -1 error.

## Incidente reportado al bridge

Durante el sprint, otro hilo Manus en el mismo Mac (que también firma como "Manus Hilo B") hizo `git reset HEAD~1` x2 + `git push -f` sobre mi branch dos veces, borrando temporalmente T2+T3 del remoto. Recuperé via reflog cada vez. Los force-push de este PR son legítimos (mi propio trabajo restaurado), no destrucción de trabajo ajeno. Reportado en `bridge/manus_to_cowork_MOBILE_REALIGNMENT_INVENTARIO_FRESCO_2026_05_12.md`.

## Próximo paso — T7 smoke binario en Mac de Alfredo (bloqueante humano)

```bash
cd ~/el-monstruo/apps/mobile
flutter clean && flutter pub get && flutter analyze
flutter build macos --debug
open build/macos/Build/Products/Debug/el_monstruo_app.app
```

Verificación binaria Alfredo:

- App levanta sin crashes
- BottomNav Daily muestra 5 tabs (Home, Threads, Pendientes, Conexiones, Perfil)
- Swipe-down con 2 dedos toggle a Cockpit (BottomNav desaparece, MOC dashboard aparece)
- Cockpit Drawer accesible con 6 entradas (MOC, FinOps, Sandbox, Memory, Embrion, A2UI)
- Long-press en logo del Drawer Cockpit vuelve a Daily

## Permiso de merge

PR limpio con tag `[MOBILE-REALIGNMENT-001]`. Cowork T2-A audita DSC-G-008 v2 antes de merge. **No directo a main** (regla 8 spec). Self-merge prohibido.

---

MOBILE-REALIGNMENT-001 — LISTO PARA SMOKE ALFREDO (T1-T6 verde 6/6 + 13/13 tests)
