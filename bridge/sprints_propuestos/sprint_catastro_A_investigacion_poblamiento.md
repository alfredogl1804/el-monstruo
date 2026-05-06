# Sprint Catastro A — Investigación y Poblamiento: Suppliers Humanos + Herramientas AI (30+ suppliers + 25+ tools)

**Estado:** Propuesto  
**Hilo:** Investigador (Alfredo + Embrión asincrónico)  
**ETA (actualizado):** 30-90 min reales (velocity: realtime curation + validation, no solo copy-paste)  
**Objetivo Maestro:** #1 (Crear valor real) + #4 (No equivocarse dos veces)

---

## Audit Pre-Sprint

**Existing Catastro Suppliers:**
- Count: 1 (Alfredo)
- Target: 6 total (Alfredo, Manus, Embrión + 3 future hires)
- Quality gate: Cada entry requiere validation de availability + contact info

**Existing Catastro Tools:**
- Status: Catastro framework listo (sprint 89)
- Count: 0 (será poblado en este sprint)
- Target: 25+ tools across 5 categories
- Quality gate: Funcionalidad verified, pricing confirmed, fallback chains mapeadas

**Research Velocity:**
- Validation per supplier: 3-5 min (call, email, verify availability)
- Tool research per entry: 5-10 min (test endpoint, check pricing, doc fallback)
- Combined with sprint 89 catastro refactoring: 60-90 min total for both

**Key Risks:**
- Contact info outdated: Mitigate con direct outreach
- Tool pricing changes: Capture snapshot + timestamp, auto-refresh monthly
- Availability windows: Store ranges, not binary flags

---

## Tareas del Sprint

### Tarea 1: Poblamiento Catastro Suppliers Humanos — 6 Entries

**Descripción:**
Completar registro de suppliers humanos con 6 personas clave en El Monstruo.

**Entries a crear:**
```json
{
  "alfredo": {
    "name": "Alfredo González",
    "role": "PM, Architect, Cowork Executor",
    "availability": "Always (Mérida, UTC-5)",
    "skills": ["architecture", "strategy", "code-review", "decision-making"],
    "contact": {
      "email": "hfhm9mycw7@privaterelay.appleid.com",
      "slack": "@alfredo",
      "timezone": "UTC-5"
    },
    "active": true,
    "last_active": "2026-05-06T14:30:00Z"
  },
  "manus": {
    "name": "Manus (El Ejecutor)",
    "role": "Agente Autonomous Task Executor",
    "availability": "On-demand (0-2 min cold start)",
    "skills": ["task-execution", "sprint-closing", "code-generation", "debugging"],
    "contact": {
      "api": "manus.space/api",
      "webhook": "/callback"
    },
    "active": true,
    "last_active": "2026-05-06T15:00:00Z"
  },
  "embrion": {
    "name": "Embrión IA",
    "role": "Agente Autonomous Planning & Learning",
    "availability": "Background loop (2-minute heartbeats)",
    "skills": ["planning", "learning", "strategy", "monitoring"],
    "contact": {
      "api": "kernel/embrion_loop.py"
    },
    "active": true,
    "last_active": "2026-05-06T15:15:00Z"
  },
  "future_engineer_senior": {
    "name": "[PENDING HIRE]",
    "role": "Senior Engineer (Backend)",
    "availability": "[TBD]",
    "skills": ["python", "systems-design", "databases"],
    "contact": {},
    "active": false,
    "last_active": null
  },
  "future_analyst_data": {
    "name": "[PENDING HIRE]",
    "role": "Data Analyst",
    "availability": "[TBD]",
    "skills": ["sql", "analytics", "visualization"],
    "contact": {},
    "active": false,
    "last_active": null
  },
  "future_devops": {
    "name": "[PENDING HIRE]",
    "role": "DevOps / Infrastructure",
    "availability": "[TBD]",
    "skills": ["kubernetes", "terraform", "ci-cd"],
    "contact": {},
    "active": false,
    "last_active": null
  }
}
```

**Validation Checklist:**
- [ ] Contact info verified (email valid, timezone correct)
- [ ] Availability windows confirmed
- [ ] Skills list matches actual track record
- [ ] Last active timestamp current (< 24h old)
- [ ] Future hires: placeholder format consistent

**Deliverables:**
- File: `kernel/data/catastro_suppliers.json`
- Entries: 6 (3 active, 3 placeholders)
- Validation: 100% of active entries verified

**Metrics:**
- Entry completeness: 100% (all required fields)
- Verification rate: 100% active
- Contact accuracy: Manual double-check

---

### Tarea 2: Poblamiento Catastro Tools AI — 25+ Entries (5 Categorías)

**Descripción:**
Investigar, validar y registrar 25+ herramientas AI especializadas en 5 categorías.

**Categorías y scope:**

#### Category 1: Research (5-7 tools)
- Perplexity (sonar-pro) — Web search + reasoning
- Tavily — Document search + summarization
- DuckDuckGo API — Privacy search
- NewsAPI — Real-time news
- ArXiv API — Academic papers
- [Future: Semantic Scholar, PubMed]

#### Category 2: Code & Development (4-6 tools)
- GitHub API — Repo search, issues, PRs
- Stack Overflow API — Q&A search
- GitLab API — Alternative code hosting
- Hugging Face API — ML models
- [Future: Docker Hub, PyPI]

#### Category 3: AI/ML Models (5-8 tools)
- DALL-E 3 — Image generation
- Runway Gen-2 — Video generation
- ElevenLabs — Voice synthesis
- Replicate API — Open source models
- Hugging Face Inference — LLM inference
- [Future: Midjourney API, Synthesia]

