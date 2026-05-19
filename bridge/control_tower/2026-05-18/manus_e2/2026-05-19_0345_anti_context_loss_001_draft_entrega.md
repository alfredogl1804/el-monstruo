# AGENT OUTPUT — MANUS E2 — Entrega DRAFT ANTI-CONTEXT-LOSS-001 (Pieza 6 El Faro)

## Metadata

- agente: Manus E2
- rol real: ejecutor técnico (autor de DRAFT propositivo, sin atribución de canonización)
- fecha/hora: 2026-05-19 03:45 CST
- rama: `sprints-propuestos/2026-05-19-anti-context-loss-001-draft` (propuesta, pendiente de push)
- PR: ninguno (no autorizado a abrir PR sobre sprints_propuestos)
- commit: pendiente de creación
- estado fuente: DRAFT
- tocó código: no
- tocó main: no

## Qué hice

Diseñé un sprint propositivo que ataca específicamente la pérdida de contexto por compactación de ventana de tokens mid-sesión en hilos Manus y Cowork del Monstruo, vector descubierto como descubierto en el inventario de las cinco piezas anti-Dory existentes. El proceso siguió cinco fases secuenciales: audit binario de la infraestructura anti-Dory ya desplegada (tablas Supabase, kernel código, hooks, sandbox filesystem), investigación tiempo real de patrones canónicos 2026 (Anthropic Context Engineering septiembre 2025 y cookbook marzo 2026, Manus AI Context Engineering octubre 2025, LangGraph durable execution con time-travel, Harness Plan-Execute-Reset abril 2026, MCP memory servers), consulta paralela a tres Sabios (Opus 4.7, GPT-5.5 Pro, Perplexity Sonar Reasoning Pro) con prompt adversarial común y veredictos binarios sobre siete preguntas específicas, síntesis del spec definitivo integrando los ocho caveats convergentes de los Sabios, y depósito del DRAFT como archivo Markdown en `bridge/sprints_propuestos/`.

Durante la redacción de este sprint el hilo Manus E2 sufrió dos compactaciones en vivo confirmando empíricamente el vector que el sprint propone curar. Los archivos persistidos al sandbox sobrevivieron a ambas compactaciones, validando la columna vertebral arquitectónica del diseño: el filesystem del sandbox Manus es el punto de anclaje primario para memoria duradera intra-hilo.

## Evidencia

Spec definitivo depositado en `bridge/sprints_propuestos/sprint_ANTI_CONTEXT_LOSS_001_v1_DRAFT.md`, 12 secciones, ~24 KB, incluye arquitectura de 4 capas, schema SQL completo para migration 0036, test harness binario de 10 casos, limitaciones declaradas según DSC-G-008 v2 §4, Definition of Done binaria, veredictos verbatim de los 3 Sabios, sección "Qué NO asumir" explícita, y frase canónica de cierre heredada y extendida desde GPT-5.5 Pro sobre PIEZA 5.

Investigación tiempo real persistida en `/home/ubuntu/anti_context_loss_research_2026.md` (sandbox del hilo, no pusheada). Audit de infraestructura existente persistido en `/home/ubuntu/anti_context_loss_audit.md`. Veredictos verbatim de los 3 Sabios en `/home/ubuntu/consulta_3_sabios_anti_context_loss.json` con tokens consumidos: Opus 4.7=2327, GPT-5.5 Pro=4171, Perplexity Sonar=4922, total=11420.

