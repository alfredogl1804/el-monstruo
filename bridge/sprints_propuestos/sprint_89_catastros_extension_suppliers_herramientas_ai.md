# Sprint 89 — Extensión Catastros: Suppliers Humanos + Herramientas AI Especializadas

**Estado:** Propuesto  
**Hilo:** Ejecutor (Alfredo)  
**ETA (actualizado):** 30-90 min reales (velocity: 2-3 refactorings per hilo + test suite)  
**Objetivo Maestro:** #3 (Mínima complejidad) + #7 (No reinventar la rueda)

---

## Audit Pre-Sprint

**Current Catastro State:**
- Location: `kernel/catastro.py`, v1.0-stable
- Scope: Single catastro (LLM models only) — 6 entries (GPT, Claude, Gemini, Grok, Kimi, DeepSeek)
- Pattern: Simple key-value registry with metadata (name, endpoint, max_tokens, cost/1k)
- Integration: Loaded by engine.py at startup, consulted by execute node
- Stability: Zero incidents, 99.9% uptime last 30d

**Gap Analysis:**
- Current: Only LLM models, no supplier ecosystem representation
- Target: 3 parallel catastros sharing infrastructure
  1. Catastro Models (LLM): GPT, Claude, Gemini, Grok, Kimi, DeepSeek
  2. Catastro Suppliers Humanos: Alfredo (PM), Manus (agente), Future hires
  3. Catastro Tools AI: Perplexity, Tavily, Duckduckgo, Chain APIs, Custom plugins
- Architectural debt: No shared base class = 3x code duplication risk

**Velocity Factors:**
- Refactoring: -15min (consolidate to CatastroBase)
- Testing: +20min (3 catastros × unit + integration)
- Documentation: +10min (README, type hints)
- Contingency: +15min (edge cases in lookups)

---

## Tareas del Sprint

### Tarea 1: Refactor `Catastro` → `CatastroBase` (Clase Genérica)

**Descripción:**
Extraer patrón común de todas 3 catastros en clase base genérica `CatastroBase<T>` que:
- Define schema base: `name`, `description`, `metadata`, `tags`
- Implementa lookups: by-key, by-tag, by-metadata-query
- Permite override en subclases sin duplicar lógica

**Deliverables:**
```python
# kernel/catastro_base.py
class CatastroBase(Generic[T]):
    """Base para todos los catastros (models, suppliers, tools)"""
    entries: Dict[str, T]
    
    def lookup(self, key: str) -> T | None: ...
    def search(self, tags: List[str]) -> List[T]: ...
    def validate(self) -> List[ValidationError]: ...

class CatastroModels(CatastroBase[ModelEntry]): ...
class CatastroSuppliers(CatastroBase[SupplierEntry]): ...
class CatastroTools(CatastroBase[ToolEntry]): ...
```

**Métricas:**
- Lines of code: 250-300 total (50 base, 80 per subclass)
- Test coverage: >90%
- Zero regressions in model lookups

---

### Tarea 2: Implementar Catastro Suppliers Humanos

**Descripción:**
Catastro de **personas + agentes que trabajan en El Monstruo**, con entries para:
1. Alfredo González (PM, Cowork, Arquitecto)
2. Manus (Agente, task executor, sprint closer)
3. Embrión (Agente, background loop, autonomous planning)
4. Future: contrataciones (Senior Engineer, Data Analyst, etc.)

**Entry Schema:**
```python
@dataclass
class SupplierEntry:
    key: str  # "alfredo", "manus", "embrion"
    name: str
    role: str  # "PM", "Agent", "Engineer"
    availability: str  # "Always", "Business hours", "Scheduled"
    skills: List[str]  # ["architecture", "coding", "testing"]
    contact: Dict[str, str]  # {"email": "...", "slack": "..."}
    active: bool
    last_active: datetime
```

**Deliverables:**
- File: `kernel/data/catastro_suppliers.json`
- Entries: 3 initial (Alfredo, Manus, Embrión)
- Lookup integration: kernel.py startup loads all 3 catastros
- CLI: `monstruo catastro suppliers list` command

**Métricas:**
- Lookup latency: < 1ms
- Availability accuracy: 99% (manual updates)
- Integration: zero breaking changes to existing code

---

### Tarea 3: Implementar Catastro Tools AI Especializadas

**Descripción:**
Catastro de **herramientas AI externas** que El Monstruo puede orquestar:
- Research: Perplexity, Tavily, DuckDuckGo
- Code search: GitHub, Stack Overflow API
- Data: OpenWeather, NewsAPI, Financial APIs
- Media: DALL-E, Runway, ElevenLabs
- Custom: Cualquier API con OpenAPI spec

**Entry Schema:**
```python
@dataclass
class ToolEntry:
    key: str  # "perplexity", "tavily", "dalle3"
    name: str
    category: str  # "research", "code", "media", "data"
    endpoint: str
    auth_type: str  # "api_key", "oauth", "none"
    rate_limit: str  # "10/min", "100/day", "unlimited"
    cost_per_call: float | None
    active: bool
    fallback_tools: List[str]  # e.g. perplexity → tavily → duckduckgo
```

**Deliverables:**
- File: `kernel/data/catastro_tools.json`
- Entries: 12-15 tools (research, code, media, data categories)
- Fallback chains: Cada tool tiene 2+ fallbacks automáticos
- Integration: `external_agents.py` consulta catastro antes de dispatch
- Monitoring: Uptimes por tool en `kernel/monitoring/tool_health.py`

**Métricas:**
- Tool availability: 95%+
- Fallback success rate: >80% (tool A down → tool B)
- Cost accuracy: Real cost vs budgeted < 5%

---

### Tarea 4: Integración con Engine + Tests

**Descripción:**
Integrar los 3 catastros en el kernel engine sin breaking changes:
1. Load all 3 en `engine.py` startup
2. Expose via `context.catastros` en todos los nodos
3. Validar integridad al startup (test suite)
4. Monitoring: Track lookup latencies, fallbacks, errors

**Deliverables:**
- Tests: 40+ unit tests (15 base, 8 per catastro, 9 integration)
- Monitoring: Prometheus metrics (lookup_latency, fallback_count)
- Docs: Type hints + docstrings para todas clases
- Backward compat: 100% — no breaking changes a `engine.execute()`

**Métricas:**
- Test pass rate: 100%
- Coverage: >90%
- Startup time increase: < 50ms (for 3 catastros)

---

## Aceptación

**Definición de Listo:**
1. CatastroBase implementada y testeada ✅
2. 3 subclases con datos iniciales ✅
3. Integration tests en engine ✅
4. Zero regressions en execution flow ✅
5. Documentation completa ✅

**Integración post-sprint:**
- Sprint 90 usa Catastro Tools (Stripe lookup)
- Sprint Catastro A puebla Suppliers + Tools (30+ entries)
- Sprint Mobile accede catastros vía API (`GET /v1/catastro/{type}`)

---

## Notas Técnicas

1. **Generic typing:** Python 3.10+ syntax, mypy --strict compatible
2. **JSON schema:** Catastro entries validadas con Pydantic v2
3. **Lazy loading:** Catastros cargados a demanda en engine init, no en import
4. **Caching:** Redis layer opcional (fallback: in-memory dict)

---

**Cowork (Hilo A), spec preparada 2026-05-06**
