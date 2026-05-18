# Veredicto Sabio — Perplexity Sonar T2-B
**Spec bajo audit:** MANUS-ANTI-DORY-003 v0.1 — Pieza 5 Anti-Dory intra-hilo Manus
**Fecha:** 2026-05-18
**Rol del Sabio:** navegador validador externo (browsing tiempo real)
**Veredicto binario:** 🟡 **CON CAVEAT**

---

## 1. ¿"Intra-thread degradation" / "intra-session context drift" es vector reconocido 2024-2026?

**Sí.**

- **Anthropic** describe "context rot" como degradación de recall/razonamiento al crecer el contexto, con finite attention budget, compaction, note-taking y subagents como mitigaciones para agentes multi-hora. Fuente: [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- **Harness** define context rot como fallo estructural de sesiones largas: contexto acumula supuestos obsoletos, detalles irrelevantes y contradicciones; recomienda Plan → Execute → Reset y checkpoints. Fuente: [Harness — Defeating Context Rot](https://www.harness.io/blog/defeating-context-rot-mastering-the-flow-of-ai-sessions).
- El paper **"Context Management for Long-Horizon SWE-Agents"** reporta context explosion, semantic drift y degraded reasoning en interacciones largas, y propone compresión estructurada de trayectorias. Fuente: [arXiv](https://arxiv.org/html/2512.22087v1).

## 2. ¿Qué frameworks resuelven intra-thread refresh? Comparación contra Alt A/B/C

- **LangGraph**: resuelve mejor Alt B/C. Tiene checkpointers, `thread_id`, checkpoints por super-step, replay, time travel, resume y PostgresSaver/AsyncPostgresSaver. Fuentes: [LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution), [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).
- **Anthropic / Claude Code pattern**: cubre Alt A + refresh conceptual vía compaction, structured note-taking, `NOTES.md`, tool-result clearing y subagents. Fuente: [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- **AutoGen**: memoria intra-sesión existe como chat history; memoria persistente requiere extensiones tipo Hindsight/Memori. Sirve menos para refresh intra-hilo nativo. Fuente: [Hindsight AutoGen](https://hindsight.vectorize.io/blog/2026/04/06/autogen-persistent-memory).
- **CrewAI**: no se verificó en este pase una fuente primaria fuerte que demuestre replay/snapshot intra-thread equivalente a LangGraph.

**Comparación:** Alt C es la más alineada. Alt A solo refresca modelo mental; Alt B persiste estado; LangGraph demuestra que la combinación snapshot + replay/resume es el patrón robusto.

## 3. Mejores prácticas que NO aparecen en el spec

- **Compaction formal**: resumir y reiniciar contexto con decisiones, bugs abiertos y archivos recientes, no solo ejecutar `git log` cada N turnos. Fuente: [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- **Replay/time travel**: permitir re-ejecutar desde checkpoint previo y bifurcar estado, como LangGraph `checkpoint_id` replay/fork. Fuente: [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).
- **Idempotency keys para side effects**: LangGraph exige encapsular operaciones no deterministas y side effects para que resume/replay no duplique writes. Fuente: [LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution).
- **Plan → Execute → Reset explícito**: resets frescos con re-inyección mínima de contexto relevante, no solo snapshot acumulativo. Fuente: [Harness](https://www.harness.io/blog/defeating-context-rot-mastering-the-flow-of-ai-sessions).
- **Métrica de context health**: token growth, stale assumptions detected, unresolved decisions, last repo/DB verification age. El spec mide overhead y drift detectado, pero no salud del contexto.

## 4. Veredicto binario

🟡 **CON CAVEAT**.

El vector está reconocido: Anthropic, Harness, LangGraph y arXiv validan context rot, semantic drift, checkpoints, compaction y replay. Caveat: Alt C debe agregar compaction, replay/time-travel, idempotency keys y reset con fresh-context-injection; solo pre-flight cada 10 turnos + snapshot puede acumular basura persistente.

---

**Recibido por:** Cowork T2-A
**Status:** documentado verbatim para anti-Memento. Integración de feedback pendiente convergencia GPT-5.5 Pro + v0.2.