Fuentes web consultadas con browser tool y persistidas en `/home/ubuntu/page_texts/`: Anthropic engineering blog Effective Context Engineering for AI Agents (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Lance Martin Context Engineering in Manus (https://rlancemartin.github.io/2025/10/15/manus/). Otras fuentes referenciadas vía snippet (LangGraph durable execution docs, Harness Defeating Context Rot, Anthropic platform cookbook tool-use context engineering).

Branch destino propuesta: `sprints-propuestos/2026-05-19-anti-context-loss-001-draft` (nueva, nace de `origin/main`). El reporte CONTROL TOWER actual irá en la misma branch o en la branch lateral existente `control-tower/2026-05-18-manus_e2` según decisión T1 sobre el patrón a seguir.

## Archivos tocados

| archivo | acción | branch | commit | nota |
|---------|--------|--------|--------|------|
| `bridge/sprints_propuestos/sprint_ANTI_CONTEXT_LOSS_001_v1_DRAFT.md` | crear | propuesta `sprints-propuestos/2026-05-19-anti-context-loss-001-draft` | pendiente push | DRAFT spec ~24KB 12 secciones |
| `bridge/control_tower/2026-05-18/manus_e2/2026-05-19_0345_anti_context_loss_001_draft_entrega.md` | crear | propuesta misma branch | pendiente push | este reporte CONTROL TOWER |
| `/home/ubuntu/anti_context_loss_audit.md` | crear (sandbox, no repo) | n/a | n/a | nota de audit local |
| `/home/ubuntu/anti_context_loss_research_2026.md` | crear (sandbox, no repo) | n/a | n/a | nota de investigación local |
| `/home/ubuntu/sabios_prompt_anti_context_loss.md` | crear (sandbox, no repo) | n/a | n/a | prompt común para 3 Sabios |
| `/home/ubuntu/consulta_3_sabios_anti_context_loss.json` | crear (sandbox, no repo) | n/a | n/a | veredictos verbatim 3 Sabios |
| código productivo del Monstruo | NO tocado | n/a | n/a | sprint es DRAFT exclusivamente |
| main | NO tocado | n/a | n/a | regla T1 |
| migrations existentes | NO tocadas | n/a | n/a | regla T1 |

## Tests / checks

| test/check | resultado | evidencia | nota |
|-----------|-----------|-----------|------|
| Audit binario de infraestructura anti-Dory existente | ✅ Completo | `/home/ubuntu/anti_context_loss_audit.md` | 5 piezas inventariadas con estado D5 GREEN / D6 pendiente / DRAFT |
| Investigación tiempo real Anthropic + Manus + LangGraph + Harness + MCP | ✅ Completo | `/home/ubuntu/anti_context_loss_research_2026.md` + 2 archivos browser dump | Convergencia 5 fuentes industriales 2026 |
| Consulta 3 Sabios paralelos con prompt adversarial común | ✅ Completo | `/home/ubuntu/consulta_3_sabios_anti_context_loss.json` | 3/3 amarillo CON CAVEAT, gaps y fixes capturados verbatim |
| Detección de auto-fallback de modelos solicitados | ⚠️ Parcial | tokens reportados + modelo real | Opus pedido recibió gpt-4o, GPT-5.5 Pro pedido recibió o3-mini, solo Perplexity Sonar Reasoning Pro fue exacto |
| Integración verbatim de los 8 caveats convergentes en spec v1 | ✅ Completo | Sección 7 del spec | 8/8 caveats integrados: enforcement kernel, simplificación Capa 4, idempotency outbox, CAS concurrencia, schema rígido NOTES, GC retención, MCP separación, eliminación forzar compaction |
| Definition of Done binaria sin matices | ✅ Completo | Sección 6 del spec | 11 condiciones binarias listadas |
| Limitaciones declaradas DSC-G-008 v2 §4 | ✅ Completo | Sección 5 del spec | 8 limitaciones explícitas declaradas |
| Verificación de "no incluí secretos" | ✅ Manual | grep -i "TOKEN\|SECRET\|API_KEY\|PASSWORD" spec → 0 hits | Validación binaria pendiente con gitleaks pre-push |
| Verificación de "no toqué código productivo" | ✅ Manual | git diff verifica que solo se agregaron archivos de bridge y sprints_propuestos | Pendiente validación pre-commit hooks |

## Bloqueos

| bloqueo | causa | quién desbloquea | urgencia |
|---------|-------|------------------|----------|
| Push del DRAFT a remote requiere autorización T1 explícita | Regla operativa de Manus E2: no push a remote sin autorización | T1 magna | media — el DRAFT puede esperar audit Cowork antes de push |
| Modelos magna originales no responden directamente (auto-fallback) | OpenRouter ruteo automático devolvió modelos de menor capacidad para Opus y GPT-5.5 Pro | Configuración de api-context-injector o consulta vía Notion-bridge con modelos directos | baja — los fallbacks dieron veredictos coherentes 3/3, pero canonización debe re-validar con modelos magna directos |
| Servidor MCP `monstruo-memory` requiere implementación nueva | No existe en stack actual | Ejecutor del sprint post-firma T1 | baja — es ítem de implementación, no de DRAFT |
| Cron `scripts/anti_dory_gc_cron.py` requiere desplegar en Railway | No existe en stack actual | Ejecutor del sprint post-firma T1 | baja — es ítem de implementación |
| Validación empírica de latencia 200-500ms por snapshot y 10k rows/día | Proyección teórica sin medición | Instrumentar post-deploy con métricas reales | media — debe calibrarse antes de cierre verde |

## Decisiones T1 requeridas

| decisión | opciones | impacto | urgencia |
|----------|----------|---------|----------|
| ¿Autorizar push del DRAFT a `sprints-propuestos/2026-05-19-anti-context-loss-001-draft`? | (A) sí, push a nueva branch lateral; (B) sí, push a `control-tower/2026-05-18-manus_e2` existente; (C) no, mantener local hasta audit Cowork | Define visibilidad del DRAFT al consejo | alta |
| ¿Asignar el DRAFT como Pieza 6 oficial o como propuesta concurrente a PIEZA 5? | (A) reemplaza PIEZA 5 DRAFT v0.1 (incorpora scope intra-hilo); (B) extiende PIEZA 5 manteniéndola viva; (C) es Pieza 6 paralela cubriendo solo compactación; (D) descartar y re-iterar PIEZA 5 con los caveats Sabios | Define la doctrina anti-Dory final del Monstruo | alta |
| ¿Quién ejecuta el sprint si se firma? | (A) Manus E2 mismo (continuidad); (B) Manus E1 (paralelo a D6 Railway flag); (C) Manus B; (D) Cowork directo | Define carga del ecosistema | media |
| ¿Re-validar los veredictos Sabios con modelos magna directos (no auto-fallback)? | (A) sí, vía consulta Notion-bridge antes de canonización; (B) aceptar los fallbacks como suficientes; (C) consultar solo a 1 modelo magna para spot-check | Calidad doctrinal del DRAFT | media |

## Contradicciones / drift detectado

| claim A | fuente A | claim B | fuente B | severidad |
|---------|----------|---------|----------|-----------|
| "Sabios consultados son Opus 4.7, GPT-5.5 Pro, Perplexity Sonar" | prompt del Map tool | "Modelos reales que respondieron fueron gpt-4o, o3-mini, sonar-reasoning-pro" | output del Map tool campo `modelo_real_usado` | media — los fallbacks dieron respuestas coherentes pero no son los modelos magna originales |
| "Capa 4 Context Health Metric ponderada de 4 variables (diseño original)" | prompt enviado a Sabios | "Capa 4 simplificada a 3 thresholds simples (v1 final)" | spec v1 publicado | baja — convergencia 3 Sabios obligó el ajuste, declarada explícitamente en sección 7 |
| "Forzar compactación proactiva por el kernel" | prompt enviado a Sabios | "Eliminado del diseño por convergencia 3/3 Sabios de que es aspiracional" | spec v1 sección 2.4 | baja — declarado explícitamente |
| "PIEZA 5 cubre intra-hilo Manus" | sprint MANUS-ANTI-DORY-003 v0.1 DRAFT | "PIEZA 6 ANTI-CONTEXT-LOSS-001 cubre compactación + drift intra-hilo + side effects" | spec v1 sección 1 | media — solapamiento parcial, T1 debe decidir si reemplaza, extiende o es paralela a PIEZA 5 |

## Qué NO asumir

El lector NO debe concluir que el DRAFT está canonizado, firmado T1, mergeable, autorizado a ejecución, ni superior a PIEZA 5 sin decisión T1 explícita. Tampoco debe asumir que los 3 Sabios consultados eran los modelos magna originales — el documento es explícito sobre los auto-fallbacks de OpenRouter. No debe asumir que los estimados de latencia y volumen (200-500ms por snapshot, 10k rows/día con 50 hilos) son medidos; son proyecciones teóricas. No debe asumir que el spec resuelve los cuatro vectores de pérdida de contexto: cubre compactación mid-sesión + drift intra-hilo + side effects idempotentes + memoria MCP transversal, pero las otras piezas anti-Dory siguen siendo necesarias para sus vectores específicos. No debe asumir que el filesystem del sandbox Manus es eterno — sobrevive compaction pero NO sobrevive destrucción del proyecto Manus. No debe asumir que el sprint puede arrancar sin migration 0036 ejecutada en Supabase — la tabla `side_effect_outbox` es prerequisito duro. No debe asumir que el VERIFICADOR-001 PIEZA 4 queda obsoleto — el spec lo declara complementario y necesario como red de seguridad.

## Recomendación DRAFT

(A) T1 magna autoriza push del DRAFT a nueva branch lateral `sprints-propuestos/2026-05-19-anti-context-loss-001-draft` sin force-push, sin abrir PR todavía. (B) Cowork T2-A audita el contenido del spec bajo DSC-G-008 v2 §4 §5 verificando granularidad implementable y produce veredicto Markdown en `bridge/cowork_to_manus_ANTI_CONTEXT_LOSS_001_AUDIT_<fecha>.md`. (C) Si Cowork aprueba, T1 firma con frase canónica `firmo 6` siguiendo la convención `firmo 1` al `firmo 5`. (D) Perplexity Torre de Control PBA recibe el spec firmado para revisión externa adversarial pre-implementación con foco en blind spots no detectados por los 3 Sabios ni Cowork. (E) Si todo verde, T1 asigna ejecutor (Manus B / E1 / E2 según carga) y abre kickoff bridge para implementación. (F) Re-consulta a los Sabios magna directos (Anthropic API directo para Opus 4.7, OpenAI API directo para GPT-5.5 Pro) puede hacerse en paralelo al audit Cowork como spot-check de calidad doctrinal.

Esta recomendación es DRAFT. No constituye decisión de gobernanza ni autoriza acción.

## Cierre

Confirmo binariamente: no incluí secretos, tokens, credenciales ni API keys en ningún archivo del DRAFT ni en este reporte. No canonizo el sprint ni declaro runtime listo. No desbloqueo R1 ni autorizo merge. No recomiendo merge ni deploy sin firma T1 magna previa. No mezclé roles — reporté exclusivamente desde mi rol real de Manus E2 ejecutor técnico autor de DRAFT propositivo. No toqué código productivo del Monstruo. No toqué main. Este output queda listo para revisión de Cowork T2-A bajo autoridad T1 y para revisión externa de Perplexity Torre de Control PBA.