#### Category 4: Data & Intelligence (4-5 tools)
- OpenWeather API — Weather + forecasts
- Finnhub API — Financial markets
- Stripe API — Payments (already integrated)
- Supabase API — Database (already using)
- [Future: Bloomberg, IEX Cloud]

#### Category 5: Utility / Multi-purpose (3-5 tools)
- Zapier API — Workflow automation
- Make.com API — Integrations
- SendGrid API — Email
- Twilio API — SMS/Voice
- [Future: Airtable, Notion API]

**Entry template:**
```json
{
  "perplexity": {
    "name": "Perplexity AI",
    "category": "research",
    "endpoint": "https://api.perplexity.ai/chat/completions",
    "auth_type": "api_key",
    "rate_limit": "100 requests/day (free), unlimited (pro)",
    "cost_per_call": 0.005,
    "pricing_model": "Per-token (input/output)",
    "languages": ["english"],
    "fallback_tools": ["tavily", "duckduckgo"],
    "active": true,
    "verified_date": "2026-05-06",
    "last_tested": "2026-05-06T13:00:00Z",
    "notes": "Best for web search + reasoning, includes sources"
  }
}
```

**Validation Checklist per tool:**
- [ ] Endpoint tested (curl/HTTP 200)
- [ ] Auth method verified (API key format, OAuth, etc.)
- [ ] Rate limits documented from official docs
- [ ] Pricing snapshot captured (costs change, record timestamp)
- [ ] Fallback tools checked (if primary down, does fallback work?)
- [ ] Documentation link valid (README, API ref)

**Deliverables:**
- File: `kernel/data/catastro_tools.json`
- Entries: 25+ across 5 categories
- Fallback chains: Every tool has 2-3 fallbacks
- Validation: 100% tested endpoints

**Metrics:**
- Tool coverage: 25+ verified entries
- Category balance: 5-8 tools per category (no single point of failure)
- Fallback success rate: > 80% (if primary fails, fallback works)
- Cost accuracy: ±5% of real pricing

---

### Tarea 3: Integración con Engine + Catastro.lookup()

**Descripción:**
Asegurar que engine.py puede consultar suppliers + tools sin errores.

**Code changes:**
```python
# engine.py startup
from kernel.catastro_base import CatastroModels, CatastroSuppliers, CatastroTools

context.catastros = {
    'models': CatastroModels(load_from_json('kernel/data/catastro_models.json')),
    'suppliers': CatastroSuppliers(load_from_json('kernel/data/catastro_suppliers.json')),
    'tools': CatastroTools(load_from_json('kernel/data/catastro_tools.json')),
}

# Usage en cualquier nodo
supplier = context.catastros['suppliers'].lookup('manus')
tool = context.catastros['tools'].lookup('perplexity')
fallback = context.catastros['tools'].search(tags=['research', 'fallback'])
```

**Tests:**
- Lookup by key: O(1), correct result
- Search by tag: All matching entries returned
- Fallback chains: Resolver falla si fallback no existe
- Startup perf: < 50ms

**Deliverables:**
- Integration complete (zero breaking changes)
- Tests: 10+ test cases (lookup, search, fallbacks, errors)
- Monitoring: Catastro lookup metrics in Prometheus

**Metrics:**
- Lookup latency: < 1ms
- Test pass rate: 100%
- Code coverage: 95%+

---

### Tarea 4: Monitoring + Auto-refresh

**Descripción:**
Setup para monitoreo de tool health + auto-refresh mensual de precios/availability.

**Implementation:**
```python
# kernel/monitoring/catastro_health.py
async def refresh_tool_status():
    """Run monthly to verify tools are still active"""
    for tool in context.catastros['tools'].entries.values():
        response = await http_client.head(tool.endpoint, timeout=5)
        tool.last_tested = now()
        tool.status = 'up' if response.status < 400 else 'down'
        
        if tool.cost_per_call_refresh_date < (now() - 30days):
            # Fetch new pricing from API docs
            tool.cost_per_call = get_updated_pricing(tool.key)
            tool.cost_per_call_refresh_date = now()
```

**Deliverables:**
- Monitoring task: Scheduled monthly
- Alerts: Datadog/PagerDuty if 3+ tools down
- Fallback detection: Auto-switch to fallback if primary unavailable > 1h
- Dashboard: Catastro health status (public in Command Center)

**Metrics:**
- Tool uptime: 95%+
- Fallback activation: < 5 times/month
- Pricing accuracy: Snapshot taken monthly

---

## Aceptación

**Definición de Listo:**
1. catastro_suppliers.json: 6 entries, verified ✅
2. catastro_tools.json: 25+ entries, tested ✅
3. Fallback chains: 100% valid ✅
4. Integration: Zero breaking changes ✅
5. Monitoring: Health check scheduled ✅

**Quality Gates:**
- All tools endpoint-tested
- All suppliers contact-verified
- Zero hardcoded secrets (use env vars)
- Pricing snapshot timestamped

**Post-sprint:**
- Sprint 90 dispatch: Can lookup tools from catastro
- Sprint Mobile: Can display supplier + tool listings
- Embrión: Can consult catastros for task planning

---

## Notas Técnicas

1. **JSON schema:** Pydantic validators para ambos catastros
2. **Secrets:** API keys en .env, NO en JSON files
3. **Caching:** Redis optional (in-memory dict fallback)
4. **Versioning:** catastro_suppliers.json v1.0, catastro_tools.json v1.0

---

**Cowork (Hilo A), spec preparada 2026-05-06**
