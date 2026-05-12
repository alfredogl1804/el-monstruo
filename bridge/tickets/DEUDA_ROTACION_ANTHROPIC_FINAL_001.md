---
id: DEUDA-ROTACION-ANTHROPIC-FINAL-001
fecha: 2026-05-12T09:50:00Z
emisor: Cowork T2-A bajo autoridad T1 ABSOLUTA AMPLIADA 2026-05-12 ~09:42 UTC
severidad: P0 documental (NO bloquea operación + T2-B contradice doctrinalmente)
estado: pendiente_T1_cierre_avance_magno_Monstruo_completo
prioridad: crítica al cierre Monstruo completo
---

# DEUDA T1 — Rotación ANTHROPIC_API_KEY + cualquier secret/credencial/API key pendiente hasta cierre Monstruo

## Decisión T1 absoluta vinculante

**Alfredo T1 verbatim 2026-05-12 ~09:08 UTC:** *"no vamos a rotar nada hasta el final cierralo asi"*

**Alfredo T1 verbatim 2026-05-12 ~09:42 UTC (ampliación):** *"lo de rotar secrets, credenciales y apis keys lo suspendemos hasta acabar el monstruo"*

**Interpretación Cowork:** alcance ampliado de "hasta el final del avance magno" → **hasta cierre completo del Monstruo** (cuando T1 declare la totalidad del proyecto cerrada). NO rotación preventiva ni reactiva durante cualquier sub-cascada interna. Riesgo aceptado verbatim por T1 absoluto vinculante.

## Origen del leak documentado

Commit `972ea02` (2026-05-12 ~07:26 UTC) introdujo en `bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_FINAL_2026_05_12.md` línea 19 el prefijo truncado de la API key Anthropic actual del kernel:

```
| ANTHROPIC_API_KEY | Rotación completa | nueva key `sk-ant-api03-LWY9v2...buQtfgAA` seteada... |
```

Detectado por Cowork audit DSC-G-008 v3 §4 pre-firma declaración MEGA-CIERRE-HOY EJECUTOR 1. Repo `alfredogl1804/el-monstruo` es público (`"private": false`).

## 4 contradicciones T2-B verbatim (Perplexity AUDIT-TRANSVERSAL 2026-05-12 ~09:30 UTC)

T2-B argumentación binaria sobre **por qué doctrinalmente debilita la decisión T1**:

1. **History git persistente** — incluso si editás el archivo, el blob queda accesible via `git log --all --raw` y mirrors públicos del repo público
2. **Secret scanning vendor-side** — GitHub + Anthropic + scanners terceros (gitleaks, trufflehog, GitGuardian) pueden detectar el patrón + disparar revocación automática externa sin tu intervención
3. **Prefijo + suffix permite correlación** — atacante con timing analysis + workspace fingerprint reducido ~99.99% del espacio búsqueda
4. **Estándar industrial exige rotación ante disclosure parcial** — SOC 2, ISO 27001, NIST 800-53 todos lo declaran mínimo doctrinal

**Recomendación T2-B verbatim:** *"Rotar ANTHROPIC_API_KEY ya + purgar blob del history."*

## Decisión T1 sobre contradicción T2-B

T1 **mantiene su decisión absoluta** post-conocimiento de las 4 contradicciones T2-B. Verbatim 2026-05-12 ~09:42 UTC: *"lo de rotar secrets, credenciales y apis keys lo suspendemos hasta acabar el monstruo, entonces dicho esto que deberia seguir?"*.

T1 absorbió los argumentos T2-B + decidió absolutamente la suspensión total de rotaciones. Cowork respeta autoridad T1 absoluta como nivel sobre T2-B convergencia. **Riesgo aceptado plenamente documentado para auditoría futura.**

## Alcance T1 ampliado (verbatim)

NO rotar **NINGUNO** de los siguientes hasta cierre Monstruo completo:

- `ANTHROPIC_API_KEY` (leak parcial conocido en commit 972ea02)
- `OPENROUTER_API_KEY`
- `OPENAI_API_KEY` (si existe)
- `GOOGLE_API_KEY` / `GEMINI_API_KEY`
- `XAI_API_KEY` (Grok)
- `DEEPSEEK_API_KEY`
- `PERPLEXITY_API_KEY`
- `KIMI_API_KEY` / `MOONSHOT_API_KEY`
- `SUPABASE_SERVICE_KEY`
- `SUPABASE_DB_URL`
- `SUPABASE_ANON_KEY`
- `RAILWAY_TOKEN`
- `GITHUB_TOKEN` / `GITHUB_PAT`
- `TELEGRAM_BOT_TOKEN`
- `LANGFUSE_SECRET_KEY` / `LANGFUSE_PUBLIC_KEY`
- `BITWARDEN_MASTER_PASSWORD` (heredado pause incidente P0 2026-05-10)
- Cualquier API key / secret / credencial actualmente en Railway env vars o repo

## Acción al cierre Monstruo completo (Alfredo T1 decide cuándo)

Cuando T1 declare cierre Monstruo completo:

1. **Rotación masiva coordinada** de todos los secrets listados arriba
2. **History rewrite** OPCIONAL si T1 decide limpiar el history vía `git filter-branch` o `BFG Repo-Cleaner` + `git push --force` coordinado con todos los hilos pausados
3. **Activar regla gitleaks preventiva** (ver `GITLEAKS_TRUNCATED_KEY_PATTERN_001.md`)
4. **Audit pre-rotación** Perplexity T2-B + Cowork DSC-G-008 v3 §4 del estado de cada secret

## Trazabilidad

- Commit detectado: `972ea02` (`bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_FINAL_2026_05_12.md` línea 19)
- Audit T2-B: pegado verbatim Alfredo 2026-05-12 ~09:30 UTC en chat session
- Decisión T1 inicial: 2026-05-12 ~09:08 UTC
- Decisión T1 ampliada: 2026-05-12 ~09:42 UTC
- DSC enforced: DSC-S-001 + DSC-S-002 + DSC-S-016 (audit binario Cowork detectó correctamente)
- Ticket preventivo paralelo: `GITLEAKS_TRUNCATED_KEY_PATTERN_001.md`
- Declaración con caveat P0: `bridge/cowork_to_manus_DECLARACION_MEGA_CIERRE_HOY_EJECUTOR1_2026_05_12.md` §3
