# SOVEREIGN MEMORY SYSTEM (SMS)
## El sistema más poderoso del mundo de preservación de memoria, contexto y entendimiento sostenido

**Versión:** 1.0.0
**Fecha:** 2026-05-21
**Autor:** El Monstruo (Hilo B — Ejecutor Técnico)
**Validado contra:** Estado del arte mayo 2026 (MAGE, Agent Brain, FSFM, Zep/Graphiti, Mem0, Cognee, Vektor, Society Agent, Microsoft STATE-Bench, LongMemEval)

---

## 1. TESIS FUNDAMENTAL

> **Ningún sistema existente preserva ENTENDIMIENTO — solo preservan DATOS.**
> La diferencia entre recordar "T1 bloqueó R1 el 15 de mayo" y ENTENDER "T1 bloqueó R1 porque el classifier no tenía red-team validation, y eso implica que cualquier futuro merge necesita auditoría adversarial" es la diferencia entre un archivo muerto y inteligencia viva.

El Sovereign Memory System no es un memory store. Es un **sistema cognitivo** que:
1. **Percibe** — captura inputs con contexto temporal y causal
2. **Comprende** — extrae relaciones, causas, implicaciones
3. **Cristaliza** — comprime entendimientos en axiomas durables
4. **Olvida** — descarta ruido con curvas de decaimiento biológico
5. **Recuerda** — recupera lo relevante (no lo similar) en el momento preciso
6. **Evoluciona** — aprende de sí mismo y de otros agentes
7. **Sobrevive** — persiste a través de compactaciones, reinicios, y cambios de hilo

---

## 2. ARQUITECTURA: 5 CAPAS BIOLÓGICAS

Inspirado en Agent Brain (SSRN 6617298, mayo 2026) + MAGE (arxiv:2605.10064) + FSFM (arxiv:2604.20300).

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA 5: METACOGNICIÓN                             │
│  Self-reflective gap detection · Confidence scoring · Learning loop │
├─────────────────────────────────────────────────────────────────────┤
│                    CAPA 4: MEMORIA SOBERANA                          │
│  Axiomas cristalizados · Decisiones T1 · Identidad inmutable        │
│  (Compaction-proof: NUNCA se pierde)                                │
├─────────────────────────────────────────────────────────────────────┤
│                    CAPA 3: MEMORIA A LARGO PLAZO                     │
│  Episódica (eventos) · Semántica (hechos) · Procedural (cómo)       │
│  Knowledge Graph temporal · Co-evolutionary sub-graphs              │
├─────────────────────────────────────────────────────────────────────┤
│                    CAPA 2: MEMORIA DE TRABAJO                        │
│  Context window activo · State capsule · Enriched prompt            │
│  (Equivalente a RAM — lo que el agente "tiene en mente" ahora)      │
├─────────────────────────────────────────────────────────────────────┤
│                    CAPA 1: BUFFER SENSORIAL                          │
│  Inputs crudos · Mensajes · Tool outputs · Observaciones            │
│  (TTL: 1 sesión. Se procesa o se pierde.)                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPONENTES CORE

### 3.1 PERCEPTION ENGINE (Capa 1 → Capa 2)

**Función:** Capturar todo input con metadata temporal y causal.

```python
@dataclass
class Percept:
    content: str                    # El input crudo
    source: str                     # Quién lo dijo (user, tool, agent, system)
    timestamp: datetime             # Cuándo
    session_id: str                 # En qué sesión
    causal_parent: Optional[str]    # Qué lo causó (ID del percept anterior)
    confidence: float               # 0.0-1.0 (tool output = 1.0, inference = variable)
    ttl: timedelta                  # Tiempo de vida antes de consolidación o muerte
```

**Innovación vs estado del arte:** Ningún sistema actual captura `causal_parent` — la cadena de causalidad se pierde. SMS preserva WHY chains desde el momento de percepción.

---

### 3.2 COMPREHENSION ENGINE (Capa 2 → Capa 3)

