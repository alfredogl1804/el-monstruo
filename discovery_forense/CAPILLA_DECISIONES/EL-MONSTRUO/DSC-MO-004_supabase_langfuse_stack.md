---
id: DSC-MO-004
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica
titulo: "Supabase para auth+DB+pgvector, Langfuse para tracing LLM. Stack mínimo viable observable Sprint 27."
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:el-monstruo-plan
cruza_con: ["ninguno"]
---

# Supabase para auth+DB+pgvector, Langfuse para tracing LLM. Stack mínimo viable observable Sprint 27.

## Decisión

Se establece Supabase como backend principal para autenticación, base de datos relacional y almacenamiento vectorial (pgvector 0.8.0) para MemPalace y Mem0. Se integra Langfuse (4.5.0) para observabilidad y tracing de LLMs, utilizando un patrón de puente con un EventStore soberano como copia principal y Langfuse como copia commodity.

## Por qué

Supabase consolida múltiples necesidades (auth fail-closed, DB, pgvector persistente) eliminando dependencias efímeras como ChromaDB en Railway. Langfuse proporciona observabilidad especializada para LLMs, pero se requiere el patrón de puente para mantener la soberanía de los datos en el EventStore propio.

## Implicaciones

Cualquier nuevo componente que requiera persistencia o búsqueda vectorial debe usar Supabase. Todo el tráfico de LLMs debe pasar por el EventStore soberano antes de enviarse a Langfuse.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)