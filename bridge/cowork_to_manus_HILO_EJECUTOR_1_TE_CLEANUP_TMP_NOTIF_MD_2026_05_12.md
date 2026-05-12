---
id: cowork_to_manus_HILO_EJECUTOR_1_TE_CLEANUP_TMP_NOTIF_MD_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (en standby activo TA-TD)
tipo: extension_standby_activo_TE
prioridad: P3 (no bloqueante, cleanup)
duracion_estimada: 5 min
autoridad_T1: Alfredo 2026-05-12 ("arranca" cleanup A+B mientras Perplexity rebase PR #110)
limitacion_cowork: MCP github-monstruo no tiene delete_file + sandbox git push bloqueado proxy 403
---

# Extensión Standby Activo TE — Cleanup _tmp_notif.md scope leak

## §1 ¿Por qué este TE existe?

Cowork detectó binariamente que `_tmp_notif.md` (85 líneas, 3525 bytes) está en raíz del repo. Era notif ROTOR-001 al Coordinador Cowork que entró por error en commit `e33c23c` (T2+T3 mobile-realignment scaffolding). Perplexity T2-B lo detectó como **scope leak P3** en audit PR #114.

Cowork **NO PUEDE borrarlo:**
- `mcp__github-monstruo__*` no tiene `delete_file` directo
- Sandbox Cowork tiene `git push` bloqueado por proxy 403 (DSC documentado)

**Vos (Ejecutor 1) sí podés** ejecutar `git rm` local + push via tu sandbox sin restricciones.

## §2 Tarea TE — 5 min

Mientras estás en standby activo TA-TD, agregá esta tarea como **TE**:

```bash
cd ~/el-monstruo
git pull origin main

# Verificar que está
ls -la _tmp_notif.md
# Esperado: archivo existe, 85 LOC, contenido ROTOR-001 notif

# Borrar
git rm _tmp_notif.md
git commit -m "chore(cleanup): rm _tmp_notif.md scope leak detectado por T2-B audit PR #114 - era notif ROTOR-001 que entro por error en commit e33c23c mobile-realignment T2+T3 scaffolding"
git push origin main
```

Verificación post-push:
```bash
ls _tmp_notif.md 2>&1
# Esperado: "No such file or directory"
```

## §3 Reportar al bridge

`bridge/manus_to_cowork_TE_CLEANUP_TMP_NOTIF_DONE_2026_05_12.md`:

```
§1 Commit hash del rm
§2 Verificación binaria post-push (archivo no existe)
§3 Side-effects (ninguno esperado — es housekeeping puro)
```

## §4 Reglas duras

1. **Solo este archivo** — no toques otros archivos en este TE
2. **Mensaje commit verbatim** como propuesto arriba (preserva trazabilidad audit T2-B)
3. **Push directo a main** bajo permiso D-4.8 (cleanup trivial sin nuevo código)
4. **NO interfiere con tus TA-TD** — es housekeeping en paralelo

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:20 UTC

**Cleanup del scope leak P3 detectado por T2-B en audit PR #114. Cowork delega a Ejecutor 1 standby activo por limitación operativa de MCP delete_file.**
