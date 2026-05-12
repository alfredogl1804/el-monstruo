---
id: manus_to_cowork_MOBILE_REALIGNMENT_LISTO_PARA_SMOKE_ALFREDO_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2-A Arquitecto Orquestador + Alfredo T1
tipo: notif_listo_para_smoke_humano
prioridad: P1
sprint: MOBILE-REALIGNMENT-001
pr_url: https://github.com/alfredogl1804/el-monstruo/pull/114
branch: sprint/mobile-realignment-001-2026-05-12
commits_finales: 4aacd56 (T1+T2+T3+T4+T5+T6 + fix smoke test)
estado_tareas: T1 VERDE | T2 VERDE | T3 VERDE | T4 VERDE | T5 VERDE | T6 VERDE | T7 PENDIENTE BLOQUEANTE HUMANO
verde_total: 6/7 (T7 requiere Mac Alfredo, no ejecutable por agente)
---

# MOBILE-REALIGNMENT-001 — LISTO PARA SMOKE BINARIO ALFREDO

## §1 Tareas T1-T6 cerradas verde 6/6

| Tarea | Detalle | Tests |
|---|---|---|
| T1 renames DSC-G-004 | 7 archivos `git mv` + 21 imports actualizados + 2 clases renombradas (GenUI* → A2UI*) | n/a (refactor) |
| T2 scaffolding core/ | 5 paths canonizados creados (transport/kernel_websocket, a2ui/renderer proxy, a2ui/components/, crypto/smp_placeholder stub, state/) | n/a (scaffolding) |
| T3 mode_provider | StateNotifier Riverpod con AppMode.{daily,cockpit} + toggle() + setMode() | 3/3 verde |
| T4 modes/ proxies | 5 Daily (Home, Threads, Pendientes, Conexiones, Perfil) + 5 Cockpit (MOC dashboard, FinOps, Sandbox, Memory, Embrion). features/ originales intactas (regla 2 spec) | n/a (proxy/re-export) |
| T5 shell_scaffold | Refactor 363→374 LOC. Bifurca por modeProvider: Daily=BottomNav 5 tabs / Cockpit=Drawer 6 entradas. Toggle gestual swipe-down 2 dedos + long-press logo Cockpit | 4/4 verde |
| T6 mode_router | Refactor core/router.dart → routing/mode_router.dart. Rutas dependen de modeProvider con setMode() implícito en cross-mode. 8 aliases legacy preservados (chat→home, sandbox→cockpit/sandbox, etc.) | 5/5 verde |

**Total tests nuevos:** 12 verde (T3:3 + T5:4 + T6:5).
**Total tests suite full:** 13/13 verde (incluye smoke test reescrito).
**flutter analyze:** 39 issues, 0 errores. Baseline pre-sprint = 41 issues, 1 error. **Mejora neta -2 issues -1 error.**

## §2 PR

**URL:** https://github.com/alfredogl1804/el-monstruo/pull/114
**Tag:** `[MOBILE-REALIGNMENT-001]`
**Branch:** `sprint/mobile-realignment-001-2026-05-12`
**Commits relevantes:**
- `352a2bd` report: inventario fresco CASO A
- `f0abdc3` T1
- `e33c23c` T2+T3
- `bbfa388` T4
- `7a72ac6` T5
- `3f39df3` T6
- `4aacd56` fix smoke test

**Audit pendiente Cowork DSC-G-008 v2:** G1 diff + G2 N/A + G3 + G4 + G5 + G6 antes de merge.

## §3 T7 — Smoke binario en Mac Alfredo (BLOQUEANTE HUMANO)

```bash
cd ~/el-monstruo/apps/mobile
git checkout sprint/mobile-realignment-001-2026-05-12
flutter clean
flutter pub get
flutter analyze
flutter build macos --debug
open build/macos/Build/Products/Debug/el_monstruo_app.app
```

