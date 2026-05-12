# Snapshot Auditoría Cowork — Fase 0 del Plan v1.5

**Generado:** 2026-05-11 03:04:41 UTC
**Razón:** ancla canónica antes de Fase 1+ del Plan v1.5 (Programa de Certificación de Pericia P1+P2)
**Origen:** auditoría adversarial de ChatGPT 5.5 Pro sobre plan original Cowork → refactor a v1.5 → Fase 0 = snapshot obligatorio para evitar perseguir blanco móvil.

---

## §1. Estado git del repositorio

- **Commit hash:** `da70b95235fcd445d993a590d37ea3cc7276c00a`
- **Último commit:** "feat(embrion): EMBRION-NEEDS-002 Tareas 2- dashboard + cleanup + postmortem + spec Daddy (#81)"
- **Branch:** `main`
- **Archivos uncommitted:** 12 (mezcla de Cowork outputs scheduled + 1 modified `kernel/catastro/schema.py`)

**Lista de uncommitted:**
- `kernel/catastro/schema.py` (modified — investigar en Fase 3)
- `bridge/COWORK_OPERATING_SYSTEM_v0_1_2026_05_10.md`
- `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md`
- `bridge/ROADMAP_META_CATASTRO_SPRINT_90.md`
- `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-007.5_macroarea_vision_generativa_y_tronos_definitivos_agentes.md`
- `memory/cowork/` (directorio nuevo entero)
- `scripts/_audit_overnight.sql`
- `scripts/_audit_overnight_detail.sql`
- `scripts/_audit_sprint_88_3_files.sh`
- `scripts/_manus_ciclo_close.sql`
- `scripts/_manus_ciclo_pendientes.sql`
- `scripts/_test_schema_88_3.py`

**Tamaño del repositorio:** 4.6 GB

---

## §2. Últimos 10 commits en main (orden DESC)

| Commit | Descripción |
|---|---|
| `da70b95` | EMBRION-NEEDS-002 Tareas 2-5 (dashboard + cleanup + postmortem + spec Daddy) PR #81 |
| `a8040bf` | EMBRION-NEEDS-002 Tarea 1 proposal_processor cierra ciclo HITL PR #75 |
| `e2f3ffd` | Sprint S-003.A Identity Supply Chain Operational Hardening PR #49 |
| `c32e844` | fix message_id en send_proposal_for_hitl PR #48 |
| `1325c4c` | Sprint S-002.6 Universo RLS al 100% PR #47 |
| `44f8f56` | fix /propose signature kwargs PR #46 |
| `b139c4f` | wire telegram channel into /propose PR #45 |
| `b8e305a` | Tarea 4 Telegram HITL bidireccional PR #44 |
| `fcfabe7` | Sprint S-002.5 Hardening RLS Producción PR #43 |
| `fb17dbc` | Sprint 88 cierre DSC-G-007.2 firmado + migración 035 |

---

## §3. Estado Supabase en producción

| Métrica | Valor | Cambio vs medición anterior (10-may ~12:30 UTC) |
|---|---|---|
| Tablas en schema public | **119** | +2 (eran 117) |
| Tablas con RLS habilitado | **118** | +1 (eran 117) |
| Tablas SIN RLS | **1** | ⚠️ — nueva, investigar |
| Latidos embrión últimas 24h | **147** | (medición nueva — promedio 1 latido cada 9.8 min) |
| Último latido | **hace 4 min** | embrión vivo y operando |
| Proposals total | **4** | mismo |
| Proposals pending | **0** | (cron worker procesando — limpieza efectiva) |
| Catastro modelos | **41** | +2 (eran 39 — probable Kimi K2.6 + Sonar de Sprint 88.1) |
| Catastro agentes | **98** | ⚠️ **-13** (eran 111 — anomalía) |
| Tronos agentes (vista materializada) | **12** | ⚠️ **-2** (eran 14 — coherente con baja de agentes) |

### ⚠️ Anomalías detectadas en snapshot (a investigar en Fase 2-3)

