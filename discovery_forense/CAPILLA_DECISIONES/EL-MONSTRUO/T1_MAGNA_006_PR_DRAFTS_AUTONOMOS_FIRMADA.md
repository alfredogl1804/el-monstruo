<!-- aspiracional -->

**Estado:** Firmada (T1 magna).

> Nota: este archivo es el **contrato canónico firmado** del T1-MAGNA-006. La articulación canónica vive en `T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_PARA_FIRMA.md` (Manus B, 2026-05-26). El instrumento de firma binaria que llevó a la decisión vive en `MANIFIESTO_FIRMA_T1_PREFORJA_BINARIO.md` (Manus B, 2026-05-27). El marcador aspiracional satisface DSC-G-017 para que el hook no lo trate como contrato ejecutable pendiente.

---

id: T1-MAGNA-006-FIRMADA
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica_magna_firmada
referencia_articulacion: discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_PARA_FIRMA.md
referencia_instrumento_firma: discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/MANIFIESTO_FIRMA_T1_PREFORJA_BINARIO.md
estado: firmada
fecha_firma: 2026-05-27
firmante: alfredo_gongora (T1 magna, no delegable)
emitido_por: manus_b (Hilo B — sesión Cabina post-rebase #227 + smoke E2E)
validacion_tiempo_real: completada (2026-05-27 21:37 UTC sobre kernel /v1/genome/now/health binario_100=true)

---

# T1-MAGNA-006 — FIRMADA: Embrion produce patches en sandbox

## Decisión firmada

**Opción D — Sandbox patches con merge-back manual obligatorio.**

El embrion_loop puede generar artefactos materiales (patches con tests pasados, diffs unificados) en `bridge/embrion_patches/<thought_id>.json`, firmados por par crítico (DSC-MO-006). **El embrion NO abre Pull Requests directamente contra repos del Monstruo.** Los patches son sandbox: viven aislados, no contaminan git history. Manus o Cowork manualmente revisan y aplican los útiles convirtiéndolos en PRs.

## Bloque YAML firmado

```yaml
decision_t1_magna_006:
  pr_drafts_autonomos_modo_ganador: D
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  justificacion_corta: |
    Validación empírica antes de autoridad PR. El embrion lleva 209 ciclos sanos
    pero NUNCA ha producido un patch material. D permite probar capacidad de
    output sin riesgo de pollution git. Migración a C escalonada por evidencia.
  fecha_revision_30_dias: 2026-06-26
  criterio_migracion_a_C: |
    30 patches útiles consecutivos auditados por Cowork con ratio aceptación ≥80%
    en 30 días. Si pasa, se re-firma esta T1-006 en modo C con scope L0-L3.
  budget_max_iteraciones_diarias: 10
  budget_max_costo_diario_usd: 5
  rollback_si_falla: |
    Si 5 patches consecutivos rechazados por Cowork por calidad o seguridad,
    embrion vuelve automáticamente a Opción A (solo memoria, no patches).
    Evento: rollback_t1_006_to_A registrado en bridge/control_tower.
  formato_canonico_patch: bridge/embrion_patches/<thought_id>.json
  par_critico_firma_obligatoria: true  # DSC-MO-006
  whitelist_archivos_modificables: |
    Solo archivos en repos: el-monstruo, tablero-campana
    Solo paths: docs/**, bridge/**, kernel/embriones/**, tools/**
    NUNCA: .env*, secrets/**, migrations/**, deploy/**
  embrion_lee_propios_patches_como_contexto: false  # evita loop infinito
```

## Cómo se ejecuta T1-006 D

1. **Manus B abre sprint** `sprint_T1_006_EMBRION_SANDBOX_PATCHES.md` con scope:
   - Construir `tools/embrion_patch_writer.py` (~250 líneas)
   - Crear directorio `bridge/embrion_patches/` y schema JSON canonico
   - Wire del par crítico embrion para firma dual
   - Test sintético: embrion produce patch para issue trivial (ej: typo fix en docs)
   - Audit Cowork pre-cierre

2. **Plazo objetivo:** 1-2 días tras firma de T1-007 (que define dónde caen los outputs).

3. **Métricas de éxito 30 días:**
   - ≥30 patches generados
   - ≥80% ratio aceptación (Cowork audita y aplica como PR)
   - 0 incidentes P0/P1 derivados de patches embrion
   - 0 violaciones de whitelist

## Cruza con

- **T1-MAGNA-005 (firmada Opción D)** — Forja Enforce escalonado L0-L3 cubre receipts Merkle del par crítico embrion.
- **T1-MAGNA-007 (firmada Opción C)** — Los patches del embrion caen en `bridge/missions/<MISSION_ID>/3_executions/embrion_patches/` cuando hay misión activa, o `bridge/embrion_patches/` cuando son standalone.
- **DSC-MO-006** — par crítico embrion firma cada patch.
- **DSC-G-008 v2** — Cowork audita pre-aplicación.
- **DSC-S-006** — autonomy budget cubre el límite diario.

## Estado verificado al momento de firma

| Item | Estado |
|---|---|
| Kernel binario_100 | ✅ true (2026-05-27 21:37Z, 393KB) |
| Embrion-loop | ✅ active, 209 ciclos, sano post fix kimi-k2-6 |
| Modelos disponibles | ✅ gpt-5.5, claude-opus-4-7, gemini-3.1-pro-preview, sonar-reasoning-pro |
| T1-005 dependencia | ✅ firmada Opción D |
| T1-007 dependencia (estructura) | ⏳ firmada en simultáneo (mismo bloque) |

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de emisión:** 2026-05-27
**Sesión:** Cabina dual + post-rebase #227 + manifiesto T1 binario
**Articulación canónica original:** `T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_PARA_FIRMA.md` (Manus B, 2026-05-26)
**Recomendación de Hilo B (modo detractor):** Opción D — aceptada por firmante.