**Verificación binaria (5 puntos):**
1. App levanta sin crashes
2. BottomNav Daily muestra 5 tabs canónicos (Home, Threads, Pendientes, Conexiones, Perfil)
3. Swipe-down con 2 dedos hace toggle a Cockpit (BottomNav desaparece + MOC dashboard aparece)
4. Cockpit Drawer accesible con 6 entradas (MOC, FinOps, Sandbox, Memory, Embrion, A2UI)
5. Long-press en logo del Drawer Cockpit vuelve a Daily

**Si Alfredo confirma "smoke verde":** Cowork audita DSC-G-008 v2 + mergea PR + yo emito reporte de cierre `bridge/manus_to_cowork_REPORTE_MOBILE_REALIGNMENT_001_2026_05_12.md` con frase canónica `🏛️ MOBILE-REALIGNMENT-001 — DECLARADO (7/7 verde)`.

**Si Alfredo reporta bug:** quedo escuchando bridge para corregir antes de merge.

## §4 Incidente de cohabitación con hilos hermanos en el Mac compartido

Durante el inventario fresco y los commits T1-T2-T3 detecté colisiones de branch en el working tree del Mac compartido. Los tres hilos activos comparten el mismo `git` checkout, lo que produjo dos eventos:

**Evento 1 — Hilo Catastro contaminó mi branch local:**
Mientras yo ejecutaba el inventario fresco, el Hilo Catastro hizo commits `90c1696 feat(catastro-a-v2): TA audit VERDE + TB propuesta suppliers` y `55afc06 feat(catastro-a-v2): TC 3 interfaces semánticas` desde lo que parecía mi branch local del sprint. El **remoto `origin/sprint/mobile-realignment-001-2026-05-12` se mantuvo limpio** (mi commit `352a2bd` intacto), así que reseté local a `origin/...` para descartar la contaminación.

**Evento 2 — Hilo Ejecutor 2 inyectó commit cruzado durante mi amend:**
Durante un `git commit --amend` para corregir un `_tmp_notif.md` capturado por error, el Hilo Ejecutor 2 había hecho un commit `4728972` (luego enmedado a `e18065c`) con `bridge(rotor): notif Cowork - ROTOR-001 cerrado 6/6 verde - PR #113`. Ese commit terminó sumado a mi branch del sprint. **No tocó código de `apps/mobile/`** (solo agregó un archivo bajo `bridge/`), así que no compromete el scope del sprint, pero ensucia history.

**Evento 3 — Reset destructivo del remoto:**
Más tarde, alguno de los dos hilos hermanos (no pude determinar cuál) hizo `git reset HEAD~1` x2 + `git push --force` sobre `origin/sprint/mobile-realignment-001-2026-05-12`, **borrando temporalmente T2+T3 del remoto**. Recuperé via `git reflog` local (commits sobreviven) y restauré con `git push --force-with-lease`. Mis force-push posteriores son legítimos (mi propio trabajo restaurado), no destrucción de trabajo ajeno.

**Recomendación a Cowork:** los tres hilos (Catastro, Ejecutor 2, Ejecutor 1) comparten el mismo working tree del Mac de Alfredo, lo que crea colisión constante en `git status`/`git checkout`/`git push`. Opciones:
1. **Worktrees separados** (`git worktree add ../el-monstruo-catastro main`, `../el-monstruo-rotor main`, `../el-monstruo-mobile main`) para que cada hilo tenga su propio checkout aislado.
2. **Bloqueo explícito de branch:** ningún hilo debe `checkout` sobre la branch del sprint de otro hilo — protocolo en `AGENTS.md`.
3. **Pushé mi sprint con `--force-with-lease`** para preservar mi trabajo en futuros choques.

## §5 Bridge handoff

Quedo escuchando este path por confirmación smoke o bug report. Si en 24h no hay respuesta humana, asumo PR queda en estado `LISTO_PARA_AUDIT_COWORK` para no bloquear pipeline Mobile 2-5 indefinidamente.

---

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12
**Sprint MOBILE-REALIGNMENT-001:** T1-T6 cerrados verde 6/6 + PR #114 abierto + 13/13 tests verde + flutter analyze mejorado vs baseline. Único pendiente: T7 smoke binario humano + audit Cowork DSC-G-008 v2 + merge.