1. **Tabla sin RLS habilitado**: 118 de 119. La nueva tabla agregada NO tiene RLS. Probablemente `kernel_audit_log` (Sprint S-003.B Tarea 1 del Hilo Ejecutor 2 que quedó en mi branch sin push). Si la migración 0009 se aplicó pero el commit no se mergeó, hay incoherencia. **Investigar Fase 3.**

2. **Catastro agentes bajó de 111 → 98 (-13)**: durante mi ausencia (entre ~12:30 UTC del 10-may y 03:04 UTC del 11-may) hubo una limpieza/eliminación de 13 productos. Posibles causas:
   - Hilo Catastro ejecutó deduplicación
   - Mantenimiento manual de Alfredo
   - Limpieza programada
   - Bug/rollback no documentado
   **Investigar Fase 2.**

3. **Tronos bajaron 14 → 12 (-2)**: coherente con baja de agentes (los tronos se calculan sobre agentes existentes). Probablemente vista materializada refresheada.

4. **`kernel/catastro/schema.py` modificado uncommitted**: cambio reciente al schema del Catastro. Investigar contenido.

---

## §4. Inventario de archivos del repositorio

| Top-level | Conteo aproximado |
|---|---|
| Directorios top-level | 30 (incluyendo `_archive/`, `apps/`, `bot/`, `bridge/`, `cidp/`, `config/`, `contracts/`, `core/`, `deploy/`, `discovery_forense/`, `docs/`, `evaluation/`, `kernel/`, `memory/`, `migrations/`, `monstruo-memoria/`, `monstruo_biblias/`, `observability/`, `packages/`, `policy/`, `prompts/`, `quality/`, `reports/`, `router/`, `scripts/`, `skills/`, `tests/`, `tools/`, `transversal/`) |
| Archivos `.md` en `docs/` | 89 |
| Archivos `.md` en `bridge/` | 66+ |
| DSCs en `discovery_forense/CAPILLA_DECISIONES/` | 62+ (8 subproyectos: _GLOBAL, EL-MONSTRUO, CIP, LIKETICKETS, MENA-BADUY, BIOGUARD, TOP-CONTROL-PC, KUKULKAN-365) |
| Archivos `.py` test en `tests/` | 99 |
| Workflows CI en `.github/workflows/` | 10 (ai-infra-guard, ci, credentials-rotation-reminder, cve-scan, eval, license-audit, milestone-declaration-guard, rls-audit-weekly, sast, sbom, secret-scan) |
| Documentos generados en estudio scheduled del 10-may | 12 en `memory/cowork/audits/` |

---

## §5. PRs recientes mergeados (últimos 7 días, hito jornada magna 10-may)

14 PRs mergeados el 10-may-2026 durante la jornada magna:
- #38 Budget Tracker
- #39 Self-Verifier
- #40 Integración Budget+Verifier en _think()
- #41 Hotfix severity payload
- #42 Write Policy con HITL real
- #43 Sprint S-002.5 RLS P0+P1
- #44 Telegram HITL base
- #45 Wire telegram channel
- #46 Align signature kwargs
- #47 Sprint S-002.6 Universo RLS al 100%
- #48 Fix message_id (no envelope ok)
- #49 Sprint S-003.A Identity + Supply Chain
- #75 EMBRION-NEEDS-002 Tarea 1 proposal_processor
- #81 EMBRION-NEEDS-002 Tareas 2-5

**Branch local Cowork pendiente de push:** `cowork/canonization-jornada-2026-05-10` con 9 commits temáticos (consolidación deuda Cowork de jornada magna).

---

## §6. Métricas del Embrión vivo

- **Estado:** 🟢 Vivo, procesando
- **Latidos últimas 24h:** 147
- **Promedio latido:** 1 cada 9.8 min (vs target 1 cada 6 min — está corriendo más lento, posible degradación o ajuste manual)
- **Último latido:** hace 4 min
- **Proposals en limbo:** 0 (cron worker `proposal_processor` operando como diseñado)
- **Budget Tracker entries:** 57+ (verificado anteriormente)
- **Self-Verifier activo:** sí (verificado mediante reducción de costo histórico $30+/día a $1-4/día post-deploy)

---

