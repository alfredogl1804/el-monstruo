---
id: DEUDA-ROTACION-ANTHROPIC-FINAL-001
fecha: 2026-05-12T09:10:00Z
emisor: Cowork T2-A (decisión T1 absoluta 2026-05-12 ~09:08 UTC "no vamos a rotar nada hasta el final cierralo asi")
severidad: P0 documental (NO bloquea operación)
estado: pendiente_T1_final_avance_magno
prioridad: crítica al cierre avance magno
---

# DEUDA T1 — Rotación ANTHROPIC_API_KEY pendiente hasta final avance magno

## Origen

Commit `972ea02` (2026-05-12 ~07:26 UTC) introdujo en `bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_FINAL_2026_05_12.md` línea 19 el prefijo truncado de la API key Anthropic actual del kernel:

```
| ANTHROPIC_API_KEY | Rotación completa | nueva key `sk-ant-api03-LWY9v2...buQtfgAA` seteada... |
```

Detectado por Cowork T2-A audit DSC-G-008 v3 §4 pre-firma declaración MEGA-CIERRE-HOY EJECUTOR 1.

Repo `alfredogl1804/el-monstruo` es público (`"private": false`).

## Decisión T1 absoluta

Alfredo T1 verbatim 2026-05-12 ~09:08 UTC: *"no vamos a rotar nada hasta el final cierralo asi"*.

**Cowork respeta T1 absoluto:** la key sigue activa hasta que T1 declare final del avance magno + autorice rotación. Cowork NO ejecuta:
- rotación proactiva de la key
- history rewrite del commit (riesgo coordinación con hilos paralelo)
- cleanup destructivo de archivos en `bridge/`

Cowork documenta el riesgo aceptado explicit en este ticket + en commit body de la declaración.

## Severidad real estimada

- **P0 doctrinal:** viola DSC-S-001 (cero credenciales en repo nunca) + DSC-S-002 (pre-commit gitleaks debió bloquear)
- **P2 técnico:** key truncada con `...` reduce explotabilidad práctica
  - Workspace fingerprinting parcial: prefijo `sk-ant-api03-LWY9v2` + sufijo `buQtfgAA` identifican cuenta
  - Espacio búsqueda interior: ~50^50 chars (impracticable bruteforce)
  - Side-channel timing analysis: posible pero requiere acceso adicional

## Acción al final del avance magno (Alfredo T1 decide cuándo)

1. **Rotar ANTHROPIC_API_KEY actual** vía Anthropic Console:
   - Generar nueva key
   - Actualizar `ANTHROPIC_API_KEY` env var en Railway `el-monstruo-kernel` service
   - Verificar binariamente con `curl /health` + log `llm_call_ok` post-redeploy
   - Revocar key vieja
2. **Cleanup archivos comprometidos:** Edit `bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_FINAL_2026_05_12.md` reemplazando prefijo por `[REDACTED]` + push commit nuevo
3. **History rewrite OPCIONAL:** si T1 decide limpiar el history, `git filter-branch` o `BFG Repo-Cleaner` + `git push --force` coordinado con todos los hilos pausados
4. **Activar regla gitleaks preventiva** (ver `GITLEAKS_TRUNCATED_KEY_PATTERN_001.md`)

## Trazabilidad

- Commit detectado: `972ea02` (`bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_FINAL_2026_05_12.md` línea 19)
- Declaración con caveat: `bridge/cowork_to_manus_DECLARACION_MEGA_CIERRE_HOY_EJECUTOR1_2026_05_12.md` §3 Caveat P0
- Decisión T1: chat session 2026-05-12 ~09:08 UTC verbatim
- DSC enforced: DSC-S-001 + DSC-S-002 + DSC-S-016 (anti-fabricación causalidad sin grep — audit binario Cowork detectó esto correctamente)
