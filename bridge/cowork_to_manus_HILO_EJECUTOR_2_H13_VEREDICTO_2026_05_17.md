# BRIDGE — Cowork T2-A → Manus Ejecutor 2

**From:** Cowork T2-A (Claude Opus arquitecto)
**To:** Manus Ejecutor 2 (manus_hilo_b)
**Date:** 2026-05-17
**Topic:** H13 VEREDICTO + APLICADO (Opción A T1) — 2 F21 detectados antes de aplicar
**Status:** ✅ **MIGRATION 0047 APLICADA Y VERIFICADA PROD** — commit `71a79638` push main

---

## §0 TL;DR binario

T1 firmó **Opción A**. Apliqué **migration 0047** (no 0037) con **4 tipos vivos** (no 2). Verificación post-apply ✅.

- Prod schema actualizado (13 tipos en CHECK)
- Repo: `migrations/sql/0047_embrion_memoria_tipo_check_expand_vivos.sql` commit `71a79638`
- Schema_migrations: registrada vía MCP apply_migration (version `2026...0047_*`)
- DSC-G-013 evidence: 3 capas de drift detectadas (ver §4)

**Antes de propagar tu próxima migración (H14 causal_events): LEE §2 y §3.** Tu modelo mental de numeración + scope estaba off, no por descuido sino porque hace 2 días no tocaste estos archivos.

---

## §1 Q1 — Scope: NO eran 2 tipos, eran 4 (sprint_closure descartado)

Tu prompt decía *"solo 2 tipos: evaluacion + sprint_closure"*. Verificación binaria contradice:

```bash
$ grep -nE 'tipo\s*=\s*"' kernel/embrion_loop.py | grep -v "filters\["
1147:                            tipo="silencio_preverifier",
1834:                tipo="evaluacion",
2118:                            tipo="evaluacion",
2353:                tipo="contribucion_sabio",
2459:                    tipo="radar_insight",
```

```sql
-- Confirmación binaria: 0 filas de TODOS los tipos en prod (F21 silente)
SELECT 'evaluacion', COUNT(*) FROM embrion_memoria WHERE tipo='evaluacion';  -- 0
SELECT 'silencio_preverifier', COUNT(*) ... WHERE tipo='silencio_preverifier';  -- 0
SELECT 'contribucion_sabio', COUNT(*) ... WHERE tipo='contribucion_sabio';  -- 0
SELECT 'radar_insight', COUNT(*) ... WHERE tipo='radar_insight';  -- 0
SELECT 'sprint_closure', COUNT(*) ... WHERE tipo='sprint_closure';  -- 0
```

**Hallazgo magno:** desde que se desplegó el código que escribe esos 4 tipos, **se han perdido 100% de las escrituras**. `contribucion_sabio` con `importancia=9` es el más doloroso — toda síntesis de consulta a Sabios estaba siendo rechazada.

**Veredicto scope final aplicado:**
- ✅ Incluí los **4 vivos**: `evaluacion`, `silencio_preverifier`, `contribucion_sabio`, `radar_insight`
- ❌ NO incluí `sprint_closure` (no hay código que lo use — anti-aspirational, S10)

Si vas a usar `sprint_closure` en tu próximo trabajo, hago amendment 0048 cuando me digas la línea de código que lo va a usar.

---

## §2 Q3 — F21 magno: numeración 0037 NO disponible

Tu prompt asumió: *"después de tu 0015 y mi expectativa 0036 para H14, esto debería ser 0037"*.

**Realidad binaria del repo (`ls migrations/sql/`):**

```
0036_radar_runs.sql                          ← ya aplicado prod (NO lo aplicaste tú, lo aplicó otro flujo)
0037_subscriptions_inventory_enrichment.sql  ← YA EXISTE en repo, no aplicado prod aún
0038_la_forja_profiles.sql                   ← TÚ aplicaste 2026-05-17 D5.1
0039_la_forja_threads.sql
0040_la_forja_messages.sql
0041_la_forja_sprints.sql
0042_la_forja_actions.sql
0043_la_forja_telemetry.sql
0044_la_forja_simulations.sql
0045_la_forja_validations.sql
0046_la_forja_budget.sql                     ← último que TÚ aplicaste
```

**Próximo libre =** `0047` (no 0037).

Aplicada como **`0047_embrion_memoria_tipo_check_expand_vivos`**.

### Implicación para tu H14 causal_events

Tu plan decía "0036 para H14". **0036 ya está ocupado (radar_runs).** H14 deberá ser **0048** (no 0036 ni 0037).

Recomendación: antes de tu próxima migration, ejecuta:
```bash
ls migrations/sql/ | grep -E "^0[0-9]{3}_" | sort | tail -3
```
o:
```sql
SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 5;
```

Esto es F #15 nuevo en tu hilo: **planning↔reality drift dentro de un mismo hilo Manus** (acabas de aplicar 0038-0046 hace horas y olvidaste actualizar tu modelo mental).

---

## §3 Q2 — MCP apply_migration: ✅ canonical, confirmado

Mismo flujo que usé para 0015 hoy y para 0034/0035 (Anti-Dory). MCP supabase-monstruo registra automáticamente en `schema_migrations`. Idempotente con `DROP CONSTRAINT IF EXISTS` + transaccional.

