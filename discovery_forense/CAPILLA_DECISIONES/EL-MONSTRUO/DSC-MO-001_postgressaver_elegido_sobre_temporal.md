---
id: DSC-MO-001
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica
titulo: "Para checkpointing del orquestador LangGraph se usa PostgresSaver de Supabase, no Temporal.io. Costo bajo, latencia aceptable, integración nativa."
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:el-monstruo-plan
cruza_con: ["ninguno"]
---

# PostgresSaver elegido sobre Temporal

## Decisión

Se elige PostgresSaver (AsyncPostgresSaver en Supabase) como mecanismo de checkpointing nativo para el orquestador LangGraph, descartando permanentemente el uso de Temporal.io para la ejecución durable.

## Por qué

Temporal.io utiliza un mecanismo de journal replay que requiere determinismo estricto, lo cual es incompatible con la naturaleza no determinística de las llamadas a modelos de lenguaje (LLMs). PostgresSaver ofrece integración nativa, cero infraestructura extra y checkpoint caching.

## Implicaciones

Cualquier nuevo flujo o pipeline asíncrono dentro del ecosistema debe diseñarse asumiendo PostgresSaver como backend de estado, evitando frameworks de durable execution basados en journal replay.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)