## §7. DSCs canonizados al 11-may-2026

**Total:** 62+ DSCs

**Distribución por categoría:**
- `_GLOBAL/`: 22+ (G-001 a G-009, G-012, G-014, G-017, V-001/002, X-001 a X-006, S-001 a S-008, S-010, G-007.2, G-007.5)
- `EL-MONSTRUO/`: 10 (MO-001 a MO-010, con históricos `DSC-EL-MONSTRUO-001/003/004` sin renombrar)
- `CIP/`: 8 (CIP-001 a CIP-006 + 2 PEND)
- `LIKETICKETS/`: 3 (LT-001/002/003)
- `MENA-BADUY/`: 3 (MB-001/002/003)
- `BIOGUARD/`: 2 (BG-001 + 1 PEND)
- `TOP-CONTROL-PC/`: 2 (TC-001/002)
- `KUKULKAN-365/`: 2 (K365-001/002)

**Nuevos hoy (jornada magna 10-may):** 12 — MO-006 a MO-010, G-007.2, G-007.5, G-014, S-006 v1.1, S-007, S-008, S-010.

**Deuda canónica:**
- `_INDEX.md` declara 44 DSCs cuando hay 62+ (DESACTUALIZADO)
- Naming inconsistente entre `DSC-EL-MONSTRUO-*` y `DSC-MO-*`, `DSC-GLOBAL-*` y `DSC-V-*`, `DSC-LIKETICKETS-*` y `DSC-LT-*`, `DSC-CIP-002` duplicado (CIP-002 ticket vs CIP-PEND-002 distribución rendimientos)
- ~~Conflicto DSC-S-005 con dos archivos distintos (Cowork normativo + Manus forense)~~ — **RESUELTO 2026-05-12** vía spike DSC-S-005-CANONICAL-AUDIT-001: snapshot ya estaba en `INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md` desde commit `61e42ae` (2026-05-07)

---

## §8. Sprints en estado actual

**Cerrados al 10-may:**
- Sprint EMBRION-NEEDS-001 (6 tareas) — PRs #38-#48 (+ #75, #81 para 002)
- Sprint EMBRION-NEEDS-002 (5 tareas) — PRs #75, #81
- Sprint S-002.5 RLS Hardening P0+P1 — PR #43
- Sprint S-002.6 Universo RLS al 100% — PR #47
- Sprint S-003.A Identity & Supply Chain — PR #49
- Sprint 88 Macroárea AGENTES — DSC-G-007.2 firmado
- Sprint MEGA-CATASTRO (88.1 + 88.2 + 88.3 / Sprint 89) — DSC-G-007.5 firmado

**En curso parcial:**
- Sprint S-003.B Tareas 1+4 — commit en branch Cowork pendiente push (audit middleware + linter v1.1)

