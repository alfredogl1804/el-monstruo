# AGENT OUTPUT — manus_e2 — ANTI-CONTEXT-LOSS-001 v1.2 + Invalidación Perplexity Sonar

## Metadata
- **agente:** manus_e2
- **rol real:** ejecutor técnico, NO firmante, NO canonizador
- **fecha/hora:** 2026-05-19 05:00 CST
- **rama:** local untracked (esperando autorización push)
- **PR:** ninguno
- **commit:** ninguno (no committed)
- **estado fuente:** EVIDENCE_PACK + DRAFT (no canonización)
- **tocó código:** no
- **tocó main:** no

## Qué hice

1. Recibí del usuario solicitud de explorar 7 vectores no investigados en v1.1 para cerrar más el gap del residual <5%.
2. Consulté 3 Sabios magna directos (Anthropic Claude Opus 4.7, OpenAI GPT-5, Perplexity Sonar Reasoning Pro) vía API directa adversarial.
3. Recibí veredictos: Opus amarillo (frameworks DBOS/Restate como alternativa), GPT-4o (fallback de gpt-5) amarillo 96%, Perplexity Sonar Reasoning Pro verde 98.7%.
4. **Detecté que el veredicto verde 98.7% de Perplexity Sonar Reasoning Pro estaba sustentado en citas sospechosamente específicas.** Apliqué skill `validacion-tiempo-real` obligatoriamente.
5. Validé binariamente 2 citas críticas de Perplexity con navegador real: **CVE-2026-33128 no existe en MITRE** y **arXiv:2603.01245 trata de Whistleblowers, NO de CRDTs**. Patrón de fabricación confirmado.
6. **Invalidé el veredicto Perplexity por fabricación demostrable de evidencia.** Mantuve veredictos amarillo de Opus + GPT-4o.
7. Validé en tiempo real que los frameworks REALES sí existen: DBOS Transact (https://www.dbos.dev/), Restate.dev (https://github.com/restatedev/sdk-python), LangGraph (https://github.com/langchain-ai/langgraph), Temporal, Dapr.
8. Redacté el spec ADDENDUM v1.2 con cura honesta **96%** (no 98.7%) integrando DBOS Transact + LangGraph PostgresSaver como reemplazos de componentes custom v1.1.
9. Declaré honestamente residual <4% en 4 categorías, demostrando que la propia alucinación de Perplexity ES el blind spot #1 (alucinación adversarial LLM) materializándose.

## Evidencia

- Archivo spec v1.2: `bridge/sprints_propuestos/sprint_ANTI_CONTEXT_LOSS_001_v1_2_ADDENDUM_DRAFT.md` (Mac local, untracked)
- Archivos previos del trabajo (en cadena): v1 (`sprint_ANTI_CONTEXT_LOSS_001_v1_DRAFT.md`), v1.1 (`sprint_ANTI_CONTEXT_LOSS_001_v1_1_ADDENDUM_DRAFT.md`), CONTROL TOWER reportes 0345 y 0445
- JSON Sabios magna directos: `/home/ubuntu/consulta_3_sabios_magna_directos_v1_2.json` (sandbox, persistido)
- Validación CVE-2026-33128: navegación oficial a https://www.cve.org/CVERecord?id=CVE-2026-33128 retornó "No article found"
- Validación arXiv:2603.01245: paper real es "Insights for an AI Whistleblower Office from 30 Case Studies" (cs.CY, Mar 2026), tema completamente distinto
- Validación DBOS: https://www.dbos.dev/ + https://github.com/dbos-inc — REAL
- Validación Restate: https://restate.dev/ + https://github.com/restatedev/sdk-python — REAL

## Archivos tocados

| archivo | acción | branch | commit | nota |
|---------|--------|--------|--------|------|
| bridge/sprints_propuestos/sprint_ANTI_CONTEXT_LOSS_001_v1_2_ADDENDUM_DRAFT.md | create | local untracked | ninguno | spec definitivo v1.2 con 96% honesto |
| bridge/control_tower/2026-05-18/manus_e2/2026-05-19_0500_anti_context_loss_v1_2_delta_perplexity_invalidado.md | create | local untracked | ninguno | este reporte CONTROL TOWER |

## Tests / checks

| test/check | resultado | evidencia | nota |
|------------|-----------|-----------|------|
| Consulta 3 Sabios magna directos sin OpenRouter | ✅ ejecutado | JSON con 3 outputs | 2/3 magnas, 1/3 fallback declarado |
| Validación tiempo real CVE-2026-33128 | ✅ ejecutado | Navegación oficial MITRE | ❌ Cita inventada |
| Validación tiempo real arXiv:2603.01245 | ✅ ejecutado | Navegación oficial arXiv | ❌ Tema distinto |
| Validación frameworks DBOS, Restate, LangGraph | ✅ ejecutado | URLs oficiales accesibles | ✅ Reales |
| Cura honesta declarada 96% | ✅ binario | Spec sección 5 | Residual <4% desglosado en 4 categorías |
| Convergencia Sabios magna válidos | ✅ binario | 2/3 amarillo, 1/3 invalidado | Patrón claro |

## Bloqueos

| bloqueo | causa | quién desbloquea | urgencia |
|---------|-------|------------------|----------|
| Push del bloque v1+v1.1+v1.2 a remote | autorización T1 pendiente | Alfredo | media |
| Audit del v1.2 por Cowork T2-A | post-audit de v1 + v1.1 también pendiente | Cowork T2-A | alta |
| Decisión adoptar DBOS vs Restate | trade-off MIT vs BSL/ELv2 + self-hosted | Alfredo + Cowork | media |
| Re-consulta Perplexity con clausula anti-alucinación o descarte | política Sabios T1 | Alfredo | baja |

## Decisiones T1 requeridas

| decisión | opciones | impacto | urgencia |
|----------|----------|---------|----------|
| Adoptar DBOS Transact vs Restate vs mantener custom | DBOS MIT Postgres / Restate BSL self-hosted / custom v1.1 | reduce código -500 líneas | media |
| Adoptar LangGraph PostgresSaver vs custom | LangGraph maduro / custom v1.1 | reduce código -300 líneas | media |
| Aceptar cura honesta 96% o exigir v1.3 que persiga 97-98% | aceptar realista / v1.3 con TLA+ + comprensión verificada | acepta residual <4% declarado | media |
| Re-consultar Perplexity con prompt anti-alucinación o descartar | 2da oportunidad / descarte como Sabio / sustituir por DeepSeek R1 | confiabilidad coro de Sabios | baja |
| Push del bloque a remote | branch lateral sprints-propuestos / mantener local | visibilidad para Cowork audit | media |

## Contradicciones / drift detectado

| claim A | fuente A | claim B | fuente B | severidad |
|---------|----------|---------|----------|-----------|
| "Cura 98.7% con citas de arXiv, CVE, blogs Railway, docs Manus, Cowork pricing" | Perplexity Sonar Reasoning Pro vía SONAR_API_KEY directo | "CVE-2026-33128 no existe, arXiv:2603.01245 trata de whistleblowers" | MITRE oficial + arXiv oficial | CRÍTICA — fabricación de evidencia por Sabio |
| "GPT-5 directo" en prompt | OPENAI_API_KEY directo solicitado | "gpt-4o" declarado en respuesta | OpenAI API real | media — fallback aceptable, gpt-5 no expuesto |
| Triple replicación es over-engineering, CRDTs lo reemplazan al 90% | Perplexity (invalidado) | CRDTs solo cubren snapshots no críticos, triple replicación sigue necesaria | Opus + GPT-4o convergencia | alta — solo Opus + GPT-4o son fuente confiable |

## Qué NO asumir

1. NO asumir que el spec v1.2 está canonizado — sigue como DRAFT propositivo
2. NO asumir que la cura 96% es contractual — es estimación honesta basada en 2 Sabios magna válidos
3. NO asumir que Perplexity Sonar Reasoning Pro es ahora "untrustworthy permanentemente" — el caso documentado es un episodio adversarial, política a definir por T1
4. NO asumir que DBOS / LangGraph se adoptarán automáticamente — son recomendaciones DRAFT que requieren audit Cowork + decisión T1
5. NO asumir que el residual <4% se reducirá más con v1.3 — TLA+ y comprensión verificada LLM son investigación abierta, no productos
6. NO asumir que el push está autorizado — el archivo está untracked en el Mac
7. NO asumir que VERIFICADOR-001 actual (Pieza 4 ya mergeada) es suficiente — el caso Perplexity demuestra que validación tiempo real obligatoria por Manus sigue siendo necesaria como red de seguridad

## Recomendación DRAFT

**DRAFT-1:** Aceptar cura honesta 96% del v1.2 antes que perseguir 97-98% con investigación abierta.

**DRAFT-2:** Adoptar DBOS Transact como reemplazo de Mec 3 idempotency_proxy custom — beneficio neto -500 líneas + exactly-once formal.

**DRAFT-3:** Adoptar LangGraph PostgresSaver como reemplazo de Mec 1 snapshot_writer custom (capa Supabase) — beneficio neto -300 líneas + primitives maduros.

**DRAFT-4:** Mantener Echo-Back custom (Mec 2) sin reemplazo — no hay framework open-source para este vector específico.

**DRAFT-5:** Política nueva sobre Sabios: cuando un Sabio entregue veredicto extremo (verde puro con cura >97%), invocar obligatoriamente validación tiempo real de TODAS sus citas antes de integrar. Codificar como skill `consulta-sabios v2`.

**DRAFT-6:** Push del bloque v1+v1.1+v1.2 a branch lateral `sprints-propuestos/2026-05-19-anti-context-loss-001-draft` para visibilidad de Cowork T2-A, sin merge a main.

## Cierre

Confirmo:
- ✅ No incluí secretos, tokens, API keys ni credenciales
- ✅ No canonizo nada
- ✅ No desbloqueo R1
- ✅ No recomiendo merge/deploy sin T1
- ✅ Validé en tiempo real las citas de los Sabios magna antes de integrarlas
- ✅ Reporté binariamente la fabricación de evidencia por Perplexity y la descarté
- ✅ Cura honesta declarada 96% con residual <4% en 4 categorías
- Este output queda listo para revisión de Perplexity Torre de Control PBA (paradójicamente, el mismo modelo cuyas citas se invalidaron — recomiendo asignación a Sabio alternativo si T1 acepta DRAFT-5)
