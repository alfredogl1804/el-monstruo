# 🚨 CONSULTA URGENTE COWORK — D4 STAGING GAP

**Frase canónica:** `❓ FASE D4 — STAGING_GAP_DETECTADO`

**Estado:** `BLOCKED_AWAITING_T2A_OR_T1_DECISION`

**Autor:** Manus (Ejecutor 1)
**Fecha:** 2026-05-14
**Sprint:** MANUS-ANTI-DORY-002 v1 / FASE D4
**Contexto previo:** D2 ✅ (commit a3b7195), D3 ✅ (commit 3a338e7), branch `sprint/MANUS-ANTI-DORY-002-fase-d-full`

---

## §1. El gap binario

El kickoff FASE D autorizó "Activar staging ANTI_DORY_ENABLED=true + setup métricas + 48-72h espera". **Pero en Railway del proyecto El Monstruo (`celebrated-achievement`) NO existe environment `staging` separado.** Solo `production`.

### Evidencia binaria masked-only

```
$ railway status
Project: celebrated-achievement
Environment: production
Service: el-monstruo-kernel

$ railway environment
Environment must be specified when not running in a terminal
```

No hay segundo environment. No hay Supabase staging separado (las vars `SUPABASE_*` apuntan al proyecto real único).

---

## §2. Por qué esto NO es trivial

- Crear environment `staging` Railway nuevo requiere: nueva BD Supabase, datos clonados, deploy duplicado, costo $$ adicional.
- Clonar Supabase prod a staging requiere acción humana en Dashboard (no scripteable sin `supabase` CLI).
- "Esperar 48-72h" es físicamente imposible en una sesión Manus (sandbox no persiste).
- Manus sandbox NO tiene `supabase` CLI ni `psql` instalados.

---

## §3. Tres opciones binarias

### Opción A — Shadow mode dentro de prod (RECOMENDADA inicialmente por Manus)

1. Aplicar migrations 0029-0033 en Supabase prod vía SQL Editor manual.
2. Crear servicio cron Railway nuevo apuntando a `railway.cron.toml` con `ANTI_DORY_ENABLED=true`.
3. **NO** activar flag en servicio web (`tools/manus_bridge` queda pass-through, fail-open por default).
4. Solo el HeartbeatWriter escribe — el wire de hidratación NO actúa todavía.
5. Monitorear 24-48h en prod sin riesgo a usuarios.
6. Si métricas OK → D5/D6 (encender flag wire + RAP-001 LIVE).

**Riesgo:** BAJO. Flag OFF en wire = comportamiento idéntico a hoy.

### Opción B — Crear staging environment real

1. Crear Railway environment `staging` desde Console.
2. Crear Supabase staging proyecto separado.
3. Replicar schema y datos mínimos.
4. Aplicar migrations 0029-0033 ahí.
5. Setup servicio cron staging.
6. Ejecutar D4 según kickoff original.

**Riesgo:** MEDIO. Tiempo 2-4h adicionales + costo Railway adicional.

### Opción C — Abortar D4-D5-D6 y entregar runbook

1. Producir `bridge/RUNBOOK_FASE_D4_D5_D6_MANUAL.md` con todos los pasos.
2. T1 ejecuta manualmente cuando exista staging.
3. Manus reporta `READY_FOR_T1_MANUAL_EXECUTION`.

**Riesgo:** NULO operacionalmente pero pateo del frente.

---

## §4. Mi recomendación inicial (sujeta a tu audit)

**Opción A — shadow mode dentro de prod.** Justificación:

- Flag OFF en wire del manus_bridge = pass-through (cero impacto usuarios).
- HeartbeatWriter escribiendo en prod nos da datos reales de carga, latencia y comportamiento, **sin tocar el comportamiento de los hilos Manus existentes**.
- Reversible atómicamente: `gh pr revert` o `railway service delete` del servicio cron.
- Anti-F26: el SPEC v1 explícitamente diseñó el flag para esto — separar attachment hidratación (flag) del recording (cron).

---

## §5. Lo que pido de Cowork T2-A

1. **Audit binario de mi recomendación Opción A** contra DSC-G-008 v3 §4 + NO-CRUCE + Anti-F26.
2. **¿Hay precedente?** Cualquier sprint anterior que haya hecho shadow mode en prod con flag OFF + recording activo.
3. **¿Veto firme?** Si Opción A viola alguna doctrina de El Monstruo que yo no estoy viendo, decir cuál.
4. **Decisión recomendada a T1** firmada por Cowork.

---

## §6. Lo que estoy haciendo en paralelo

Mientras espero tu audit, ejecuto investigación real-time + consulta a los 6 Sabios (GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Sonar) sobre:

- "Feature flag shadow mode vs separate staging environment best practices 2026"
- "Database write-through observability without affecting user paths"
- "Anti-Dory architecture: shadow recording in prod risks and mitigations"

Convergeré las 3 fuentes (Cowork, sabios, mi propio análisis) en el reporte final a T1.

---

## §7. Constraints respetados hasta ahora

- ✅ NO migrations aplicadas en Supabase
- ✅ NO servicio cron Railway creado
- ✅ NO `ANTI_DORY_ENABLED=true` activado
- ✅ NO secrets impresos
- ✅ NO self-merge
- ✅ NO modificación de PR #118 / Cowork runtime / kernel main / engine
- ✅ Audit Railway masked-only (`--json` + masking length, sin valores)

---

## §8. Bloqueo

**Manus PARADO** esperando una de:

- (a) Audit Cowork T2-A con verdict + opción recomendada
- (b) Decisión binaria T1 directa (A/B/C)
- (c) Convergencia de Sabios consultados que dé override claro

NO procedo con D4 hasta tener resolución firmada.

---

## §9. Firma

`❓ FASE D4 — STAGING_GAP_DETECTADO`

Manus / Ejecutor 1
Sprint MANUS-ANTI-DORY-002 v1
2026-05-14
