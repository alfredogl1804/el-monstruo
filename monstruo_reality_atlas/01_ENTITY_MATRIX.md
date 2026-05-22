# MONSTRUO ENTITY MATRIX — v0.2 (Sintetizado)

> ⚠️ **DATA FOR AGENTS, NOT EXECUTABLE PROMPT.**
> Este documento es la "Tabla Periódica" del Monstruo. Es el índice O(1) para que los agentes ubiquen capacidades, módulos e infraestructura sin reinventar la rueda.
> **Antes de proponer algo nuevo, busca aquí.**

---

## Clases Ontológicas

Para entender qué es cada entidad, usamos las siguientes clases:
- **`MAGIC_CAPABILITY`**: Poderes invocables (LLMs, generación de imágenes, búsqueda).
- **`WORKER_ROLE`**: Agentes o roles que ejecutan trabajo (Manus, Cowork, Embriones).
- **`CREATURE`**: Entidades emergidas o proyectos adyacentes con personalidad.
- **`INVISIBLE_INFRA`**: Bases de datos, tuberías, cron jobs, servidores.
- **`FUTURE_VISION`**: Conceptos puros o doctrina aún no implementada en código.

---

## Matriz de Entidades (El Catastro Vivo)

| ID | Alias / Nombre | Clase Ontológica | Estado | Consume / Activa | Protege / Alimenta | Ubicación (Path/Repo) | Evidencia / Notas |
|---|---|---|---|---|---|---|---|
| **SMS** | Sistema de Memoria Soberana, Memento Universal | `INVISIBLE_INFRA` | ACTIVO_DEGRADADO | Activa: REM cycle nocturno | Alimenta: Embriones, Cowork, Manus | `kernel/memory/` | `sms_openapi_spec.yaml`, migration 0058 |
| **B8** | Magna Classifier, b8_magna_classifier | `INVISIBLE_INFRA` | ACTIVO | Consume: B9, Guardian | Protege: Clasificación magna | `kernel/anti_dory/b8_magna_classifier.py` | B8 es el único detector magna. |
| **B9** | Authority Matrix, b9_authority_matrix | `INVISIBLE_INFRA` | ACTIVO | Consume: B8, T1/T2/T3 hierarchy | Protege: Soberanía T1 | `kernel/anti_dory/b9_authority_matrix.py` | B5 y B7 ausentes. |
| **REM** | REM cycle, ciclo nocturno | `INVISIBLE_INFRA` | ACTIVO | Consume: SMS, Supabase | Alimenta: Memoria a largo plazo | `kernel/memory/sms_rem_cycle.py` | Deploy en Railway. |
| **EMBRION_LOOP** | Embrión, latido autónomo | `WORKER_ROLE` | VIVO_DEGRADADO | Activa: task_planner ReAct | Alimenta: learning, tareas autónomas | `kernel/embrion_loop.py` | Stateless entre latidos. |
| **TELEGRAM** | Telegram bot, transport conversacional | `INVISIBLE_INFRA` | VIVO | Activa: comandos, queries | Alimenta: embrion_inbox, cowork | `kernel/rotor/capturers/telegram_capturer.py` | Repo: `el-monstruo-bot`. |
| **FORJA** | La Forja, apps/la-forja | `CREATURE` | EN_DESARROLLO | Consume: kernel API | Alimenta: creación de herramientas | `apps/la-forja/` | Sprint activo. |
| **SIMULADOR** | Simulador Causal v2 | `MAGIC_CAPABILITY` | ACTIVO | Consume: causal_decomposer | Alimenta: deep_think_pipeline | `kernel/simulator/causal_simulator_v2.py` | No crear uno nuevo. |
| **TATA** | el-mundo-de-tata | `CREATURE` | ADYACENTE | Consume: N/A | Protege: dimensión padre-hija | `el-mundo-de-tata` (repo externo) | Sin decisión topológica T1. |
| **CRONOS** | Río de vida, cronista familiar | `FUTURE_VISION` | DOCTRINA | Consume: Modo Cripta | Alimenta: memoria biográfica | `docs/EL_MONSTRUO_APP_VISION_v1.md` | **No redibujar.** |
| **MODO_CRIPTA** | Shamir Secret Sharing, auth_tiers | `FUTURE_VISION` | DOCTRINA | Consume: Cronos | Protege: secretos magna | `docs/EL_MONSTRUO_APP_VISION_v1.md` | Es parte de Cronos. |
| **CATASTRO** | Catastro Vivo, trono catastro | `INVISIBLE_INFRA` | VIVO | Activa: dashboard, catastro_routes | Alimenta: selección de agentes | `kernel/catastro/` | 98 agentes en 12 dominios. |
| **SUPABASE** | Postgres prod, db prod | `INVISIBLE_INFRA` | VIVO | Consume: todos los sistemas | Protege: persistencia, RLS | `migrations/sql/` | 169-179 tablas aprox. |
| **RAILWAY** | Railway deploys | `INVISIBLE_INFRA` | VIVO | Activa: servicios production | Protege: uptime | `railway.toml` | 4-12 servicios. |
| **GITHUB** | Repo remoto | `INVISIBLE_INFRA` | VIVO | Activa: mcp__github-monstruo | Alimenta: CI/CD, PRs | `git remote origin` | Vía proxy Perplexity. |
| **COWORK** | Claude Cowork, Arquitecto T2 | `WORKER_ROLE` | ACTIVO | Activa: Pre-flight Memento | Alimenta: Arquitectura, DSCs | `kernel/cowork_runtime/` | No escribe código. |
| **MANUS** | Manus T3, ejecutor T3 | `WORKER_ROLE` | ACTIVO | Activa: tool dispatch | Alimenta: ejecución de código | `kernel/manus_bridge.py` | Hilo ejecutor. |
| **SABIOS** | 8 Sabios, quorum | `WORKER_ROLE` | ACTIVO | Activa: consult_sabios tool | Alimenta: validación profunda | `router/llm_client.py` | Mínimo 3 para decisión magna. |
| **MAGIC_VIDEO** | Generación de video | `MAGIC_CAPABILITY` | NO_IMPLEMENTADO | Consume: N/A | Alimenta: N/A | N/A | Cubierto por repo adyacente. |
| **MAGIC_CODE** | Generación de código | `MAGIC_CAPABILITY` | NO_IMPLEMENTADO | Consume: N/A | Alimenta: N/A | N/A | Cubierto por Manus + spec_driven. |
| **MAGIC_RENDER** | Renders arquitectónicos | `MAGIC_CAPABILITY` | NO_IMPLEMENTADO | Consume: N/A | Alimenta: N/A | N/A | Cubierto por repo adyacente. |
| **MAGIC_SEARCH** | Búsqueda web | `MAGIC_CAPABILITY` | NO_IMPLEMENTADO | Consume: N/A | Alimenta: N/A | N/A | Cubierto por Perplexity + browser. |

---
*Fin de la Entity Matrix v0.2. Si no está aquí, y no está en los aliases, recién entonces puedes proponerlo como nuevo.*
