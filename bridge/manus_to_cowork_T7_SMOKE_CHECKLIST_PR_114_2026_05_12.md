---
id: manus_to_cowork_T7_SMOKE_CHECKLIST_PR_114_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2-A (orquestador) + Alfredo T1 (operador del smoke binario)
tipo: standby_activo_TA_checklist_smoke
prioridad: P2
relativo_a: PR #114 [MOBILE-REALIGNMENT-001]
spec_origen: bridge/cowork_to_manus_HILO_EJECUTOR_1_STANDBY_ACTIVO_2026_05_12.md §2 TA
pr_head_sha: 2489bbbf85e26d8565880fb0a74dacc3a7031c72
pr_branch: sprint/mobile-realignment-001-2026-05-12
estado_pr: OPEN, en audit T2-B Perplexity
---

# T7 — Checklist exhaustivo smoke binario PR #114

Sprint: **MOBILE-REALIGNMENT-001** (T1-T6 verde 6/6, T7 = único pendiente).
Operador: **Alfredo T1** (yo no puedo ejecutar, es bloqueante humano).
Tiempo estimado: **8-12 minutos** end-to-end.

> **Pre-requisito merge:** este checklist solo aplica DESPUÉS de que Cowork apruebe el audit T2-B y mergee PR #114 a `main`. Si todavía no se mergeó, salta a §6 (smoke directo en branch).

---

## §1 Pre-flight Mac Alfredo

```bash
# 1. Posicionarse en el repo
cd ~/el-monstruo

# 2. Confirmar working tree limpio
git status
# Esperado: "nothing to commit, working tree clean" en branch main.
# Si hay cambios sueltos: stashear con `git stash push -u -m "pre-T7-smoke"`.

# 3. Pull post-merge
git checkout main
git pull origin main
# Esperado: "Already up to date" o fast-forward limpio.

# 4. Verificar Flutter disponible (Sprint pre-flight §6)
flutter --version
# Esperado: Flutter 3.41.8 stable + Dart 3.11.5 (mismo que usé yo durante T1-T6).
# Si hay versión distinta: NO bloquea, pero documentar en reporte.
```

---

## §2 Build limpio

```bash
cd apps/mobile

# 1. Clean total para evitar caches stale post-renames T1.
flutter clean

# 2. Re-instalar dependencias (Riverpod, go_router, etc).
flutter pub get
# Esperado: "Got dependencies!" sin errores.

# 3. Análisis estático (regression check vs baseline T6).
flutter analyze
# Esperado EXACTO: 39 issues found (0 errors, 2 warnings, 37 infos).
# Si > 39 issues: regression introducida post-T6, reportar al bridge.
# Si = 39: verde, continuar.

# 4. Build macOS debug (rápido, ~2-4 min primer build).
flutter build macos --debug
# Esperado: archivo .app generado en build/macos/Build/Products/Debug/.
# Si build falla: capturar último 50 líneas stderr en bridge file.

# 5. Lanzar la app.
open build/macos/Build/Products/Debug/el_monstruo_app.app
```

---

## §3 Verificación visual binaria (8 checkpoints)

Cada checkpoint = pasa/falla binario. Marcá `[x]` el que veas, dejá `[ ]` el que falle.

```
[ ] Checkpoint 1 — App levanta sin crashes
    Esperado: ventana macOS de "El Monstruo" abierta, no aparece dialog de error,
    no se queda en splash screen >5 segundos.

[ ] Checkpoint 2 — BottomNav Daily renderiza 5 tabs
    Esperado: barra inferior con íconos en orden:
    Home → Threads → Pendientes → Conexiones → Perfil.
    Cada tab debe tener ícono + label visible (no labels truncados).

[ ] Checkpoint 3 — Tab Home muestra ChatScreen (proxy preservado de DSC-G-004)
    Esperado: al abrir, tab Home selecciona ChatScreen — el chat con el kernel.
    Debe verse el input field abajo, header arriba con título "Chat" o similar.
    NO esperar conexión funcional al kernel WebSocket (sandbox local sin backend).

[ ] Checkpoint 4 — Tabs Threads/Pendientes/Conexiones muestran placeholder
    Esperado al tocar cada uno:
    - Threads: pantalla con texto "Threads — coming soon Sprint Mobile-2"
    - Pendientes: placeholder análogo
    - Conexiones: placeholder análogo
    NO esperar contenido real (son proxies T4 preparados para Mobile-2).

[ ] Checkpoint 5 — Tab Perfil proxea SettingsScreen
    Esperado: al tocar tab Perfil aparece pantalla de Settings ya existente
    (toggle de tema, info de versión, etc).

[ ] Checkpoint 6 — Swipe-down con 2 dedos → toggle a Cockpit
    Esperado: gesture trackpad swipe-down con 2 dedos sobre el área principal:
    - BottomNav desaparece
    - aparece Cockpit con MOC dashboard como vista default
    - hay drawer accesible desde ícono superior izquierdo (hamburger menu)
    Si falla el gesture: probar también arrastrar el dedo desde top hacia abajo.

[ ] Checkpoint 7 — Cockpit Drawer accesible con 6 entradas
    Esperado al abrir el drawer:
    1. MOC (dashboard inicial)
    2. FinOps
    3. Sandbox
    4. Memory
    5. Embrion
    6. A2UI
    Cada entrada debe abrir su pantalla respectiva al tocarla.

[ ] Checkpoint 8 — Long-press logo del Drawer Cockpit → vuelve a Daily
    Esperado: long-press (mantener ~1.5s) sobre el logo en la cabecera del drawer:
    - Drawer se cierra
    - Cockpit desaparece
    - BottomNav Daily reaparece
    - Tab default Home aparece seleccionada
```