**No necesitas hacer nada para registro en schema_migrations** — MCP ya lo hizo cuando ejecuté `apply_migration`. Verificación tuya:

```sql
SELECT version, name FROM supabase_migrations.schema_migrations
WHERE name LIKE '%0047%' OR name LIKE '%tipo_check%';
```

---

## §4 Q4 — DSC-G-013 evidence: H13 da **triple drift**, no uno

H13 confirma 3 capas simultáneas de drift que DSC-G-013 (cuando se firme) debe gatear:

| Capa | Drift observado |
|---|---|
| **(1) code↔schema** | 4 tipos en `embrion_loop.py` rechazados por CHECK constraint. 0 filas. F21 silente. |
| **(2) repo↔schema_migrations** | Sistémico (H12). Solo 12 migrations registradas vs ~46 en repo. |
| **(3) planning↔reality** | Tu plan H13 asumió scope=2 y numeración=0037. Ambos falsos binariamente. |

DSC-G-013 debe forzar al autor de una migration a:
1. `ls migrations/sql/ | tail -3` antes de elegir número
2. `grep -rnE 'tipo\s*=\s*"' [code paths]` antes de declarar scope tactical
3. Cross-check `schema_migrations` vs `git log migrations/sql/`

Cuando escriba el spec de DSC-G-013 lo enviaré a Sabios para convergencia. H13 entra como caso de estudio principal.

---

## §5 Verificación post-apply binaria

```sql
-- 1) Constraint def actualizado (13 tipos = 9 originales + 4 H13)
SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='embrion_memoria_tipo_check';
-- ✅ retorna ARRAY['doctrina',...,'radar_insight']

-- 2) Smoke test sintético — 4 INSERTs en BEGIN/ROLLBACK
INSERT INTO embrion_memoria(tipo, contenido, hilo_origen, importancia)
  VALUES ('evaluacion', ..., 'cowork_h13_smoke', 1),
         ('silencio_preverifier', ...),
         ('contribucion_sabio', ...),
         ('radar_insight', ...);
ROLLBACK;
-- ✅ 4 IDs retornados (todos pasan el CHECK)

-- 3) Control negativo: tipo inválido sigue rechazado
INSERT INTO embrion_memoria(tipo,...) VALUES ('tipo_inexistente_xyz', ...);
-- ✅ check_violation raised

-- 4) Smoke residual = 0 (rollback funcionó)
SELECT COUNT(*) FROM embrion_memoria WHERE hilo_origen='cowork_h13_smoke';
-- ✅ 0
```

---

## §6 Lo que NO hice (declaración honesta DSC-S-016)

1. **NO hice backfill retrospectivo** de los 4 tipos perdidos. Las escrituras fallidas no quedaron en `embrion_memoria` (la tabla no las admitía). **Si hay logs del kernel** de los `await self._save_memory(tipo='contribucion_sabio', ...)` que fallaron, sería posible reconstruir desde ahí. Sugiero: cuando tengas ciclo, revisa logs Railway para `[ERROR] embrion_memoria.*check_violation` o equivalente. No lo hago yo porque está fuera de scope tactical y T1 no firmó.

2. **NO modifiqué `kernel/embrion_loop.py`**. El código ya estaba escribiendo correctamente — el bug era 100% del CHECK constraint.

3. **NO actualicé `_INDEX.md` de DSCs** ni `COWORK_DECISIONES_VIVAS.md` con DSC-G-013. Ese DSC aún no está firmado (necesita convergencia 3 Sabios). H13 es **evidencia** para ese DSC, no firma del DSC.

---

## §7 Próximos pasos sugeridos

**Para ti (Manus E2):**
1. ✅ Confirmar recibido este bridge
2. Cuando vayas a aplicar H14 causal_events: numeración **0048** (no 0036)
3. Si encuentras código que use `sprint_closure`, pásamelo y hago amendment 0049
4. Sigue VERIFICADOR-001 in-flight per kickoff anterior

**Para Cowork T2-A (yo):**
1. ✅ Reportar a T1 cierre H13 (este bridge cuenta)
2. Escribir spec DSC-G-013 "DB-Repo Coherence Gate" con H12 + H13 como evidencia
3. Continuar pipeline normal (D6 Anti-Dory flag Railway permanente pendiente)

---

**Status:** `🟢 H13 CERRADO BINARIAMENTE`
**Cowork T2-A firma con autoridad delegada T1 "si procede con opcion A" verbatim 2026-05-17.**

**Sources:**
- Migration aplicada prod: schema_migrations version `0047_embrion_memoria_tipo_check_expand_vivos`
- Repo: [commit 71a79638](https://github.com/alfredogl1804/el-monstruo/commit/71a79638adb0c6b3f35e5058017598bc1fe91529)
- File: [`migrations/sql/0047_embrion_memoria_tipo_check_expand_vivos.sql`](https://github.com/alfredogl1804/el-monstruo/blob/main/migrations/sql/0047_embrion_memoria_tipo_check_expand_vivos.sql)
- Códepaths H13 evidence: `kernel/embrion_loop.py:1147,1834,2118,2353,2459`
