---
id: cowork_to_manus_HILO_EJECUTOR_2_SPRINT_ROTOR_001_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 2 (cerrando GUARDIAN-AUTONOMO-001 — esperar reporte de cierre antes de arrancar este sprint)
tipo: kickoff_encadenado_post_guardian
prioridad: P1 (Bloqueante magna #1 del proyecto según Handoff Cowork saliente 2026-05-11 §9)
duracion_estimada: 4-7 días reales (per spec firmado — agrega código de fondo nuevo, no solo wiring como GUARDIAN)
autoridad_T1: Alfredo autorizó 2026-05-12 ("ok lo que tu recomiendes mas")
autoridad_T2: Cowork T2-A firma encadenamiento post-GUARDIAN
spec_firmado: bridge/sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md (firma T1 2026-05-11 incluyendo defaults energy_units T3 sin modificación)
delta_esperado_obj_global: Δ pendiente (cierra Bloqueante magna #1 — autonomía sostenida + primer paso real hacia Embrión-Dirige Fase 2)
---

# Kickoff Sprint ROTOR-001 — Reciclador de Actividad (pieza diferencial Reloj Suizo)

## §1 ¿Por qué este kickoff existe?

Estás cerrando GUARDIAN-AUTONOMO-001 con velocity demostrada (en menos de 1 hora desde el kickoff `fff2604`). Cowork T2-A reconoce calidad ejemplar previa: PAR_BICEFALO_001 con 3 PRs limpios + 84/84 tests.

Próxima asignación encadenada: **ROTOR-001**. Es la pieza diferencial del Reloj Suizo según `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3 y `_INDEX.md §3 #4` recomendación operativa: *"Hilo Ejecutor (cualquiera libre tras GUARDIAN-AUTONOMO-001)"*. Condición cumplida.

**Este documento NO duplica el spec.** Solo: encadenamiento + reglas duras NO-CRUCE 2026-05-12 + override de timing post-GUARDIAN.

## §2 NO ARRANCAR HASTA cerrar GUARDIAN

Antes de tocar nada de ROTOR-001:

1. Cerrá GUARDIAN-AUTONOMO-001 con frase canónica de éxito (per kickoff §6: `🏛️ GUARDIAN-AUTONOMO-001 — DECLARADO (6/6 verde)` si y solo si las 4 condiciones del spec §"Firma propuesta de cierre" están verdes)
2. Mergeá los PRs de GUARDIAN bajo permiso T2-A si pasan DSC-G-008 v2 (T2/T3/T5 write-risky requieren audit Cowork — vos dejás los PRs abiertos con tag `[GUARDIAN-AUTONOMO-001]`, yo audito y mergeo)
3. Seed embrion_memoria de cierre GUARDIAN
4. Reportá al bridge `bridge/manus_to_cowork_REPORTE_GUARDIAN_AUTONOMO_001_2026_05_12.md`
5. **Solo entonces** arrancás ROTOR-001

**Bloqueante humano persistente de GUARDIAN T3 (alerting Telegram)** sigue vivo: si dejaste T3 stub esperando firma Alfredo para hora/canal, NO bloquea cierre de GUARDIAN — se canoniza como "esperando bloqueante humano T1" en el reporte de cierre y se difiere a sprint paralelo cuando Alfredo firme.

## §3 Documentos a leer ANTES de escribir código

1. **Spec firmado:** [`bridge/sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md`](sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md) — 272 LOC, 6 tareas T1-T6 con `perfil_riesgo` declarado. **Fuente de verdad — defaults T3 firmados por T1 2026-05-11, no abrir a debate.**

2. **Doctrina canónica:**
   - `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3 (rotor + escape + resorte + volante)
   - DSC-MO-010 (analogía Reloj Suizo aplicada a IA agéntica)

3. **Audits que dieron origen:**
   - `memory/cowork/audits/AUDIT_4_CAPAS_3A_2026_05_10.md` §3 tabla Reloj Suizo + §7 H3
   - `memory/cowork/audits/CRUCE_DIMENSIONAL_5A_2026_05_10.md` §5 #5

4. **Código existente del Reloj Suizo (leer, NO modificar fondo):**
   - `kernel/embrion_loop.py` (2,151 LOC — Volante, doctrina del silencio. Solo agregás 1 marcador `ROTOR_LATIDO_BEGIN/END` en T2.6)
   - `kernel/embrion_budget.py` (484 LOC — Resorte. Agregás 1 función nueva `add_recycled_energy` en T4)
   - `kernel/finops.py` (252 LOC — FinOps Soberano)
   - `kernel/embrion_scheduler.py` (706 LOC — Áncora. Agregás 1 tarea `recharge_mainspring` cada 5 min en T4. **NO modificás scheduler core** — el patrón es idéntico a `daily_guardian_audit` que vos mismo registraste en GUARDIAN)

5. **Patrones de referencia (para no reinventar):**
   - GUARDIAN-AUTONOMO-001 que cerraste recién (registro de cron task + dashboard HTML + alerting + scoring engine)
   - Sprint T5 Embrión-Daddy bidireccional para marcadores `ROTOR_LATIDO_BEGIN/END` (mismo patrón de Sprint 81)

## §4 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

5 hilos en paralelo activos. **NO tocar:**

1. **Ejecutor 1 en Sprint 89** (kickoff commit `a40c693`) — `migrations/sql/00XX_catastros_4_tablas.sql` + `kernel/catastros/` + scaffolding. **Tu migración ROTOR T1 toma el siguiente número libre POSTERIOR al de Ejecutor 1.** Verificar con `python3 scripts/_check_migration_gaps.py` o equivalente DSC-S-012.
2. **PR #110 Perplexity** (`feat/t1-pre-response-hook-observe-only`) — `kernel/cowork_runtime/`. **No tocar.**
3. **Perplexity T2-B** auditando + mergeando PRs #108/#109/#111 (prompt commit `6f502a4`). **No tocar esos PRs.**
4. **Hilo Catastro** en holding esperando Sprint 89. Después arranca Catastro-A (`kernel/catastro/` singular + `kernel/data/`). **No tocar.**
5. **Tu propio trabajo GUARDIAN-AUTONOMO-001 mientras lo estás cerrando** — no abandonarlo a medias por arrancar ROTOR.

**SÍ podés tocar:**
- `kernel/rotor/` (NUEVO subdirectorio — territorio ROTOR)
- `kernel/rotor/capturers/` (6 módulos NUEVOS — uno por source)
- `kernel/dashboards/rotor_history.py` (NUEVO, sin chocar con `guardian_dashboard.py` que acabás de hacer)
- `migrations/sql/00YY_rotor_activity_log.sql` (NUEVA — YY = siguiente libre POST Sprint 89)
- `kernel/embrion_routes.py` (T2 — agregar endpoint webhook GitHub Push)
- `kernel/embrion_loop.py` (T2.6 — marcadores `ROTOR_LATIDO_BEGIN/END` para revert trivial, patrón conocido)
- `kernel/embrion_budget.py` (T4 — agregar `add_recycled_energy` función nueva)
- `kernel/embrion_scheduler.py` (T4 — registrar tarea `recharge_mainspring` cada 5 min, mismo patrón que `daily_guardian_audit`)
- `tests/rotor/*` (NUEVOS)
- `bridge/` para reportes

## §5 Bloqueante humano declarado

**T3 defaults `energy_units` ya firmados por Alfredo T1 el 2026-05-11.** El spec §3 Tarea T3 tiene la tabla completa con 8 sources × USD-equivalent + caps diarios. **No requiere re-firma.**

**Cap superior del recharge:** $30/día (2× daily cap original). Firmado T1.

**Validation magna post-deploy:** `record_validation("rotor_energy_calibration_2026", ...)` documentando primeros 7 días en producción. Si las cifras resultan mal calibradas, Alfredo puede ajustar via PR retroactivo. v1.0 corre con defaults firmados.

## §6 Cadencia de reportes esperada

ROTOR-001 es sprint LARGO (4-7 días reales). NO esperás reporte único al final. Cadencia recomendada:

- **Después de T1 cerrada** (migración aplicada): `bridge/manus_to_cowork_ROTOR_T1_DONE_2026_05_XX.md`
- **Después de T2 cerrada** (6 capturers funcionando): `bridge/manus_to_cowork_ROTOR_T2_DONE_2026_05_XX.md`
- **Después de T3 cerrada** (energy_calculator con tests ≥20 casos): `bridge/manus_to_cowork_ROTOR_T3_DONE_2026_05_XX.md`
- **Después de T4 cerrada** (recharge wireado al Resorte): `bridge/manus_to_cowork_ROTOR_T4_DONE_2026_05_XX.md` ⚠️ **paso crítico — toca el budget**
- **Después de T5 cerrada** (dashboard): `bridge/manus_to_cowork_ROTOR_T5_DONE_2026_05_XX.md`
- **Sprint completo cerrado** (T6 postmortem + canonización): `bridge/manus_to_cowork_REPORTE_ROTOR_001_2026_05_XX.md` con frase canónica `🏛️ ROTOR-001 — DECLARADO (6/6 verde)` solo si las condiciones del spec están verdes.

## §7 Permiso de merge

- **T1 migración SQL + T3 energy_calculator** (lógica pura): write-safe, push directo bajo D-4.8 (<100 LOC kernel + tests verdes + pre-commit verdes)
- **T2 capturers + T4 recharge + T5 dashboard** (write-risky por wiring al budget): PR limpio + tag `[ROTOR-001]`, Cowork T2-A audita DSC-G-008 v2 antes de merge
- **Self-merge prohibido** para PRs write-risky (T2, T4)
- **Bypass:** SOLO bajo instrucción T1 explícita

## §8 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint ROTOR-001 CERRADO. Pieza diferencial del Reloj Suizo implementada: 6 capturers (github_commit, supabase_query, telegram_message, cowork_session, manus_session, embrion_latido) → energy_calculator con defaults T1 firmados → recharge_mainspring cada 5 min → embrion_budget.add_recycled_energy. Cap superior $30/día respetado. Dashboard rotor_history.html operativo. Autonomía sostenida DESBLOQUEADA. Primer paso real hacia Embrión-Dirige Fase 2.',
  'manus-hilo-ejecutor-2',
  10
);
```

## §9 Pre-flight obligatorio (NO arrancar sin verde)

```bash
cd ~/el-monstruo
git status && git pull origin main
git log --oneline -1                  # esperado: >= a40c693 (kickoff Sprint 89)
# GUARDIAN cerrado:
grep -l "GUARDIAN-AUTONOMO-001 — DECLARADO" bridge/manus_to_cowork_REPORTE_GUARDIAN_AUTONOMO_001_*.md
# Esperado: 1 archivo (tu reporte de cierre)
# Migración Sprint 89 mergeada (para no chocar números):
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name LIKE 'catastro_%';"
# Esperado: >= 4 (las 4 tablas de Sprint 89 ya creadas — sino esperá a que Ejecutor 1 mergee)
# Webhooks GitHub configurables:
test -n "$GITHUB_WEBHOOK_SECRET" || echo "WARNING: GITHUB_WEBHOOK_SECRET no seteado, T2 github_capturer requiere config previa"
# Telegram bot:
test -n "$TELEGRAM_BOT_TOKEN" && test -n "$TELEGRAM_CHAT_ID"
```

Si pre-flight rojo, reportá `bridge/manus_to_cowork_ROTOR_001_PREFLIGHT_BLOCKED_2026_05_12.md`. **NO arranques en pre-flight rojo** (lección vivida por vos mismo en TRANSVERSAL-001).

## §10 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 ("ok lo que tu recomiendes mas") — full delegación T2-A para ROTOR-001
- T2-A (Cowork) firma encadenamiento post-GUARDIAN
- T3 (Hilo Ejecutor 2) ejecuta autónomamente bajo reglas duras §4
- ETA realista: 4-7 días reales (spec firmado), pero con tu velocity demostrada en GUARDIAN podría reducirse a 2-3 días reales

Si en pre-flight detectás bloqueante técnico no resoluble, **reportá honestamente al bridge** — regla anti-autoboicot que vos mismo canonizaste al cerrar TRANSVERSAL-001 con preflight bloqueado.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:30 UTC

**Sprint ROTOR-001 cierra Bloqueante magna #1 del proyecto declarado en Handoff Cowork saliente 2026-05-11 §9. Habilita autonomía sostenida: la actividad real de Alfredo + hilos Manus se convierte en energía que recarga el Resorte del Embrión, eliminando el cuello de botella del budget exhausto. Es el primer paso operativo hacia Embrión-Dirige (Fase 2 del modelo de hilos).**

**Cascada canónica encadenada:**
```
D-3 (latido autónomo) ✅
  → D-4 (schedulers zombies) ✅
    → D-5 (restore overdue) ✅
      → D-6 (anti-reentrada) ✅
        → Sprint 89 (4 catastros) ⏳ Ejecutor 1
          → Catastro-A (poblamiento) ⏳ Catastro (post Sprint 89)
            ↘
              GUARDIAN-AUTONOMO-001 ⏳ Ejecutor 2 (cerrando)
                → ROTOR-001 ⏳ Ejecutor 2 (este sprint, post-GUARDIAN)
                  → AUTONOMÍA SOSTENIDA DESBLOQUEADA
                    → Embrión-Dirige Fase 2 (siguiente sprint magno)
```
