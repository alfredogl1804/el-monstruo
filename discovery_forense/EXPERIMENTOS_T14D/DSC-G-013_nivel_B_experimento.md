---
experimento_id: DSC-G-013-NIVEL-B
estado: 🟡 EXPERIMENTO T+14D — métricas pendientes
inicio: T0 = firma T1 DSC-G-013 v0.1
cierre: T+14d (cosecha métricas + decisión canonización v0.2)
parent_dsc: DSC-G-013 v0.1
autor: Cowork T2-A — post-veredicto GPT-5.5 Pro (Sabio adversarial 2026-05-18)
---

# DSC-G-013 Nivel B — EXPERIMENTO T+14D

> **Sabio GPT-5.5 Pro adversarial dictaminó:** "Nivel B NO canonizar completo todavía. Mover a EXPERIMENTO_T+14D con métricas." Razón: la propuesta de `tools/_coherence_gate.py` automatizado es estructural pero no probada en campo. Mejor ejecutar 14 días con Nivel A doctrinal + medir antes de comprometerse a Nivel B canónico.

## §1 Hipótesis a validar

¿La automatización Nivel B (`tools/_coherence_gate.py`) **previene** F-pattern reincidentes más allá de lo que Nivel A doctrinal ya logra, sin introducir falsos positivos que paralicen el flujo?

## §2 Métricas binarias obligatorias (T+14D)

| # | Métrica | Pre-experimento (baseline) | Esperado T+14d | Threshold éxito |
|---|---|---|---|---|
| 1 | Falsos positivos del gate (count/semana) | N/A | 0-2/semana | ≤ 5/semana |
| 2 | Errores prevenidos pre-acción | 0 (gate no existe) | ≥ 1 | ≥ 1 (binario: 0 = experimento no-conclusivo) |
| 3 | Tiempo agregado real por turno (s) | 0 (no gate) | +5-30s | ≤ +60s |
| 4 | Frecuencia drift detectado pre-acción (count/sem) | retrospectivo: 3 esta sesión | depende uso real | medible binariamente |
| 5 | Cobertura multi-branch (PRs revisados con gate, %) | 0% | ≥ 50% PRs | ≥ 30% PRs (L_C6) |
| 6 | Hotfix manual DDL detectado (count) | desconocido | ≥ 0 | reportable binariamente (L_C7) |

**Decisión post-T+14d:**
- ✅ 5/6 métricas en threshold → canonizar Nivel B en DSC-G-013 v0.2
- 🟡 3-4/6 → revisar implementación, segundo experimento T+14d
- 🔴 ≤2/6 → archivar Nivel B como NO viable, mantener solo Nivel A

## §3 Implementación experimental (NO canonizar bytes hasta T+14d verde)

Script propuesto `tools/_coherence_gate.py` con 3 modos:

```python
# Ejemplos placeholders — implementación pendiente Manus E2 cuando tenga ciclo
python3 tools/_coherence_gate.py --mode=migration-numbering
# → output: próximo número libre, lista de últimas 5 en cada lado

python3 tools/_coherence_gate.py --mode=schema-constraint TABLE COLUMN
# → output: whitelist actual del CHECK + diff vs grep en código

python3 tools/_coherence_gate.py --mode=pre-action ACTION_TYPE
# → output: gate pass/fail con detalle
```

**Owner sugerido:** Manus E2 cuando tenga ciclo (post-T6 S-EMBRION-009). NO bloqueante.

**Integración experimental:**
- Pre-commit hook (manus push) — opt-in
- Pre-flight Cowork (Paso 0 extendido) — opt-in
- NO falla CI durante experimento (warn only)

## §4 L_C6 + L_C7 — limitaciones objetivo del experimento

### L_C6 — Multi-branch / PR divergence

Gate puede pasar en main y fallar en branch activa. 2 agentes pueden crear migrations paralelas y colisionar al merge. **Test experimental:** 2 hilos Manus crean migration con número 0050 paralelo. ¿Gate detecta colisión? Esperado: sí, ambos reciben warn antes de push.

### L_C7 — DB state fuera de schema_migrations

Supabase puede tener hotfix manual aplicado fuera de migrations. **Test experimental:** aplicar `CREATE INDEX` manual via psql (no migration). ¿Gate detecta drift? Esperado: sí, reporta DDL no-trackeado.

## §5 Referencias industria a explorar durante experimento

Perplexity sugirió evaluar Atlas/Flyway/Liquibase. Durante experimento Cowork puede comparar:
- ¿Custom Python cubre suficiente?
- ¿Atlas con `migrate/autorebase` cubre L_C6 mejor sin escribir código?
- ¿Liquibase `diff --format=json` cubre L_C7 mejor?

**Si T+14d demuestra que herramienta industria es superior:** v0.2 puede ser **"adopt Atlas + thin wrapper"** en vez de custom Python.

## §6 NO-CRUCE durante experimento

- ❌ NO canonizar Nivel B como parte de DSC-G-013 v0.1 (es experimental)
- ❌ NO bloquear CI por gate falso positivo durante T+14d (warn only)
- ✅ SÍ documentar cada caso de gate disparado (verdadero positivo o falso) en bridge
- ✅ SÍ medir las 6 métricas binariamente con queries reproducibles
- ✅ SÍ evaluar herramientas industria como alternativa a custom

## §7 Trayectoria post-experimento

- **T+7d:** revisión intermedia métricas — ¿correr 7 días más vale la pena?
- **T+14d:** cosecha completa + decisión canonización
- **T+14d → v0.2:** si verde → integrar Nivel B; si rojo → archivar Nivel B en `_archived/`

## §8 Triggers de cierre prematuro

Detener experimento ANTES de T+14d si:
- Falsos positivos > 10/semana (paraliza flujo)
- 0 errores prevenidos en 7 días Y 0 drift detectado (gate no aporta)
- Capacidad Manus E2 saturada — no puede ejecutar análisis

---

**Status:** `🟡 EXPERIMENTO PENDIENTE — espera firma T1 DSC-G-013 v0.1 + ciclo Manus E2 para implementación`
**Cowork T2-A firma experimento bajo autorización T1 "procede x" verbatim 2026-05-18.**

**Sources:**
- [DSC-G-013 v0.1](../CAPILLA_DECISIONES/_GLOBAL/DSC-G-013_db_repo_coherence_gate.md)
- [Veredicto GPT-5.5 Pro (que pidió esta degradación)](../../bridge/veredictos_dsc_g_013/gpt55_pro_veredicto_2026_05_18.md)
