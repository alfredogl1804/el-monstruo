# 🔌 PR #129 LISTO PARA AUDIT COWORK — FASE D2-D3-D4

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fases consolidadas:** D2 + D3 + D4
**PR:** https://github.com/alfredogl1804/el-monstruo/pull/129
**Rama:** `sprint/MANUS-ANTI-DORY-002-fase-d-full`
**Base:** `main`
**Estado:** `OPEN` — `🔌 AUDIT_PENDIENTE`
**Autor:** Manus (Ejecutor 1)
**Fecha:** 2026-05-14

---

## §1. Resumen para Cowork T2-A

PR #129 entrega las 3 fases consolidadas (D2 grants + D3 cron + D4 shadow prod blindado) en una sola unidad auditable. **11 archivos, +2469 líneas, -0 líneas**. Manus se autodescarta del audit — Cowork T2-A aplica DSC-G-008 v3 con 6 gates.

---

## §2. Cambios respecto al estado pre-rebase

| Cambio | Razón |
|---|---|
| Rebase contra `origin/main` post merge PR #128 MEMENTO | Captura `0033_cowork_claims_calibration.sql` + SPEC FASE A retroactivo |
| `git mv 0033_anti_dory_grants.sql → 0034_anti_dory_grants.sql` | Colisión con MEMENTO |
| Migration 0035 nueva | Kill switch DB + write budget hardcap (C2-C3) |
| Cron rewriting completo | 18 condiciones duras + GPT-5.5 timeout/finally |
| Tests rewriting completo | 20 tests cubriendo C1-C7 + PC3 + GPT-5.5 |
| 3 bridge files D4 nuevos | DONE + REVERT_PLAN + MIGRATIONS_APPLIED template |

---

## §3. Convergencia TRIPLE Tier 1 documentada

| Sabio / Auditor | Input | Estado |
|---|---|---|
| T1 Alfredo | Veredicto Cowork bd11733b aceptado | ✅ Firmado |
| Cowork T2-A | Audit bd11733b: 10 condiciones + 6 puntos ciegos + plan operativo | ✅ Implementado en PR |
| GPT-5.5 Pro Sabio Magna | Convergencia: timeout estricto + finally close + frase canónica | ✅ Implementado en cron |

**Frase canónica magna:** *"Shadow prod no es activación: es instrumentación reversible con cero hidratación hasta que el attachment real pase prueba binaria."*

---

## §4. Gates DSC-G-008 v3 — pre-resultado Manus

| Gate | Descripción | Pre-resultado |
|---|---|---|
| G1 | Tests verdes | ✅ 48/48 |
| G2 | Grep secrets clean | ✅ 0 hits |
| G3 | Bridge files completos | ✅ 3/3 D4 |
| G4 | Constraints respetados | ✅ todos |
| G5 | Spec coverage 18 condiciones | ✅ documentadas en PR body |
| G6 | Rollback plan firmable | ✅ REVERT_PLAN.md con L1/L2/L3 |

---

## §5. Verificaciones binarias que Cowork debe re-correr

```bash
cd ~/el-monstruo
git fetch origin && git checkout sprint/MANUS-ANTI-DORY-002-fase-d-full

# G1
python3.11 -m pytest tests/anti_dory/ -q     # esperado 48/48 PASS

# G2 (DSC-G-008 grep)
PATTERN='ghp_[A-Za-z0-9]{36,}|sk-proj-[A-Za-z0-9_-]{30,}|sk-ant-api03-[A-Za-z0-9_-]{30,}|AIzaSy[A-Za-z0-9_-]{20,}|sk-or-v1-[a-f0-9]{30,}|xai-[A-Za-z0-9]{30,}|pplx-[A-Za-z0-9]{30,}|sbp_[a-f0-9]{30,}|sb_secret_[A-Za-z0-9_-]{15,}'
grep -nEH "$PATTERN" scripts/anti_dory_heartbeat_cron.py migrations/sql/0034_anti_dory_grants.sql migrations/sql/0035_anti_dory_runtime_flags.sql tests/anti_dory/test_heartbeat_cron.py
# esperado: vacío

# G3 (smoke test C7)
python3.11 scripts/anti_dory_heartbeat_cron.py --smoke-test
# esperado: exit 0, "smoke_test: PASS (all assertions OK)"

# G4 (verificar wire no tocado)
grep -nE "ANTI_DORY_ENABLED" tools/manus_bridge.py kernel/engine.py kernel/main.py 2>&1 | head
# esperado: SOLO referencias legacy NO modificadas en este PR

# G5 (verificar 0034 + 0035 no aplicadas en Supabase prod)
# Vía MCP Supabase, verificar que las tablas anti_dory_runtime_flags y
# anti_dory_write_budget NO existen aún
```

---

## §6. Acción solicitada a Cowork T2-A

1. **Audit DSC-G-008 v3** sobre PR #129 (6 gates arriba)
2. Si VERDE → **comentar veredicto en PR + autorizar merge**
3. Post-merge → **aplicar migrations 0034 + 0035 via MCP Supabase**
4. Post-apply → **llenar `FASE_D4_MIGRATIONS_APPLIED.md` con 7 métricas PC6**
5. Si verde 7/7 → **firmar handoff** → Manus procede con Railway service

NO se requiere a Cowork modificar código, solo auditar.

---

## §7. NO procede de mi parte hasta veredicto Cowork

Manus queda en `STANDBY` operativo. NO crearé el Railway service hasta que:
- PR #129 esté mergeado (o con autorización explícita de Cowork bajo DSC firmado)
- Migrations 0034 + 0035 aplicadas en Supabase prod
- 7 métricas PC6 verdes en `FASE_D4_MIGRATIONS_APPLIED.md`

Cualquier intento de auto-escalamiento sin estos 3 gates es violación de constraints C10 + convergencia TRIPLE.

---

**Manus firma:** Ejecutor 1
**Frase canónica al cierre D4:** `🏛️ ANTI-DORY D4 SHADOW PROD — DECLARADO`
