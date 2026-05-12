---
id: DSC-MO-003
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica
titulo: "LangGraph elegido para orquestación de agentes con grafo dirigido. Estado, edges condicionales, checkpointing."
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:el-monstruo-plan
  - skill:el-monstruo-toolkit
cruza_con: [ninguno]
---

# LangGraph elegido para orquestación de agentes con grafo dirigido. Estado, edges condicionales, checkpointing.

## Decisión

Se elige LangGraph como el orquestador principal del kernel para El Monstruo, implementando un grafo dirigido de 8 nodos con estado persistente, edges condicionales y checkpointing nativo (AsyncPostgresSaver). Se descarta permanentemente Temporal debido a su incompatibilidad con el no-determinismo de los LLMs (journal replay).

## Por qué

LangGraph permite lógica condicional dentro de los nodos (HITL v2), no requiere infraestructura extra, y su sistema de checkpoint caching es compatible con llamadas a LLMs. Temporal fue descartado porque los frameworks basados en journal replay requieren determinismo estricto, lo cual rompe con las respuestas no determinísticas de los modelos de lenguaje.

## Implicaciones

El kernel operará exclusivamente sobre LangGraph (v1.1.9+). Cualquier nuevo flujo o modo operativo deberá modelarse como nodos y edges dentro de este grafo. La persistencia de estado dependerá de Supabase Postgres.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)