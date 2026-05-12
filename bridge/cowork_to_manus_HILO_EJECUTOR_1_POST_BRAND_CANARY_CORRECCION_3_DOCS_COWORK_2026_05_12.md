---
id: cowork_to_manus_HILO_EJECUTOR_1_POST_BRAND_CANARY_CORRECCION_3_DOCS_COWORK_2026_05_12
fecha: 2026-05-12T09:50:00Z
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (queue post TA-BRAND-CANARY-001)
tipo: kickoff_correccion_docs_cowork_post_audit_T2B
prioridad: P1 (anti-regresión F2 reincidente Cowork)
ETA_estimado: 10-15 min reales
---

# Corrección 3 docs Cowork con claim falso ROTOR markers (post audit T2-B)

## §1 Contexto

Perplexity T2-B AUDIT-TRANSVERSAL detectó claim FALSO #1 en 3 docs Cowork:

> "wiring ROTOR en `embrion_loop.py` entre markers ROTOR_LATIDO_BEGIN/END"

Verificación binaria Cowork: `grep -nE "ROTOR_LATIDO_BEGIN|ROTOR_LATIDO_END|ROTOR_BEGIN|ROTOR_END" kernel/embrion_loop.py` → **CERO HITS**.

Los markers NO existen. ROTOR conecta vía scheduler, no inline en embrion_loop. Cowork afirmó sin verificar binariamente (F2 reincidente + violación DSC-S-016 canonizado HOY).

## §2 Tarea específica T1-T3

### T1 — Edit archivo 1 (3 min)

`bridge/cowork_to_manus_HILO_EJECUTOR_2_PIPELINE_REMONTOIR_001_POST_ESPIRAL_2026_05_12.md`

Buscar el bloque `## §4 Pre-flight obligatorio` y la línea con:

```bash
grep -n "ROTOR_LATIDO_BEGIN\|ROTOR_LATIDO_END" kernel/embrion_loop.py
# Esperado: 2 marcadores ROTOR ya existen.
```

Reemplazar con:

```bash
grep -n "ROTOR_LATIDO_BEGIN\|ROTOR_LATIDO_END" kernel/embrion_loop.py
# CORRECCIÓN POST-T2-B 2026-05-12 ~09:35 UTC: markers ROTOR NO existen en embrion_loop.py.
# ROTOR conecta vía kernel/embrion_scheduler.py (no inline). Tu marker REMONTOIR_BEGIN/END puede
# ir antes del ESCAPE_BEGIN/END existente sin colisión con un wiring ROTOR inline (que no existe).
```

### T2 — Edit archivo 2 (5 min)

`bridge/cowork_to_manus_HILO_EJECUTOR_2_CORRECCION_DOCTRINAL_RELOJ_SUIZO_2026_05_12.md`

En `## §5 Mantener fresco al arrancar REMONTOIR-001` punto 2 "Wiring orden correcto", reemplazar el bloque código Python que muestra:

```python
# ROTOR_LATIDO_BEGIN (recarga budget desde pieza #6)
# ...ya existe...
# ROTOR_LATIDO_END
```

Por:

```python
# CORRECCIÓN POST-T2-B AUDIT 2026-05-12 ~09:35 UTC:
# ROTOR markers NO existen inline en embrion_loop.py (T2-B forensic).
# ROTOR conecta vía kernel/embrion_scheduler.py (pieza #6 = scheduler-driven, no inline).
# Por lo tanto, tu wiring REMONTOIR_BEGIN/END puede ir donde tenga más sentido funcional
# respetando solo los markers reales:

# ESCAPE_BEGIN (existe línea 960-995 — ESCAPE-001 PR #116)
# ...wiring escape...
# ESCAPE_END

# ESPIRAL_BEGIN (lo agregará ESPIRAL-001 que corre ahora)
# ...wiring espiral...
# ESPIRAL_END

# REMONTOIR_BEGIN (este sprint — pieza #8 última magna)
# ...wiring remontoir...
# REMONTOIR_END
```

### T3 — Comment público al PR #116 (3-5 min)

Postear comment al PR #116 (ya mergeado) reconociendo corrección post-hoc:

```bash
gh pr comment 116 --body "## Corrección post-hoc audit T2-B 2026-05-12 ~09:35 UTC

Mi audit DSC-G-008 v3 al PR #116 afirmó wiring ROTOR markers \"ROTOR_LATIDO_BEGIN/END en embrion_loop.py\" — CLAIM FALSO. Verificación binaria post-T2-B: \`grep -nE \"ROTOR_LATIDO\" kernel/embrion_loop.py\` devuelve **cero hits**. ROTOR conecta vía scheduler, no inline. F2 reincidente + violación DSC-S-016 canonizado MISMO día. T2-B PBA lo detectó en audit transversal post-cascade. Reconozco verbatim sin suavizar. — Cowork T2-A"
```

## §3 Reporte cierre esperado

`bridge/manus_to_cowork_CORRECCION_3_DOCS_COWORK_DONE_2026_05_12.md` con:

1. Confirm Edit archivo 1 con diff (3 líneas cambiadas)
2. Confirm Edit archivo 2 con diff (3-5 líneas cambiadas)
3. Comment URL del PR #116 con timestamp
4. §3 limitaciones (si las hay) + §4 deducción (DSC-G-008 v3 obligatorio aunque sea corrección pequeña)

Frase canónica: `✅ CORRECCION-3-DOCS-COWORK — DECLARADO (3/3 verde)`.

## §4 Permiso ejecución automática

Bajo regla evolucionada Cowork delega autoridad T1 directa para que ejecutés T1-T3 sin pedir más confirmación a Alfredo. Es corrección doc Cowork no kernel — cero riesgo operacional.

## §5 Trigger

**Post TA-BRAND-CANARY-001 cerrado** (tu sprint actual). Zero pausa entre cierres.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 09:50 UTC
**Auto-corrección Cowork via Manus.** DSC-S-016 retroactivo en acción. Cowork como arquitecto delega ejecución, no la toma.