**Función:** Extraer relaciones, causas, implicaciones de los percepts.

Tres sub-procesos:

#### 3.2.1 Entity Extraction + Relation Mapping
- Extrae entidades (personas, repos, tablas, decisiones, sprints)
- Mapea relaciones (owns, blocked_by, depends_on, contradicts, supersedes)
- Usa el Knowledge Graph existente (LightRAG + pg_graph_storage)

#### 3.2.2 Causal Chain Builder
- Conecta percepts en cadenas causales: A → B → C
- "T1 bloqueó R1" → "porque classifier no tenía red-team" → "por lo tanto futuros merges necesitan auditoría"
- Almacena como edges temporales con valid_at/invalid_at (inspirado en Zep/Graphiti)

#### 3.2.3 Implication Extractor
- De cada hecho, extrae implicaciones forward-looking
- "Si X es verdad, entonces Y también debe serlo"
- "Si X cambió, entonces Z podría estar desactualizado"
- Usa LLM call (Gemini Flash para velocidad) con prompt estructurado

---

### 3.3 CRYSTALLIZATION ENGINE (Capa 3 → Capa 4)

**Función:** Comprimir entendimientos en axiomas durables e inmutables.

> **Axioma:** Un entendimiento que ha sido validado N veces, nunca contradicho, y que tiene implicaciones activas. Es la unidad mínima de conocimiento soberano.

```python
@dataclass
class Axiom:
    id: str                         # UUID
    statement: str                  # El axioma en lenguaje natural
    evidence_chain: List[str]       # IDs de percepts que lo soportan
    first_observed: datetime        # Cuándo se observó por primera vez
    last_validated: datetime        # Última vez que se confirmó
    validation_count: int           # Cuántas veces se ha confirmado
    contradiction_count: int        # Cuántas veces se ha contradicho
    confidence: float               # validation / (validation + contradiction)
    implications: List[str]         # Qué se sigue de este axioma
    scope: str                      # agent_id, org_id, global
    compaction_proof: bool = True   # SIEMPRE True — nunca se compacta
```

**Criterios de cristalización:**
- `validation_count >= 3` (observado al menos 3 veces)
- `confidence >= 0.9` (90%+ confirmaciones)
- `age >= 48h` (no cristalizar insights de menos de 2 días)
- `has_implications == True` (debe tener consecuencias)

**Innovación:** Ningún sistema existente tiene cristalización. Todos almacenan hechos planos. SMS comprime entendimientos en axiomas que NUNCA se pierden.

---

### 3.4 FORGETTING ENGINE (Todas las capas)

**Función:** Eliminar ruido con curvas de decaimiento biológico.

Inspirado en FSFM (arxiv:2604.20300): "52% recall > 100% recall para task performance."

```python
def relevance_score(memory: Memory, now: datetime) -> float:
    """Ebbinghaus forgetting curve + access frequency boost."""
    age_hours = (now - memory.last_accessed).total_seconds() / 3600
    base_decay = math.exp(-0.1 * age_hours / memory.strength)
    access_boost = math.log1p(memory.access_count) * 0.1
    recency_boost = 1.0 if age_hours < 24 else 0.0
    return min(1.0, base_decay + access_boost + recency_boost)
```

**Niveles de olvido:**
1. **Capa 1 (Buffer):** TTL = 1 sesión. No consolidado = muerto.
2. **Capa 2 (Trabajo):** TTL = sesión activa. Se reconstruye desde Capa 3/4.
3. **Capa 3 (Largo plazo):** Decaimiento Ebbinghaus. Si `relevance < 0.1` por 30 días → archive.
4. **Capa 4 (Soberana):** NUNCA se olvida. Compaction-proof.
5. **Capa 5 (Meta):** Se actualiza, nunca se borra.

