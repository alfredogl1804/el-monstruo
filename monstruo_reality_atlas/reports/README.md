# Monstruo Reality Atlas — Phase 95 ChatGPT Pericia

**Fecha:** 2026-05-18
**Branch:** `monstruo-reality-atlas-001`
**Hilo Manus:** `monstruo-cycle-31-2026-05-18` (FASE 95)

## Propósito

Producir 5 evidence packs que permitan a ChatGPT alcanzar pericia ≥ 95% sobre el ecosistema del Monstruo, distinguiendo realidad runtime/código vs doctrina aspiracional, sin diseñar nuevos sprints, sin canonizar decisiones y sin tocar APP_VISION.

## Reglas observadas

- **NO_DESIGN** — packs solo sintetizan, no diseñan.
- **NO_CANONIZATION** — no agregan DSCs.
- **NO_APP_VISION_v2** — no tocan `docs/EL_MONSTRUO_APP_VISION_v1.md`.
- **NO_PRE_IA_CLOSE** — no cierran sprints pre-IA.
- **NO_NEW_SPRINT** — no proponen sprints (solo listan deudas).
- **EVIDENCE_ONLY** — todos los datos son auditoría runtime real 2026-05-18.

## Inventario de los 5 packs

| Pack | Archivos | Foco |
|---|---|---|
| **1. PROD_REALITY_AND_UI_CONSUMER_PACK** | `.md` + `.json` | Servicios vivos Railway, 20 routers FastAPI, Embrión runtime, Supabase tablas con counts, consumidores UI reales |
| **2. SECURITY_SMP_CRONOS_PACK** | `.md` + `.json` | DSCs Security S-001..S-016, 5 mig RLS, secrets, **SMP/Cronos = doctrina sin código**, Capa Magna Cap 17 aspiracional |
| **3. OPERATIONS_BRIDGE_RACI_PACK** | `.md` + `.json` | 237 mds bridge activos, hilos canónicos, Cowork=T2 Arquitecto (F9), Anti-Dory completo, runbooks gap |
| **4. PRODUCT_PORTFOLIO_BUSINESS_PACK** | `.md` + `.json` | 20 proyectos canónicos, **Command Center drift**, CIP sin código, Pipeline E2E implementado, C3-C6 sin spec |
| **5. CHATGPT_95_SYNTHESIS_PACK** | `.md` + `.json` + `_TEST_BATTERY.json` | Síntesis 5 tesis, batería 30 preguntas-test, delta gap-95%, protocolo calibración |

## Hallazgos top consolidados (cross-pack)

1. **Doctrina sobreconstruida vs runtime sub-implementado** (gap fundamental).
2. **CATASTRO-WIRING-001** mergeado main 2026-05-18 SHA `469c5eb` (caso ejemplar doctrina↔código↔runtime↔CI alineados).
3. **Command Center** declarado activo en doctrina pero NO existe código (drift severo P1).
4. **CIP** = "primera empresa-hija magna" pero 100% diseño/legal sin código.
5. **SMP / Cronos / Capa Magna Cap 17** = 100% aspiracional.
6. **Anti-Dory** = único subsistema con cobertura completa (kernel + migs + 8 fases DONE + audit Sabio externo).
7. **Bridge** vivo (5 fresh hoy) pero saturado (4/34 sprints completados).
8. **Catastro multi-namespace** = brain layer más maduro (41 modelos + 148 eventos + pipeline + quorum).
9. **RLS y secrets management** sólidos: 5 mig RLS aplicadas, 4 hooks pre-commit activos, P0 2026-05-06 cerrado con postmortem.
10. **Runbooks** cubren solo 3/13 credenciales activas → deuda P2.

## Cómo usar este atlas

1. **Inyectar los 5 JSON** al system prompt o sesión inicial de ChatGPT que vaya a operar sobre el Monstruo.
2. **Ejecutar `CHATGPT_95_TEST_BATTERY.json`** (30 preguntas) y medir score binario.
3. Score ≥ 28/30 = pericia 95%+ alcanzada.
4. Si falla 3, 4, 5, 24, 26, 27 → remediar con Pack 2 + Pack 4.
5. Si falla 18 → remediar con Pack 3 + `CLAUDE.md L151`.
6. Calibrar al inicio de cada hilo nuevo de ChatGPT.

## ACCESS_BLOCKED list (consolidada)

- Endpoints autenticados X-API-Key (proposals, finops, memory, moc, catastro/status, agui/info).
- Costos infra real Railway/Supabase/Langfuse.
- Logs Railway últimos 7 días.
- Status real proyectos clientes externos.
- Auditoría completa pre-commit `--no-verify` históricos.

## NO_SOURCE list (consolidada)

- `kernel/smp/`, `kernel/cronos/`, `kernel/cripta/`, `kernel/security_magna/`.
- `command-center/` directorio.
- Repos separados: ticketlike-mx, kukulkan-365, observatorio-merida, CIP.
- Embrión "Convergencia Cronos".
- Apps mobile en producción real.
- Métricas latencia bridge.
- Runbooks crisis: kernel-down, sabios-down, bridge-roto.

## Preguntas Magna Pendientes para Alfredo

16 preguntas consolidadas en `CHATGPT_95_SYNTHESIS_PACK.json` campo `questions_for_alfredo_consolidated`.

## Cierre

Atlas entregado para:
- **Alfredo (T1)** decida priorización de deudas.
- **ChatGPT (pericia)** se calibre con datos reales sin alucinar.
- **Cowork T2 Arquitecto** valide y observe canónicamente.
- **Hilos futuros Manus** tengan contexto verificado sin rehacer audit.

Sin merge a `main` propuesto. Branch viva: `monstruo-reality-atlas-001`.