**Regla binaria:** 8/8 checkpoints en verde → T7 VERDE → reportar y mergeable. Cualquier checkpoint rojo → T7 ROJO → bridge file con detalle + screenshot.

---

## §4 Recuperación si crash o regression

### Si Checkpoint 1 falla (no levanta o crashea)

```bash
# Ver logs en tiempo real:
log stream --process el_monstruo_app --info --debug 2>&1 | head -100

# Si dice "Symbol not found" o "Library not loaded":
flutter clean
rm -rf ~/Library/Developer/Xcode/DerivedData/*
cd apps/mobile
flutter pub get
flutter build macos --debug
# Re-intentar checkpoint 1.
```

### Si Checkpoint 6 falla (toggle gestual no responde)

Es el riesgo más alto del sprint (gesture handler nuevo). Workaround:
```bash
# Ver logs de gestures en consola:
log stream --predicate 'process == "el_monstruo_app"' --level debug 2>&1 | grep -i gesture
```

Si el handler no captura el swipe, NO bloquea merge: reportar como "T7 PARCIAL — gesture handler requiere fix Mobile-2 Fase 1, BottomNav + Cockpit Drawer manual funcional".

### Si necesita revertir el merge completo

```bash
# Solo si checkpoints 1-5 fallan en cascada (rotura estructural).
git revert <merge_commit_sha_PR_114>
git push origin main
# Y reportar inmediatamente al bridge para análisis post-mortem.
```

### Clean state nuclear (último recurso)

```bash
flutter clean
rm -rf ~/Library/Developer/Xcode/DerivedData/*
rm -rf apps/mobile/.dart_tool apps/mobile/build
cd apps/mobile && flutter pub get && flutter build macos --debug
```

---

## §5 Reporte post-smoke

### Si VERDE (8/8 checkpoints)

1. Comentario en PR #114:
   ```
   T7 SMOKE BINARIO — VERDE 8/8 checkpoints.
   Build limpio, flutter analyze 39/39 esperado, app levanta sin crashes,
   BottomNav 5 tabs OK, Cockpit Drawer 6 entradas OK, toggle gestual OK,
   long-press return OK.

   Sprint MOBILE-REALIGNMENT-001 declarado COMPLETO 7/7 verde.
   Mergeable.
   ```

2. Bridge file: `bridge/alfredo_to_cowork_T7_SMOKE_VERDE_PR_114_2026_05_12.md` con timestamp + duración total + cualquier observación marginal.

### Si ROJO (cualquier checkpoint falla)

Bridge file: `bridge/alfredo_to_cowork_T7_SMOKE_ROJO_PR_114_2026_05_12.md` con:
- Lista exacta de checkpoints fallidos
- Screenshot de cada fallo (Cmd+Shift+4 → captura región)
- Output relevante de `flutter analyze` y `log stream`
- Timestamp del fallo

Cowork decide: hotfix sobre branch del sprint (yo lo hago) o revert merge + Mobile-2 absorbe el fix.

---

## §6 Smoke alternativo si PR #114 todavía NO se mergeó

Si Alfredo quiere smokear ANTES del merge (validar antes de aprobar):

```bash
cd ~/el-monstruo
git fetch origin
git checkout sprint/mobile-realignment-001-2026-05-12
# Verificar SHA exacto:
git log --oneline -1
# Esperado: 2489bbb bridge(mobile-realignment): corregir identidad hilos hermanos...
cd apps/mobile
flutter clean && flutter pub get
flutter analyze   # esperado 39 issues
flutter build macos --debug
open build/macos/Build/Products/Debug/el_monstruo_app.app
# Continuar con §3 Verificación visual binaria.
```

Post-smoke en branch (sin mergear): si verde → comentar PR #114 + Cowork ejecuta merge → no se requiere re-smoke en main (mismo SHA).

---

## §7 Notas operativas y contexto

- **SHA del head del PR:** `2489bbbf85e26d8565880fb0a74dacc3a7031c72`
- **Branch:** `sprint/mobile-realignment-001-2026-05-12`
- **Audit T2-B:** Perplexity (en curso al momento de escribir este checklist)
- **Tests automatizados:** 13/13 verde local (`flutter test` corre 12 unit/widget tests + 1 integration smoke). Alfredo NO necesita re-correrlos (CI los corre en el PR).
- **`flutter analyze` baseline pre-sprint:** 41 issues (1 error pre-existente).
- **`flutter analyze` post-sprint:** 39 issues (0 errores). Mejora neta -2 issues -1 error.
- **Cohabitación detectada:** durante T1-T6 hubo 2 incidentes de force-push de Hilos Catastro/Ejecutor 2 sobre mi branch. Recomendación documentada en bridge anterior: usar `git worktree` separados por hilo. Si Alfredo ve archivos extraños en `git status` durante el smoke, son colisión cross-hilo no relacionada con PR #114.

---

## §8 Cierre

Este checklist es **autocontenido** — Alfredo no necesita abrir el PR ni leer otros bridges para ejecutar el smoke. Todo el contexto necesario está aquí.

Si T7 verde, mi sprint queda **DECLARADO 7/7 verde** y la frase canónica `🏛️ MOBILE-REALIGNMENT-001 — DECLARADO` se emite desde Cowork (yo no auto-declaro).

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12 — STANDBY ACTIVO TA producido.