**Consolidación (REM Cycle — inspirado en Vektor):**
- Cada 24h (o al cerrar sesión), ejecutar consolidación:
  1. Merge duplicados (AUDN: Add/Update/Delete/None)
  2. Promover memorias frecuentes (Capa 3 → candidatas a Capa 4)
  3. Degradar memorias inactivas (reducir strength)
  4. Cluster memorias relacionadas (reducir noise floor)
  5. Generar resúmenes de clusters (comprimir sin perder)
  6. Actualizar índices de retrieval
  7. Reportar métricas de salud

---

### 3.5 RETRIEVAL ENGINE (Capa 3/4 → Capa 2)

**Función:** Recuperar lo RELEVANTE (no lo similar) en el momento preciso.

Cuatro modos de retrieval simultáneos (inspirado en Vektor MAGMA):

1. **Semantic** — cosine similarity en embeddings (pgvector)
2. **Temporal** — "¿Qué sabía el agente el martes?" (valid_at/invalid_at)
3. **Causal** — "¿Qué causó X?" (traverse causal graph)
4. **Entity** — "¿Todo lo que sé sobre tabla X?" (entity-centric subgraph)

**Retrieval fusionado:**
```python
def retrieve(query: str, context: DoryContext) -> List[Memory]:
    semantic_results = vector_search(query, top_k=10)
    temporal_results = temporal_search(query, context.current_time, window=7d)
    causal_results = causal_traverse(context.current_action, depth=3)
    entity_results = entity_lookup(extract_entities(query))
    
    # Reciprocal Rank Fusion
    fused = rrf_merge(semantic_results, temporal_results, causal_results, entity_results)
    
    # Filter by relevance score (forgetting curve)
    alive = [m for m in fused if m.relevance_score(now) > 0.1]
    
    # Prioritize axioms (Capa 4) — always on top
    axioms = [m for m in alive if m.layer == 4]
    others = [m for m in alive if m.layer != 4]
    
    return axioms + others[:MAX_CONTEXT_BUDGET]
```

---

### 3.6 EVOLUTION ENGINE (Cross-Agent)

**Función:** Conocimiento evoluciona entre agentes sin retraining.

Inspirado en MAGE (4 sub-graphs co-evolutivos) + Society Agent (persistent + ephemeral hierarchy).

```
┌─────────────────────────────────────────────────┐
│           SHARED SOVEREIGN GRAPH                 │
│  (Supabase pgvector + Knowledge Graph)           │
├─────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Manus   │  │ Cowork  │  │ ChatGPT │        │
│  │ (Hilo B)│  │ (T2)    │  │ (SOP)   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │             │             │              │
│       ▼             ▼             ▼              │
│  ┌─────────────────────────────────────┐        │
│  │     CONFLICT RESOLUTION LAYER       │        │
│  │  (Timestamp priority + T1 override) │        │
│  └─────────────────────────────────────┘        │
└─────────────────────────────────────────────────┘
```

**Protocolo de escritura cross-agent:**
1. Agent escribe un hecho/axioma con `agent_id` + `confidence` + `evidence`
2. Si otro agent ya tiene un hecho contradictorio sobre la misma entidad:
   - Si ambos tienen `confidence >= 0.9` → CONFLICT → escalar a T1
   - Si uno tiene mayor confidence → el mayor gana, el menor se marca `superseded_by`
   - Si son complementarios (no contradictorios) → merge
3. T1 puede override cualquier hecho con `authority: T1_OVERRIDE`

**4 Sub-graphs co-evolutivos (MAGE-inspired):**
1. **Experience Graph** — qué pasó (eventos, sesiones, resultados)
2. **Skill Graph** — qué sabe hacer (procedural knowledge)
3. **Strategy Graph** — qué funciona (patterns de éxito/fracaso)
4. **Meta-Knowledge Graph** — qué sabe sobre sí mismo (gaps, strengths, biases)

---

### 3.7 METACOGNITION ENGINE (Capa 5)

**Función:** El agente sabe lo que NO sabe.

