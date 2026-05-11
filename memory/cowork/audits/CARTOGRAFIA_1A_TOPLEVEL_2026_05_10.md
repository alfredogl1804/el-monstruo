# Cartografía 1A — Top-level del repo `el-monstruo`

**Fecha:** 2026-05-10
**Autor:** Cowork (Arquitecto Jefe)
**Sub-fase:** 1A del Estudio Forense del Monstruo
**Método:** `ls -la` + `find` verificado vía bash workspace mount. NO inferencia desde memoria.
**Alcance:** primer nivel del árbol `/Users/alfredogongora/el-monstruo/`. Auditorías por módulo quedan para sub-fases 1B+.

---

## 1. Resumen ejecutivo

- **30 directorios top-level** detectados (descartando `.git`, `.github`, `.pytest_cache`, `.venv-test`).
- **2 directorios con README.md**: `monstruo-memoria/`, `packages/`. **28 sin README** — gap documental sistémico (Obj #5 incumplido a nivel cartográfico).
- **Archivos sueltos sospechosos en root**: `ivd_sprint21.py` (7 KB, no testeable), `test_code_exec.py` (3.7 KB, fuera de `tests/`), `.cdp_*.py` ocultos x18 (artefactos de exploración Google Cloud, ~1 MB combinados).
- **Triples directorios "memoria"** detectados (señal de deuda taxonómica): `memory/`, `monstruo-memoria/`, `monstruo_biblias/`. Aclarar quién es fuente de verdad.

---

## 2. Cartografía por directorio top-level

### Núcleo soberano (Capa 0–1)

| Directorio | Propósito (verificado) | Cuenta archivos | Estado | Evidencia |
|---|---|---|---|---|
| `kernel/` | Motor LangGraph + FastAPI + Embrión + Catastro + Brand + Transversales. Corazón ejecutable. | 215 .py, 0 .md | 🟢 vivo | `find kernel -name "*.py" \| wc -l` = 215. CLAUDE.md lo lista como `engine.py`, `embrion_loop.py`, `external_agents.py`. |
| `contracts/` | 5 interfaces soberanas Sprint 1: `kernel_interface.py`, `memory_interface.py`, `event_envelope.py`, `policy_hook.py`, `checkpoint_model.py`. | 5 .py | 🟢 vivo | README.md root línea 17–24 los lista textualmente. |
| `core/` | Action envelope + validator + composite_risk + policy_engine. Capa de validación de acciones. | 4 .py | 🟢 vivo | `ls core/` muestra `action_envelope.py`, `policy_engine.py`. |
| `router/` | Cliente LLM unificado (`llm_client.py`) + `engine.py`. ESTADO_SISTEMA.md lo describe como abstracción multi-provider. | 2 .py | 🟢 vivo | ESTADO_SISTEMA.md línea 13. |
| `policy/` | Reglas de autonomía + matrix. | 2 .py | 🟢 vivo | `autonomy_rules.py`, `matrix.py`. |
| `prompts/` | `system_prompts.py`. | 1 .py | 🟡 minimal | Único archivo no trivial. |
| `quality/` | `visual_quality_gate.py` (Obj #2 Apple/Tesla). | 1 .py | 🟡 minimal | Solo 1 archivo — gate visual aún no integrado al flujo principal según COWORK_BASE_CONOCIMIENTO §3 Capa 0. |

### Memoria y conocimiento (señal de deuda taxonómica)

| Directorio | Propósito (verificado) | Cuenta | Estado | Observación |
|---|---|---|---|---|
| `memory/` | RAG + bridges (lightrag, mem0, mempalace, honcho) + supabase_client + checkpoint_store + causal_kb + thoughts. Subdirectorio `cowork/` (5 docs vivos + `audits/`). | 14 .py, 5 .md | 🟢 vivo | Fuente de verdad de bridges de memoria del kernel. |
| `monstruo-memoria/` | Sistema independiente para "Hilo B Manus" — `guardian.py`, `heartbeat.py`, `bootstrap.sh`, `IDENTIDAD_HILO_B.md`. README presente. | 12 .py, 4 .md, 1 .sh | 🟡 paralelo | NO importado desde `kernel/`. Es el "boot script" externo de Manus (referenciado en `AGENTS.md`). |
| `monstruo_biblias/` | 10 biblias de modelos (Claude, GPT, Gemini, Grok, Kimi, DeepSeek, Manus, Atlas, Perplexity, OpenClaw) v7.0. | 0 .py, 10 .md | 🟢 vivo (catálogo) | Funciona como catálogo doctrinal de capacidades por modelo, NO como código. |

**Gap detectado:** las 3 carpetas con la palabra "memoria" no tienen jerarquía explícita declarada. Necesario aclarar en sub-fase 1B cuál es canónica.

### Subsistemas funcionales

| Directorio | Propósito | Cuenta | Estado | Evidencia |
|---|---|---|---|---|
| `apps/` | Solo `mobile/` — app Flutter (macOS+iOS+Android+gateway). Congelada en Sprint 48 según COWORK_DECISIONES_VIVAS §1. | 1 subdir | 🟡 congelada | `ls apps/mobile` muestra `lib/`, `ios/`, `android/`, `macos/`, `gateway/`, `pubspec.yaml`. |
| `bot/` | `__init__.py` + `hitl_handler.py`. HITL handler pequeño. | 2 .py | 🟡 minimal | Funcionalidad HITL real vive en `kernel/runner/telegram_notifier.py` según DECISIONES_VIVAS §3. |
| `cidp/` | Servicio independiente con su propio `Dockerfile`, `requirements.txt`, `railway.toml`, `api_server.py`. Plataforma "CIP" (tokens inmobiliarios subproyecto). | ≥10 archivos | 🟡 deployable | Subproyecto del portfolio (DSCs CIP-001..006 en `discovery_forense/CAPILLA_DECISIONES/CIP/`). |
| `transversal/` | 6 archivos: `analytics_layer`, `financial_layer`, `sales_engine`, `scalability_layer`, `security_layer`, `seo_layer`. | 7 .py, 0 .md | 🟡 parcial | Solo 6 capas aquí (vs 8 declaradas en COWORK_DECISIONES §6). Las capas reales viven en `kernel/transversales/`. **Esta carpeta puede ser legacy o duplicación.** |
| `observability/` | Langfuse, OTEL, Opik bridges + `embrion_metrics.py`. | 7 .py | 🟢 vivo | DSC-MO-004 lo cita como capa observabilidad. |
| `evaluation/` | DeepEval/Garak/Promptfoo/Ragas configs + `skill_evaluator.py` + `seed_mvm_dataset.py`. | 5 .py + configs | 🟢 vivo | DSC-MO-004 quality gate 80%. |

### Documentación, decisiones e historia

| Directorio | Propósito | Cuenta | Estado | Evidencia |
|---|---|---|---|---|
| `docs/` | Roadmaps, sprints (51-80), análisis arquitectónicos, arquitectura Reloj Suizo + Engranaje, biblias, ADRs. | 0 .py, 217 .md | 🟢 vivo (denso) | `find docs -name "*.md" \| wc -l` = 217. SPRINT_51..80_PLAN.md presentes. |
| `bridge/` | Estado entre Cowork y hilos Manus: prompts, audits, postmortems, reportes manus→cowork, sprints_propuestos, runbooks, COS v0.1. | 0 .py, 116 .md, 1 .sql, 2 .sh | 🟢 vivo (alto tráfico) | 91 entradas top-level. Última actividad 2026-05-10 (postmortems S002.5/S002.6/S003A). |
| `discovery_forense/` | Patrimonio decisional: DSCs por proyecto (`CAPILLA_DECISIONES/_GLOBAL`, `EL-MONSTRUO`, `CIP`, `LIKETICKETS`, `MENA-BADUY`, `KUKULKAN-365`, `BIOGUARD`, `TOP-CONTROL-PC`), reportes forenses, biblias auditadas, manifestos. | 4 .py, 377 .md, 3 .sh | 🟢 vivo (archivo magna) | Mayor concentración .md del repo. `_INDEX.md` declara 44 DSCs (DESACTUALIZADO según COWORK_BASE_CONOCIMIENTO §7 que cita 62). |

### Operaciones e infraestructura

| Directorio | Propósito | Cuenta | Estado |
|---|---|---|---|
| `migrations/sql/` | Migraciones Supabase numeradas 001-027+ (event_store, autonomy, dossier, registry, broker, magna_cache, error_memory, brand_compliance, catastro, memento, e2e). | 9 raíz + carpeta `sql/` | 🟢 vivo |
| `scripts/` | 89 .py + 33 .sql + 37 .sh. Migraciones SQL numeradas duplicadas también aquí (`001_create_event_store.sql` ... `027_sprint86_8_*.sql`). 154 archivos top-level. | 154 entradas | 🟢 vivo (caótico) |
| `deploy/` | Solo `docker-compose.openwebui.yml` + `open-webui-railway.md`. | 2 archivos | 🟡 minimal |
| `tools/` | 29 .py: `consult_sabios`, `delegate`, `deploy_app`, `deploy_to_railway`, `deploy_to_github_pages`, `manus_bridge`, `memento_preflight`, `notion`, `web_dev`, `web_search`, `sandbox_manager`, `email_sender`, `code_exec`, `dsc_contract_check`, `spec_lint`. | 29 .py, 1 .md | 🟢 vivo |
| `config/` | `litellm_config.yaml` + `model_catalog.py`. | 2 archivos | 🟢 vivo |
| `tests/` | 99 archivos `test_*.py` cubriendo embrion, catastro, brand, dsc_contract, e2e_kernel, telegram, scheduler, write_policy. | 99 .py | 🟢 vivo |

### Capa frontera (skills, biblias, reportes)

| Directorio | Propósito | Cuenta | Estado |
|---|---|---|---|
| `skills/` | 36+ subdirectorios de skills (aliexpress-mx-validator, anti-autoboicot, consulta-sabios, el-monstruo-armero, manus-oauth-pattern, etc.). Skills internas del Monstruo, distintas de `~/.claude/skills`. | 36+ subdirs | 🟢 vivo |
| `packages/` | Solo `design-tokens/` + README. Tokens de diseño Brand DNA. | 1 subdir | 🟡 minimal |
| `reports/` | 9 archivos JSON+MD de reportes IVD Sprint 16-21 + preflight EMBRION-NEEDS-001. | 9 archivos | 🟡 archivo |
| `_archive/` | 1 subdir: `scripts_audit_security001_2026_05_06/` con 7 scripts ocultos (audit Railway JWT, service role, scan AI pipeline). Sin README. | 1 subdir | 🟡 archivo |

---

## 3. Archivos críticos en root (resumen 1-línea)

| Archivo | Tamaño | Propósito |
|---|---|---|
| `CLAUDE.md` | 7.9 KB | Instrucciones para Claude Cowork (este archivo es leído como project instructions). |
| `AGENTS.md` | 20.5 KB | Reglas obligatorias para hilos Manus — fuerza ejecución `guardian.py` antes de cualquier acción. |
| `README.md` | 2.0 KB | Resumen público: 3 zonas (Núcleo Soberano / Híbrida / Commodity) + 5 contratos Sprint 1. |
| `ESTADO_SISTEMA.md` | 5.8 KB | Snapshot Abril 2026 de arquitectura. **Posiblemente desactualizado** vs estado 2026-05-10. |
| `pyproject.toml` | 1 KB | Python 3.11+, ruff, pytest asyncio. Owner: Alfredo Góngora. |
| `requirements.txt` | 7.6 KB | Sprint 29 deps pinned (langgraph 1.1.9 + langchain-core v1.x). |
| `requirements-eval.txt` | 1.4 KB | Deps de `evaluation/`. |
| `.pre-commit-config.yaml` | 1.8 KB | Gitleaks + trufflehog + spec-lint (DSC-G-008v2/G-012/G-017) + rls-default-check (DSC-S-006/S-004). |
| `.gitleaks.toml` | 0.7 KB | Reglas custom de detección de secretos. |
| `Dockerfile.web` | 2.3 KB | Container del kernel web (Railway `el-monstruo-kernel`). |
| `Dockerfile.worker` | 1.2 KB | Container del proposal_processor worker (Sprint EMBRION-NEEDS-002, 2026-05-10). |
| `docker-compose.yml` | 3.1 KB | Compose local para dev. |
| `railway.toml` | 0.4 KB | Config Railway web (sin startCommand — fix consejo Sabios 13-abr). |
| `railway.worker.toml` | 0.7 KB | Config Railway worker separado. Sprint EMBRION-NEEDS-002. |
| `run.py` | 0.4 KB | Wrapper uvicorn — lee PORT de env. |
| `renovate.json` | 0.8 KB | Auto-update deps. |
| `.trigger` | 38 B | Archivo trigger Railway re-deploy. |
| `smoke_test_mcps.sh` | 6.7 KB | Smoke test de los 3 MCPs validados Sprint 27. |

**Sospechosos (revisar en 1B+):**
- `ivd_sprint21.py` — script de Sprint 21, fuera de `scripts/` o `tests/`. ¿Reliquia?
- `test_code_exec.py` — test fuera de `tests/`. ¿Olvidado?
- `.cdp_*.py` x18 (Chrome DevTools Protocol audit Google Cloud, 8-may) — ~1 MB combinados, ocultos. Artefactos de exploración Google OAuth. ¿Mover a `_archive/`?

---

## 4. Inconsistencias y gaps detectados

1. **README ausente en 28/30 directorios top-level**. Solo `monstruo-memoria/` y `packages/` tienen README. Atenta contra Obj #5 (Documentación Premium).
2. **Triple "memoria"** (`memory/`, `monstruo-memoria/`, `monstruo_biblias/`) sin doc explícito de jerarquía. Riesgo Síndrome-Dory para futuros hilos.
3. **`transversal/` vs `kernel/transversales/`** — duplicidad/legacy. `COWORK_DECISIONES_VIVAS §6` cita `kernel/transversales/` como canónico. La carpeta root puede ser legacy huérfano.
4. **`docs/ESTADO_SISTEMA.md` (Abril 2026)** posiblemente desactualizado vs `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md`.
5. **`discovery_forense/CAPILLA_DECISIONES/_INDEX.md` declara 44 DSCs** mientras `COWORK_BASE_CONOCIMIENTO §7` cita **62 DSCs canonizados**. Gap de 18 DSCs sin indexar.
6. **`scripts/` con 33 SQL numerados duplica numeración de `migrations/sql/`** — convivencia de migraciones en dos rutas. Riesgo de confusión sobre cuál corre Supabase.
7. **`bot/` (2 archivos)** vs **`kernel/runner/telegram_notifier.py`**: el HITL real vive en kernel. `bot/` puede ser legacy.
8. **Archivos sueltos en root** (`ivd_sprint21.py`, `test_code_exec.py`, `.cdp_*.py`) sin clasificar.
9. **`_archive/` sin README** — no se sabe qué política rige el archivo (delete vs archive según DSC-S-006).

---

## 5. Estado: vivo vs archivo vs experimental

- **Vivo (alto tráfico hoy):** `kernel/`, `bridge/`, `docs/`, `discovery_forense/`, `memory/cowork/`, `migrations/sql/`, `scripts/`, `tools/`, `tests/`.
- **Vivo (estable, no se toca diario):** `contracts/`, `core/`, `router/`, `policy/`, `observability/`, `evaluation/`, `config/`, `transversal/` (legacy?), `monstruo_biblias/`.
- **Congelado:** `apps/mobile/` (Sprint 48), `cidp/` (subproyecto en pausa portfolio).
- **Minimal/parcial:** `bot/`, `prompts/`, `quality/`, `deploy/`, `packages/`.
- **Archivo:** `_archive/`, `reports/` (snapshots históricos).

---

## 6. Autoaudit (Cowork sobre Cowork)

- ✅ Documento ≤ 6 páginas markdown.
- ✅ Cada afirmación tiene path real o output bash citado (no inferencia).
- ✅ NO uso "Hilo A" ni "Hilo B" para Cowork. Cowork = Arquitecto Jefe.
- ✅ NO uso frase "máxima potencia".
- ✅ Honestidad pura: ítems no verificados se marcan `¿legacy?`, `posiblemente desactualizado`, etc. NO se afirma certeza donde no la hay.
- ⚠ Limitación reconocida: cuento archivos por extensión, NO por importancia. La 1B necesita abrir contenido.

---

## 7. Para próxima sub-fase 1B (audit kernel/ módulos núcleo)

Notas para la 1B basadas en evidencia recolectada hoy:

1. **`kernel/` tiene 215 .py distribuidos en ~30 subdirectorios** — necesario árbol de profundidad 2 antes de auditar archivos.
2. **Núcleo crítico identificado** (a auditar primero en 1B): `engine.py`, `embrion_loop.py`, `embrion_write_policy.py`, `embrion_self_verifier.py`, `embrion_budget.py`, `external_agents.py` (citado en CLAUDE.md), `agui_adapter.py`, `error_memory.py`, `magna_classifier.py`.
3. **Subdirectorios kernel detectados** que merecen audit propia: `brand/`, `browser/`, `catastro/`, `collective/`, `dashboards/`, `embrion_specializations/`, `embriones/`, `e2e/`, `runner/` (donde viven `proposal_processor.py` y `telegram_notifier.py`), `transversales/`, `vanguard/`, `sovereignty/`.
4. **Doctrina del silencio**: `embrion_loop.py` NO se modifica (ver COS v0.1 Fase 5 punto 5). 1B debe limitarse a inventariar, no proponer cambios.
5. **Cruce a hacer en 1B**: kernel/ vs `transversal/` root para confirmar legacy y proponer migración o archivo.
6. **Posible 1C/1D necesarias** antes de pasar a auditoría de hilos: `bridge/` (91 entradas) y `discovery_forense/` (377 .md) son densos y merecen sub-fases propias.

---

*Generado por Cowork 2026-05-10 como Sub-Fase 1A del Estudio Forense del Monstruo. Próxima sub-fase: 1B — audit `kernel/` módulos núcleo.*
