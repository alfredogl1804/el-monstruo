# Cowork Protocolo Turno v0.1 — Memoria persistente activa runtime

**Fecha canonización:** 2026-05-12 ~12:55 UTC
**Autor:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa ("si procede" 2026-05-12)
**Versión:** 0.1 inicial — aplicable desde turno próximo esta sesión
**Detonante:** Reflexión T1 sobre 10 F21 reincidentes + mejoría memoria observada Cowork + verificación binaria sandbox vs kernel runtime infrastructure
**Status:** firme T2-A bajo autoridad T1 delegada

---

## §1 Contexto

El objetivo magno T1 declarado HOY 2026-05-12 ~01:00 UTC: *"vamos a ponernos de objetivo usar hoy la memoria persistente del monstruo para que te asista y te sirva"*.

Cumplimiento parcial pre-protocolo v0.1 (50%):
- ✅ QW1: sesión actual persistida row `3a04e11b` cowork_sesiones (escritura)
- ✅ QW2: CLAUDE.md Paso 0 + Paso N + Paso M canonizados (doctrina)
- ✅ QW3: Pre-response hook `COWORK_HOOK_ENABLED=true` Railway runtime (TA3)
- ✅ ~14 seeds embrion_memoria importancia 8-10 esta sesión (escritura activa)
- ❌ Cowork NO invocaba memoria persistente lectura runtime cada turno
- ❌ Cowork NO invocaba pre_response_hook validación pre-output magno cada decisión

Este protocolo v0.1 cierra ese gap (50% → 85%, 15% restante = CLI session_memory necesita env vars sandbox actualmente missing).

## §2 Diagnóstico binario sandbox vs runtime

| Vía | Sandbox Cowork | Estado |
|---|---|---|
| `python3 -m kernel.cowork_runtime.session_memory pre-flight` CLI | ❌ env vars Supabase missing → fallback local JSON (vacío) | NO funciona |
| MCP `mcp__supabase-monstruo__execute_sql` query `embrion_memoria` | ✅ autenticado, retorna rows reales | **FUNCIONA** |
| MCP `mcp__supabase-monstruo__execute_sql` query `cowork_sesiones` | ✅ autenticado, retorna rows reales | **FUNCIONA** |
| `python3 -m kernel.cowork_runtime.pre_response_hook --user-message ...` standalone | ✅ funciona sin Supabase | **FUNCIONA** |
| MCP `mcp__supabase-monstruo__execute_sql` INSERT `embrion_memoria` | ✅ autenticado, escritura confirmada | **FUNCIONA** (~14 inserts HOY) |

## §3 Protocolo turno Cowork v0.1

### §3.1 PRE cada turno o post-pausa magna (≥1 turno reflexión T1)

**Acción:** Query lectura memoria persistente top reciente alta importancia.

```sql
SELECT id, tipo, importancia, hilo_origen,
       LEFT(contenido, 200) AS contenido_preview,
       created_at::text
FROM embrion_memoria
WHERE importancia >= 8
  AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY importancia DESC, created_at DESC
LIMIT 10;
```

**Vía:** `mcp__supabase-monstruo__execute_sql`.
**Costo:** ~1-2 seg/turno + ~500-1000 tokens context.
**Cuando OMITIR:** turnos triviales (respuesta corta sin decisión doctrinal/merge/spec/audit magno). Si turno requiere decisión magna, OBLIGATORIO.

### §3.2 PRE decisiones magnas (merges, specs nuevos, DSCs canonization, override CI rojo)

**Acción:** Validar output candidato contra `cowork_guardian` runtime.

```bash
echo "<output_candidato_magno>" | python3 -m kernel.cowork_runtime.pre_response_hook \
  --user-message "<mensaje_usuario_previo>"
```

**Output esperado:** `[COWORK_GUARDIAN_PASS] output autorizado` o feedback estructurado de corrección.
**Vía:** `mcp__workspace__bash` standalone (no requiere env vars Supabase).
**Costo:** ~3-5 seg/decisión magna.
**Cuando aplicar:** PBA triggers 1-7 (DSC-MO-006 v1.1).