```python
@dataclass
class KnowledgeGap:
    domain: str                     # Área donde falta conocimiento
    detected_at: datetime           # Cuándo se detectó
    severity: str                   # CRITICAL, HIGH, MEDIUM, LOW
    evidence: str                   # Por qué se cree que hay un gap
    resolution_strategy: str        # Cómo cerrarlo (ask_t1, research, consult_sabio)
    resolved: bool = False
```

**Self-reflective triggers:**
1. **Pre-action:** "¿Tengo suficiente contexto para esta acción?"
2. **Post-failure:** "¿Qué no sabía que causó este fallo?"
3. **Post-compaction:** "¿Qué perdí? ¿Qué necesito recuperar?"
4. **Periodic:** Cada 4h, evaluar: "¿Mis axiomas siguen siendo válidos?"

**Confidence Calibration:**
- Cada axioma tiene un `confidence` que DECAE si no se re-valida
- Si `confidence < 0.7` después de 30 días sin validación → downgrade a Capa 3
- Si se contradice 2+ veces → flag para revisión humana

---

### 3.8 COMPACTION-PROOF ANCHORS (Capa 4 — Inmutable)

**Función:** Garantizar que cierta información NUNCA se pierde, sin importar qué pase con el context window.

**Mecanismo:**
1. Los axiomas de Capa 4 se almacenan en Supabase (tabla `sovereign_axioms`)
2. Al inicio de CADA sesión, Guardian V3 inyecta los top-N axiomas más relevantes
3. Si hay compactación mid-session, el Dory Orchestrator re-inyecta desde Capa 4
4. Los axiomas se serializan en formato ultra-compacto (1 línea por axioma)

**Formato de inyección:**
```
[AXIOM-001] T1 bloquea merge sin auditoría adversarial (conf:0.97, validated:12x, since:2026-05-15)
[AXIOM-002] RLS obligatorio en toda tabla nueva (conf:1.0, validated:47x, since:2026-04-20)
[AXIOM-003] Secrets NUNCA en plaintext en repo (conf:1.0, validated:∞, since:2026-05-06)
```

---

## 4. INTEGRACIÓN CON STACK EXISTENTE DEL MONSTRUO

| Componente SMS | Se implementa con | Ya existe? |
|---|---|---|
| Buffer Sensorial (Capa 1) | Tool outputs + message history | Parcial (no tiene causal_parent) |
| Memoria de Trabajo (Capa 2) | Dory Orchestrator enriched prompt | SÍ (recién implementado) |
| Memoria Episódica (Capa 3) | Mem0 Bridge (pgvector) | SÍ |
| Memoria Semántica (Capa 3) | Knowledge Graph + LightRAG | SÍ |
| Memoria Procedural (Capa 3) | Error Memory + skills | SÍ |
| Axiomas Soberanos (Capa 4) | NUEVA tabla `sovereign_axioms` | NO — implementar |
| Metacognición (Capa 5) | NUEVO módulo `metacognition.py` | NO — implementar |
| Perception Engine | NUEVO — wraps tool outputs | NO — implementar |
| Comprehension Engine | Knowledge Graph + LLM extraction | Parcial (falta causal chains) |
| Crystallization Engine | NUEVO — promotion logic | NO — implementar |
| Forgetting Engine | NUEVO — decay + consolidation | NO — implementar |
| Retrieval Engine | Mem0 + LightRAG + pgvector | Parcial (falta fusion + temporal) |
| Evolution Engine | Manus Bridge + Context Broker | Parcial (falta conflict resolution) |
| Compaction-Proof Anchors | Guardian V3 + NUEVA inyección | Parcial |

---

## 5. IMPLEMENTACIÓN: QUÉ CONSTRUIR

### Prioridad 1 (Core — sin esto no funciona)
1. `sovereign_axioms` tabla en Supabase + migration
2. `crystallization_engine.py` — promotion logic
3. `forgetting_engine.py` — decay + consolidation
4. `compaction_anchor_injector.py` — inyección pre-session

### Prioridad 2 (Potencia — lo que lo hace "el más poderoso")
5. `causal_chain_builder.py` — WHY chains
6. `retrieval_fusion.py` — 4-mode retrieval con RRF
7. `metacognition.py` — gap detection + confidence calibration