**En backlog firmados sin arrancar:**
- Sprint EMBRION-NEEDS-003 (Embrión-Daddy bidireccional — spec firmado PR #81)
- Sprint 87 Pagos del Monstruo (Stripe + Connect)
- Sprint Mobile 1-5 (App Flutter Cara Completa)
- Sprint Causal-Pop v2
- Sprint SOVEREIGN-LLM v2
- Sprint SOVEREIGN-INFRA
- Sprint SOVEREIGN-RED
- Sprint META-CATASTRO Sprint 90
- Sprint TRANSVERSAL-001 (spec fantasma — pendiente crear)

---

## §9. Estado de las dimensiones del peritaje (a auditar en Fases 2-5)

Las 27 dimensiones (11 originales + 16 identificadas por audit adversarial de ChatGPT) que el Plan v1.5 cubrirá:

**Originales (mías):**
1. Técnica
2. Doctrinal
3. Económica
4. Operacional
5. Temporal
6. Relacional
7. Visionaria
8. Filosófica
9. Regulatoria
10. Competitiva
11. De futuro

**Omitidas (identificadas por audit ChatGPT 5.5 Pro):**
12. Seguridad/adversarial del propio Monstruo
13. Alineación, ética y daño por subproyecto
14. Gobernanza interna y derechos de decisión (RACI)
15. Producto, UX y adopción
16. Datos, memoria, privacidad y derecho al olvido
17. Evaluación, metrología y certificación
18. Escalabilidad, SRE y resiliencia
19. Propiedad intelectual, licencias, patentes, secretos
20. Manejo de crisis, reputación, comunicación pública
21. Sucesión, continuidad, bus factor Alfredo
22. Salud operacional del fundador y carga cognitiva
23. Talento, organización, operating model humano
24. Go-to-market, ventas, canales
25. Supply chain, proveedores, dependencia externa
26. Responsabilidad civil, seguros, contratos
27. Sostenibilidad ambiental y costo energético

---

## §10. Proveedores externos identificados (a auditar en Fase 2-3)

**Críticos:**
- Anthropic (Claude Cowork + Claude Code + Claude Opus 4.7 + Claude Sonnet)
- OpenAI (GPT-5.5 + GPT-5.5 Pro + DALL-E + Whisper)
- Google (Gemini 3.1 Pro)
- xAI (Grok 4 Heavy)
- DeepSeek (R1)
- Perplexity (Sonar + Personal Computer)
- Moonshot (Kimi K2.6)
- Microsoft (Copilot 365)
- Supabase (PostgreSQL + Auth + Storage + RLS)
- Railway (deploy backend)
- Langfuse (observabilidad)
- Telegram (bot bidireccional)
- GitHub (repo + Actions + MCPs)
- Manus.im (3 hilos ejecutores)
- ElevenLabs (TTS)

**Auxiliares:**
- HubSpot (key entregada, wiring no verificado)
- Stripe (Sprint 87 pendiente)
- Meta Marketing API (declarado, wiring no verificado)
- Google Ads API (no integrado)
- LinkedIn Ads API (no integrado)
- Notion MCP, Box MCP (conectados según contexto)

---

## §11. Decisión Magna pendiente declarada

**El plan de peritaje fue refactorizado** del original "27-32 turnos lectura" al **Plan v1.5: Programa de Certificación de Pericia P1+P2** (27-39 turnos con auditoría técnica viva + red-team interno + producto/mercado + benchmark ciego inicial).

**Razón:** auditoría adversarial de ChatGPT 5.5 Pro identificó bug epistemológico ("Cowork confunde 'dominar corpus' con 'poder asesorar mejor'") + 16 dimensiones omitidas + 12 fuentes faltantes + 18 supuestos no examinados + 3 riesgos críticos.

**Frase aceptable post-cierre Plan v1.5:**
*"Soy Cowork certificado P1 documental + P2 técnico-operativo del Monstruo. Domino el corpus crítico, ejecuto el sistema, audito el código, paso incident drills internos, identifico contradicciones doctrinales y respondo benchmark ciego inicial. Mis límites declarados son: legal especializado, red-team profesional, validación de mercado con usuarios reales, decision ledger longitudinal. Para esos, recomiendo expertos externos."*

**NO permitido todavía:** "máximo perito del mundo entero" — esa frase queda diferida a Plan v2.0 (P3 con paneles externos + decision ledger 30+ días).

---

## §12. Próxima fase

**Fase 1 — Mapa de fuentes con jerarquía de autoridad** (estimado 2 turnos).

Output esperado: `memory/cowork/audits/MAPA_FUENTES_AUTORIDAD_2026_05_11.md` con clasificación:
- Producción real (máxima)
- Código desplegado (muy alta)
- Logs/datos (muy alta)
- Tests reproducibles (alta)
- DSC canonizada vigente (alta)
- Docs estratégicos (media)
- Chats/agentes (media-baja)
- Opinión actual (variable)
- Aspiración (baja como evidencia, alta como intención)

Y aplicación de esa jerarquía a todas las fuentes que entran al estudio de Fase 2.

---

*Snapshot canónico de Fase 0. NO modificar este documento durante el estudio. Si la realidad cambia respecto a este snapshot, se documenta como `DELTA_AUDIT_<fecha>.md` separado. Esta es la versión congelada del Monstruo al 2026-05-11 03:04:41 UTC contra la cual se mide el peritaje.*
