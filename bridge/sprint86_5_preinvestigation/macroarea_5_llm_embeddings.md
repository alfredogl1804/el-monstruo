> Hilo Manus Catastro · 2026-05-04 · Standby Productivo
> Entrega B: Macroárea 5 LLM Embeddings
> Validación tiempo real ejecutada el 2026-05-04. Fuentes primarias: MTEB Leaderboard, PE Collective (abril 2026).

---

## 1. Justificación de macroárea

La **Macroárea 5 — LLM Embeddings** se separa del resto porque estos modelos no generan texto (output de inferencia generativa), sino que producen vectores matemáticos de alta dimensionalidad. Sus métricas críticas no son razonamiento o coding, sino la calidad de recuperación (Retrieval/MTEB), latencia de embedding, longitud de contexto soportada, y capacidad de compresión (Matryoshka/Quantization).

El Catastro necesita trackear estos modelos porque el ecosistema del Monstruo (ErrorMemory, MemPalace, y el Catastro mismo) depende de *semantic search* sobre `pgvector`.

## 2. Análisis del modelo actual del kernel

**Diagnóstico:** El kernel actualmente está fuertemente acoplado a **OpenAI `text-embedding-3-small` (1536 dimensiones)**.
- `kernel/error_memory.py:50`: `DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"`
- `kernel/main.py:132`: Comentario explícito `ThoughtsStore (pgvector + Supabase + text-embedding-3-small)`
- `kernel/main.py:138`: Log de inicialización causal_kb_initialized `embedding="text-embedding-3-small"`

El kernel usa Supabase con la extensión `pgvector` para persistir estos embeddings. El esquema del Catastro (`catastro_modelos`) tiene una columna `embedding: Optional[list[float]]` que actualmente no se persiste (`exclude={"embedding"}` en `persistence.py:385`).

## 3. Modelos frontier observados (Top Embeddings, 2026-05-04)

Basado en MTEB y análisis de mercado reciente (abril 2026):

| Modelo | Proveedor | MTEB Score (aprox) | Costo ($/1M tokens) | Dimensiones Max | Notas |
|---|---|---|---|---|---|
| `voyage-3-large` | Voyage AI | 66.3 | $0.18 | 1024 | Líder absoluto en Code & Technical Docs |
| `Jina Embeddings v3` | Jina AI | 65.5 | $0.02 | 1024 | 8192 context window, late chunking, LoRA adapters |
| `text-embedding-3-large` | OpenAI | 64.6 | $0.13 | 3072 | Soporte Matryoshka (reducible a 256), safest default |
| `embed-v4` | Cohere | 63.8 | $0.10 | 1024 | Líder en Multilingual, compresión int8/binary |
| `text-embedding-3-small` | OpenAI | ~62.3 | $0.02 | 1536 | Modelo actual del kernel, barato pero superado |
| `BGE-M3` | BAAI | 62.4 | Free (Self-hosted) | 1024 | Líder Open Source, multi-vector (dense/sparse) |
| `Nomic Embed v2` | Nomic | ~61.5 | Free / API | 768 | Ideal para Edge/CPU (137M params) |

*Nota:* Qwen3-Embedding y NV-Embed-v2 también muestran puntajes top en MTEB, pero su adopción en pipelines de producción estándar es menor comparada con OpenAI/Voyage/Cohere.

## 4. Impacto de migración (Semantic Search del Catastro)

Migrar el modelo de embeddings en el kernel (ej. de `text-embedding-3-small` a `voyage-3-large` o `text-embedding-3-large`) tiene un **impacto severo y destructivo** si no se maneja correctamente:

1. **Incompatibilidad de dimensiones:** `pgvector` requiere que la dimensión de la columna coincida con el vector. `text-embedding-3-small` es 1536d. `voyage-3-large` es 1024d. Un cambio de modelo rompe las inserciones SQL.
2. **Incompatibilidad semántica:** Incluso si las dimensiones coinciden, el espacio latente de dos modelos distintos es incompatible. Un vector de OpenAI no se puede comparar (cosine similarity) con un vector de Cohere.
3. **Re-embedding masivo:** Migrar implica re-calcular los embeddings de *todos* los registros históricos (ErrorMemory, MemPalace, Catastro).

## 5. Schema delta para provider configurable

Para que el Catastro pueda trackear modelos de embeddings, la convención `data_extra` debe ampliarse:

```python
# kernel/catastro/conventions.py (extensión para Embeddings)
DATA_EXTRA_KEYS_EMBEDDINGS = {
    "dimensions_max": int,          # Dimensión máxima del vector (ej. 3072)
    "matryoshka_support": bool,     # Soporta reducción de dimensiones nativa
    "max_context_length": int,      # Ventana de contexto (ej. 8192)
    "mteb_score_overall": float,    # Score general MTEB
    "best_use_case": str            # "multilingual", "code", "general", "long-doc"
}
```

## 6. Recomendación firme: ¿Migrar o mantener?

**Recomendación: MANTENER `text-embedding-3-small` en el corto plazo (Sprint 86/87), pero preparar la arquitectura para `voyage-3-large` o `text-embedding-3-large` a mediano plazo.**

**Justificación:**
1. **Costo/Beneficio negativo hoy:** El costo operativo de re-calcular todo ErrorMemory y MemPalace y alterar las tablas `pgvector` en producción supera el beneficio marginal de un +3-4% en MTEB score para los casos de uso actuales del Monstruo.
2. **`text-embedding-3-small` es "suficientemente bueno":** A $0.02/1M tokens, es imbatible en precio/rendimiento general y la latencia de OpenAI es estable.
3. **Deuda técnica:** El Catastro ni siquiera está persistiendo sus propios embeddings hoy (`exclude={"embedding"}`). Antes de cambiar el modelo global, el Hilo Ejecutor debe estabilizar la persistencia de vectores actuales.

**Futuro (Sprint 88+):** Cuando el Monstruo escale su RAG sobre código fuente completo (Motor/Motor2), la migración a **Voyage-3-large** será imperativa, ya que es el líder indiscutido en *Code & Technical Docs*.

## 7. Riesgos identificados

1. **Vendor Lock-in Vectorial:** Una vez que acumulas millones de vectores con un proveedor (ej. OpenAI), el costo de migración (re-embedding) te ancla a ese proveedor.
2. **Obsolescencia de MTEB:** El benchmark MTEB está saturado. Modelos sobre-optimizan para MTEB pero fallan en recuperación real con jerga específica del dominio (ej. la nomenclatura única de "El Monstruo", "SOP", "EPIA").
3. **Costos ocultos de contexto largo:** Modelos como Jina v3 soportan 8192 tokens, pero procesar chunks tan grandes dispara el costo de inferencia de embeddings linealmente.