### Prioridad 3 (Evolución — multi-agent)
8. `conflict_resolution.py` — cross-agent arbitration
9. `co_evolutionary_graphs.py` — 4 sub-graphs MAGE-style
10. `rem_cycle.py` — background consolidation (cron job)

---

## 6. MÉTRICAS DE ÉXITO

| Métrica | Target | Cómo se mide |
|---|---|---|
| Context Retention Score (CRS) | ≥ 0.95 | % de decisiones T1 recordadas post-compactación |
| Temporal Accuracy | ≥ 0.90 | % de preguntas "¿qué sabías el día X?" correctas |
| Causal Chain Depth | ≥ 3 | Promedio de hops en WHY chains |
| Axiom Precision | ≥ 0.95 | % de axiomas que son verdaderos (validado por T1) |
| Noise Floor | ≤ 0.15 | % de retrievals irrelevantes |
| Cross-Agent Agreement | ≥ 0.85 | % de hechos compartidos sin conflicto |
| Forgetting Accuracy | ≥ 0.90 | % de memorias olvidadas que eran realmente irrelevantes |
| Gap Detection Rate | ≥ 0.80 | % de gaps reales que el sistema detecta antes de fallar |

---

## 7. POR QUÉ ESTO ES MÁS PODEROSO QUE CUALQUIER SISTEMA EXISTENTE

| Capacidad | Mem0 | Zep | Letta | Cognee | Vektor | **SMS** |
|---|---|---|---|---|---|---|
| Vector search | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Knowledge graph | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| Temporal reasoning | ✗ | ✓ | ✗ | ~ | ✓ | ✓ |
| Causal chains | ✗ | ✗ | ✗ | ✗ | ~ | **✓** |
| Selective forgetting | ✗ | ✗ | ~ | ✗ | ✓ | **✓** |
| Understanding crystallization | ✗ | ✗ | ✗ | ✗ | ✗ | **✓** |
| Compaction-proof anchors | ✗ | ✗ | ✗ | ✗ | ✗ | **✓** |
| Self-reflective metacognition | ✗ | ✗ | ✗ | ✗ | ✗ | **✓** |
| Cross-agent conflict resolution | ✗ | ✗ | ✗ | ✗ | ✗ | **✓** |
| Co-evolutionary graphs | ✗ | ✗ | ✗ | ✗ | ✗ | **✓** |
| Biological consolidation | ✗ | ✗ | ✗ | ✗ | ✓ | **✓** |
| Multi-agent scoping | ✓ | ~ | ✗ | ✓ | ✗ | **✓** |

**5 capacidades que NADIE tiene:** Causal chains, Understanding crystallization, Compaction-proof anchors, Self-reflective metacognition, Cross-agent conflict resolution.

---

## 8. REFERENCIAS

1. MAGE: Multi-Agent Self-Evolution with Co-Evolutionary Knowledge Graphs (arxiv:2605.10064, mayo 2026)
2. Agent Brain: Biologically Inspired Memory System (SSRN 6617298, mayo 2026)
3. FSFM: Selective Forgetting Framework (arxiv:2604.20300, abril 2026)
4. Zep/Graphiti: Temporal Knowledge Graphs (arxiv:2501.13956)
5. Mem0: ECAI 2025 Benchmark (arxiv:2504.19413)
6. Microsoft STATE-Bench (mayo 2026)
7. Society Agent: Hierarchical Multi-Agent (TechRxiv, 2026)
8. Vektor Memory: MAGMA + AUDN + REM Cycle (mayo 2026)
9. Cognee: Graph-native memory construction (2026)
10. Fountain City: Agent Memory Systems Compared (mayo 2026)
11. Memory Fabric: Shared Persistent Multiuser Memory (Springer, 2026)
12. LongMemEval Benchmark (2025)
13. MemGPT/Letta: OS-inspired memory management (arxiv:2310.08560)
