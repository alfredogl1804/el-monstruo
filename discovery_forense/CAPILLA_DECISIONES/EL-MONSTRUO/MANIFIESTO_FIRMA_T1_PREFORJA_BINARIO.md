<!-- aspiracional -->

**Estado:** Aspiracional — instrumento de firma binaria, no es DSC.

> Nota: este archivo empaca en un solo documento las decisiones T1 magnas pendientes pre-FORJA-OMEGA. T1-005 ya fue firmada el 2026-05-27 (Opción D — Enforce escalonado L0-L3). Quedan pendientes T1-006 y T1-007. El marcador aspiracional satisface DSC-G-017 para que el hook no lo trate como contrato ejecutable pendiente.

---

id: MANIFIESTO-FIRMA-T1-PREFORJA-BINARIO
proyecto: EL-MONSTRUO
tipo: instrumento_firma_t1_magna_consolidado
referencias_articulacion:
  - discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_PARA_FIRMA.md
  - discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_PARA_FIRMA.md
estado: pendiente_firma
fecha_emision: 2026-05-27
emitido_por: manus_b (Hilo B — sesión Cabina Cowork+Manus, post-rebase #227)
validacion_tiempo_real: completada (2026-05-27 21:50 UTC)
firmante_requerido: alfredo_gongora (T1, no delegable)
bloquea: prompt_v2_FORJA_OMEGA_VISUAL

---

# MANIFIESTO BINARIO — Firmas T1 magnas pendientes pre-FORJA-OMEGA

## Estado verificado HOY (cross-check 2026-05-27 21:37 UTC)

| Item | Estado real verificado |
|---|---|
| Kernel `binario_100` | ✅ true, generated 2026-05-27 21:37Z, size 393 KB |
| Embrion-loop | ✅ **active**, cycle_count 209, thoughts_today 1, last_trigger reflexion_autonoma — **sano** |
| Modelo `kimi-k2-6` | ✅ retirado de models_available — incidente embrion-down resuelto en producción |
| T1-MAGNA-005 | ✅ **FIRMADA** Opción D (Enforce escalonado L0-L3) — file FIRMADA existe |
| T1-MAGNA-006 | ❌ Pendiente firma — bloquea PR autónomos del embrion |
| T1-MAGNA-007 | ❌ Pendiente firma — bloquea nomenclatura `bridge/missions/` para FORJA OMEGA |
| DSC-S-012 (auth fail-closed) | ⚠️ ID ocupado por otro DSC ya firmado (anti_deriva_migraciones_supabase) — propuesta original requiere re-numeración |
| Forja v4 código | ✅ Existe en `tablero-campana/server/forja/` (2,549 líneas TS) |
| Cognitive Republic | ✅ DSC-G-019 firmado, endpoints `/v1/factory/*` LIVE en kernel |
| Sprint Registry | ✅ Canonizado en Sprint 91.16, validado por CI |

---

## DECISIÓN 1 — T1-MAGNA-006: Embrion crea PRs Draft autónomos

> **¿El embrion_loop puede crear Pull Requests Draft autónomos contra los repos del Monstruo?**

### Las 4 opciones en una tabla (lectura 30 segundos)

| Criterio | A — NO PR | B — PR libre | C — PR escalonado doble llave | **D — Patches sandbox** |
|:---:|:---:|:---:|:---:|:---:|
| **Riesgo P0 con embrion alucinando** | 0 | **alto** | bajo | **0** |
| **Velocidad backlog (32 PROPOSED)** | lenta | alta teórica | media-alta | lenta-media |
| **Cumple DSC-MO-006 par crítico** | n/a | **no** | sí | sí |
| **Cumple DSC-G-008 v2 audit** | n/a | colapsa Cowork | sí | n/a (no merge) |
| **Pollution git history** | 0 | alta | media | **0** |
| **Costo implementación (líneas)** | 0 | ~150 | ~600 | ~250 |
| **Reversibilidad si falla** | n/a | baja | alta | **alta** |
| **Riesgo loop infinito** | n/a | **alto** | bajo | n/a |
| **Bottleneck humano residual** | Manus/Cowork | Cowork (50/día) | Cowork (10/día) | Manus aplica patch |
| **Independiente de T1-005 firmado** | sí | no | parcial | **sí** |
| **Cumple SOP/EPIA Capa 2** | NO | sí extremo | sí balanceado | parcial |

### Recomendación firme — Opción D (sandbox patches con merge-back manual)

Cuatro motivos verificables:

1. El embrion ya está VIVO con 209 ciclos sanos. Pero darle autoridad B/C el día 1 de operación post-fix kimi-k2-6 sin haber producido nunca un patch material es saltar la validación empírica.

2. Costo de error es asimétrico. Un PR malicioso de B/C con Cowork cansado puede mergearse a producción. Un patch malicioso de D muere en `bridge/embrion_patches/` sin tocar git history.

3. Opción C es destino correcto a largo plazo (~600 líneas + matriz Power Lanes embrion + DSC-MO-EMBRION-PR-AUTONOMY + SLA Cowork co-firma) — pero llegar a C sin pasar por D es saltarse la validación.

4. Plan de migración: T0 firmas D → T0+30 días si embrion produjo 30 patches útiles consecutivos, Cowork audita y se re-firma esta misma T1-006 en modo C con scope L0-L3.

### Bloque YAML de firma binaria T1-006

```yaml
decision_t1_magna_006:
  pr_drafts_autonomos_modo_ganador: ___  # A | B | C | D
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  justificacion_corta: ___
  fecha_revision_30_dias: 2026-06-26
  criterio_migracion_a_C: ___  # ej: "30 patches útiles consecutivos auditados por Cowork"
  budget_max_iteraciones_diarias: ___  # ej: 10 si D, 5 si C
  rollback_si_falla: ___  # criterio explícito
```

---

## DECISIÓN 2 — T1-MAGNA-007: Estructura del Evidence Pack

> **¿La unidad canónica de trabajo es SPRINT (registry actual) o MISIÓN (FORJA OMEGA) o ambos coexisten?**

### Las 4 opciones en una tabla (lectura 30 segundos)

| Criterio | A — Statu quo | B — Migración total | **C — Coexistencia jerárquica** | D — Por origen |
|:---:|:---:|:---:|:---:|:---:|
| **Rompe Sprint 91.16 (CI registry)** | no | **sí crítico** | **no** | no |
| **Acepta nomenclatura FORJA OMEGA** | no | sí | **sí** | sí parcial |
| **Costo migración** | 0 | alto | medio | bajo |
| **DSCs existentes sin cambios** | sí | no | sí + anexo | sí |
| **Sprint con múltiples misiones paralelas** | no | sí | **sí** | parcial |
| **Trazabilidad histórica continua** | sí | requiere reescritura | **sí** | fragmentada |
| **Complejidad para hilo nuevo** | baja | media | media-alta | alta (asimetría) |
| **Reversibilidad si falla** | n/a | **muy baja** | media (consolidador reversible) | alta |
| **Riesgo "decisión apurada por ChatGPT"** | n/a | **alto** | bajo | bajo |
| **Cumple "no inventar rueda"** | sí | no | parcial | parcial |
| **Expresividad semántica** | baja | alta | **alta** | media |

### Recomendación firme — Opción C (coexistencia jerárquica)

Tres motivos:

1. **No rompe Sprint 91.16.** El registry y la GitHub Action `sprint-registry-validate.yml` (mergeada hace 24h en PRs #213/#214) quedan intactos. Romper algo recién canonizado sería pirotecnia.

2. **Captura la riqueza semántica de FORJA OMEGA en la capa de ejecución sin tocar el manifiesto.** Un sprint puede tener múltiples misiones paralelas (caso real: 3 envelopes Forja simultáneos). Bridge/missions/ es el home natural de eso.

3. **Trazabilidad clara con 3 niveles:**
   - `sprints/registry.yaml` → MANIFIESTO (qué sprints existen, status, paradigm, OM)
   - `bridge/missions/<MISSION_ID>/` → EJECUCIÓN VIVA (intent, orders, assemblies, evidence, court)
   - `bridge/sprints_completados/<sprint_id>_<fecha>.md` → HISTÓRICO CONSOLIDADO

Cuando una misión cierra, un consolidador genera el resumen para sprints_completados y archiva la misión a `bridge/missions/_archive/`. DSC-G-008 v3 extiende el scope de audit pre-cierre para cubrir `bridge/missions/`.

### Bloque YAML de firma binaria T1-007

```yaml
decision_t1_magna_007:
  evidence_pack_estructura_ganadora: ___  # A | B | C | D
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  justificacion_corta: ___
  mission_id_schema: ___  # ej: "<sprint_id>_<seq>" si C, o solo <sprint_id>
  consolidador_obligatorio_al_cerrar: ___  # true | false (recomendado true si C)
  dsc_g_008_v3_anexo_requerido: ___  # true | false (recomendado true si C)
  rollback_si_falla: ___  # criterio explícito
```

---

## Lo que pasa el día después de firmar

| Si firmas | Acción Manus B | Plazo |
|---|---|---|
| **T1-006: D + T1-007: C** (recomendación dual) | Aplica firmas a archivos canónicos · branch `sprint-t1-magnas-preforja-omega-v1` · valida registry · push · abre PR · solicita audit Cowork · mergea cuando verde · mueve sprint a `sprints_completados/` | ~30 min de Manus B |
| **T1-006: A o B + T1-007: A o B** | Manus B re-articula con ChatGPT en iteración 002 (las opciones extremas requieren más sustento) — sprint queda PROPOSED | 1-2 días |
| **T1-006: C + T1-007: C** (variante alternativa) | Manus B abre 2 sprints adicionales (~600 líneas C de T1-006 + consolidador C de T1-007) — bloquea FORJA OMEGA visual ~1-2 semanas | 1-2 semanas |

Si firmas la dupla recomendada (D + C), **el ecosistema queda listo para prompt v2 FORJA OMEGA en menos de 1 hora**. Las 5 capas de S5 ya están firmadas y mergeadas en main. El embrion está sano. Forja v4 está construida. Solo falta exhibición visual en `tablero-campana`.

---

## Tres formas de firmar (elige una)

### Opción 1 — Respuesta inline en este hilo (RECOMENDADO — más rápido)

Escribe simplemente:

```text
Firmo T1-006 — Opción D
Firmo T1-007 — Opción C
```

Si quieres ser más explícito (no es necesario):

```text
Firmo T1-006 — Opción D
  budget: 10 patches/día
  migracion_a_C: 30 patches útiles consecutivos
  rollback: si 5 patches consecutivos rechazados, embrion vuelve a A

Firmo T1-007 — Opción C
  mission_id_schema: <sprint_id>_<seq>
  consolidador_al_cerrar: true
  dsc_g_008_v3_anexo: requerido
  rollback: si consolidador falla 3 veces, vuelta a A
```

Yo me encargo del resto: aplicar firmas YAML a los archivos canónicos, validar, commitear, abrir PR, gestionar audit Cowork, mergear, mover el sprint a sprints_completados.

### Opción 2 — Editar este archivo directamente

Edita los bloques YAML arriba con tus valores, commit y push. Yo recojo el cambio.

### Opción 3 — Crear archivos separados FIRMADA

Escribe `T1_MAGNA_006_..._FIRMADA.md` y `T1_MAGNA_007_..._FIRMADA.md` con los YAML completos en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/` y commit.

Cualquiera de las tres genera el contrato canónico. **La opción 1 es la más rápida si quieres hacerlo desde móvil o el chat.**

---

## Si decides NO firmar HOY

Está bien dormirlo. Lo que sigue avanzando sin firmas:

- Bug ghost residual S5 (esperando log Railway de Cowork para diagnóstico binario completo).
- Forja v4 enforce L0-L3 (T1-005 ya firmada, no depende de 006/007).
- Cierre formal del incidente embrion-down (ya resuelto en producción, falta postmortem).

Lo que se bloquea sin firma:

- Prompt v2 FORJA OMEGA VISUAL — sin nomenclatura `bridge/missions/` canonizada (T1-007), no puede usar el path que pide ChatGPT.
- Embrion produciendo trabajo material (patches o PRs) — sin T1-006, sigue siendo asesor que solo escribe a memoria.
- Sprint `T1_MAGNAS_PREFORJA_OMEGA_v1` — queda en estado PROPOSED indefinidamente.

---

## Notas finales

Este manifiesto NO firma por ti. Solo entrega las decisiones binarias con criterios verificables HOY (cross-check tiempo real ejecutado contra `/v1/genome/now/health` y `/health`) y la recomendación de Hilo B con justificación.

Las firmas son tuyas, T1 magnas, no delegables a Manus, ni a Cowork, ni a ChatGPT.

**Tiempo total de lectura: ≤4 minutos.** Tiempo total para firmar inline: ≤1 minuto adicional. Total: **≤5 minutos** para cerrar las dos decisiones magnas que desbloquean FORJA OMEGA.

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de emisión:** 2026-05-27 21:55 UTC
**Sesión:** post-rebase PR #227 + smoke E2E ghost residual + auditoría binaria del Genoma Vivo
**Articulaciones canónicas referenciadas:**
- `T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_PARA_FIRMA.md` (Manus B, 2026-05-26 — 303 líneas)
- `T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_PARA_FIRMA.md` (Manus B, 2026-05-26 — 324 líneas)

**Validación tiempo real:** ejecutada por Manus B hoy 2026-05-27 21:37 UTC sobre `https://el-monstruo-kernel-production.up.railway.app/v1/genome/now/health` y `/health` (kernel binario_100, embrion vivo 209 ciclos, modelos correctos)

**Recomendación dual firme:** T1-006 Opción D (sandbox patches) + T1-007 Opción C (coexistencia jerárquica)
