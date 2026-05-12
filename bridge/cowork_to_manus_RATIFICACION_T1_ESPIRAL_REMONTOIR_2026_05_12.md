---
id: cowork_to_manus_RATIFICACION_T1_ESPIRAL_REMONTOIR_2026_05_12
fecha: 2026-05-12T08:38:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 delegada ("si avanza" 2026-05-12)
receptor: Manus Hilo Ejecutor 2 + Catastro (informativo)
tipo: ratificacion_firma_T1
prioridad: P1
---

# Ratificación T1 simbólica de specs ESPIRAL-001 + REMONTOIR-001

## §1 Contexto

Dos specs magnos del Reloj Suizo fueron firmados T2-A bajo autoridad T1 delegada el 2026-05-12 ~08:10 UTC (commit `46f0ee6`):

- `bridge/sprints_propuestos/sprint_ESPIRAL_001_homeostasis_dinamica.md` (pieza #5 Hairspring)
- `bridge/sprints_propuestos/sprint_REMONTOIR_001_constant_force_quality.md` (pieza #8 Constant Force)

Alfredo T1 ratifica firma simbólica 2026-05-12 ~08:38 UTC con instrucción "si avanza" + autoriza Cowork ejecutar plan default. Esto da camino completo a Ejecutor 2 post-ESCAPE-001 merge.

## §2 Estado de ratificación

| Spec | Estado pre-ratificación | Estado post-ratificación |
|---|---|---|
| ESPIRAL-001 | FIRME T2-A (Cowork delegada) | **FIRME T1 ratificada** — Alfredo "si avanza" 2026-05-12 ~08:38 UTC |
| REMONTOIR-001 | FIRME T2-A (Cowork delegada) | **FIRME T1 ratificada** — Alfredo "si avanza" 2026-05-12 ~08:38 UTC |

Ambos specs siguen siendo gobernables por Alfredo T1 absoluto (puede revocar en cualquier turno). La ratificación simbólica habilita a Ejecutor 2 a tomar gate VERDE para arrancar cualquiera de los dos post-ESCAPE-001 sin esperar segundo round de firma.

## §3 Cadena de gates VERDE simbólicos para Ejecutor 2

1. **ROTOR-001** (PR #113) → mergeado pre-cierre ESCAPE — verde ✅
2. **ESCAPE-001** (PR #116) → esperando T2-B PBA + Cowork merge — amarillo ⏳
3. **ESPIRAL-001** → GATE VERDE post-ESCAPE merge — ratificada T1 ahora ✅
4. **REMONTOIR-001** → GATE VERDE post-ESPIRAL merge — ratificada T1 ahora ✅
5. **RUBIES-001** → spec sembrado paralelo este turno (pieza #7 expansión cache semántica) — cierra simbólicamente 8/8 piezas del Reloj Suizo

## §4 Acciones que NO requieren más ratificación T1

- Ejecutor 2 puede arrancar ESPIRAL-001 inmediatamente post-ESCAPE merge
- Ejecutor 2 puede arrancar REMONTOIR-001 inmediatamente post-ESPIRAL merge
- Cowork puede armar specs adicionales del Reloj Suizo (RUBIES-001 este turno; otros futuros) bajo regla evolutiva

## §5 Decisión T1 pendientes (NO bloquean ejecución)

- Telegram T3 valores explícitos Brand Engine canary (chat_id + window_hours + rate_limit) — solo Alfredo los tiene
- T7 smoke binario Mac PR #114 (Alfredo ejecuta en Mac local)
- DSC-MO-013 ROTOR pulse_seconds dinámico decisión D+30
- DSC-MO-014 ESCAPE pulse_interval dinámico decisión D+30
- DSC-MO-015 ESPIRAL sensitivity calibration policy decisión D+30
- DSC-MO-016 REMONTOIR quality_floor per-consumer policy decisión D+30

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 08:38 UTC, bajo ratificación T1 simbólica ("si avanza") 2026-05-12 ~08:38 UTC
**Gate VERDE simbólico:** ESPIRAL + REMONTOIR aprobados pipeline. Ejecutor 2 continþa post-ESCAPE merge sin esperar segunda ratificación T1.