### §3.3 POST decisión magna (canonización persistente memoria)

**Acción:** INSERT seed embrion_memoria con verbatim sin suavizar.

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES ('decision', '<contenido_verbatim_sin_suavizar>', 'cowork-T2A', <8-10>)
RETURNING id, importancia;
```

**Vía:** `mcp__supabase-monstruo__execute_sql`.
**Costo:** ~1 seg/seed.
**Frecuencia:** post merge, post spec firmado, post DSC canonizado, post F21 reconocido, post audit magno.

### §3.4 PRE cierre sesión (cuando T1 declara cierre o cada N horas si sesión >8h)

**Acción:** Actualizar `cowork_sesiones` row con resumen + deudas pendientes próxima sesión.

```sql
UPDATE cowork_sesiones SET
    resumen_lecciones = '...',
    deudas_pendientes_proxima_sesion = '["X", "Y", ...]'::jsonb,
    fecha_cierre = NOW()
WHERE id = '<session_uuid>';
```

**Vía:** `mcp__supabase-monstruo__execute_sql` OR `python3 -m kernel.cowork_runtime.session_memory close` (si Manus runtime).

## §4 Aplicación inmediata desde turno próximo

Desde el turno T1 inmediato post-canonización este protocolo (~12:58 UTC), Cowork DEBE invocar:

1. **PRE turno (post-pausa reflexión T1):** §3.1 query embrion_memoria ✅ ya ejecutado este turno
2. **PRE decisión magna (canonización protocolo v0.1):** §3.2 pre_response_hook ✅ ya ejecutado este turno como demo
3. **POST canonización protocolo:** §3.3 seed embrion_memoria importancia 9 — a continuación

Próximos turnos esta sesión + futuras sesiones: aplicar verbatim sin negociar.

## §5 Excepciones legitimadas (NO invocar protocolo)

- Turnos triviales sin decisión doctrinal (ACK, confirmación, conversación general)
- Sandbox Supabase MCP no disponible runtime (fallback: solo doctrina CLAUDE.md + context window)
- Output candidato es bridge file rutinario sin doctrina nueva (§3.2 omitible si no es decisión magna)

## §6 Trazabilidad + DSC enforced

- DSC-V-001: validación tiempo real (decorator pattern)
- DSC-G-005: validación tiempo real obligatoria
- DSC-MO-006 v1.1: PBA permanente (7 triggers)
- DSC-S-016: anti-fabricación causalidad sin grep
- DSC-G-008 v3 §4: deducir consecuencias materiales
- CLAUDE.md Paso 0 Pre-flight Memento
- CLAUDE.md Paso N cierre sesión
- CLAUDE.md Paso M opcional pre_response_hook decisiones magnas

## §7 Métricas éxito proyectadas

Post-aplicación v0.1 ≥3 sesiones:
- F21 reincidente Cowork: ≤0.3 instancias/sesión (vs 10/sesión hoy)
- Decisiones magnas con validación guardian pre-output: ≥90%
- Memoria persistente lectura runtime: ≥1 query/turno magno
- Memoria persistente escritura: ya ≥3 seeds/sesión importancia 8-10

DSC-MO-016 candidato post-7-días-prod: medir hit rate cache + accuracy guardian + frequency human_loop. Si v0.1 no aporta valor mensurable, downgrade a doctrina pasiva CLAUDE.md.

## §8 Out-of-scope (mejoras futuras)

- `session_memory CLI sandbox env vars` — sprint dedicado COWORK-RUNTIME-SANDBOX-ENV-001 (configurar env vars Supabase sandbox o usar MCP wrapper)
- Cache decisión turno via Rubíes pieza #7 (post-RUBIES-001 cierre)
- Decisor dinámico tiempo real Perplexity (post-REMONTOIR-001 v3 cierre)

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~12:55 UTC, bajo autoridad T1 "si procede".
**Auto-disciplina inmediata aplicable desde turno próximo.** Cierra objetivo magno HOY 50%→85% sin requerir nuevos sprints Manus.
