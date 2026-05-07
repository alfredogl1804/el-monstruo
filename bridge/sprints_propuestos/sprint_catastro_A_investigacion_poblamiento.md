# Sprint Catastro A — Poblamiento de los 4 Catastros + 3 Interfaces Operativas

**Estado:** Propuesto (v2 — reconfigurado a 4 catastros post-conversación 2026-05-06)
**Hilo:** Investigador (Manus Hilo Catastro)
**ETA:** 75-110 min reales (3 dominios + 3 interfaces operativas + integración)
**Objetivo Maestro:** #1 (Crear valor real) + #4 (No equivocarse dos veces) + #7 (No reinventar la rueda) + #11 (Seguridad adversarial)
**DSCs aplicables:** DSC-G-007.1 (4 catastros canónicos), DSC-S-001/S-003/S-004 (cero secrets en JSON), DSC-V-002 (validación realtime)

---

## 0. Procedencia — Reconfiguración a 4 catastros

**Spec original (v1 2026-05-06):** 3 catastros — Modelos LLM + Suppliers Humanos + Herramientas AI Verticales (DSC-G-007 original).

**Reconfiguración (v2 2026-05-06):** Conversación Cowork ↔ Manus detectó **gap conceptual**: las 21 biblias canónicas en `docs/biblias_agentes_2026/` (Claude Code, Cline, Devin, OpenAI Operator, Manus v3, etc.) son **AGENTES** generalistas — sistemas autónomos completos con loops propios — no son ni Modelos LLM crudos, ni Tools verticales, ni Suppliers humanos.

**Taxonomía firmada (DSC-G-007.1):**

| Catastro | Definición | Ejemplos | Cantidad |
|---|---|---|---|
| **Modelos LLM** | Endpoint LLM crudo + tokens + cost/1k. Sin loop, sin tools nativas, sin orquestación. | GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, Kimi K2.5, DeepSeek R1 | 6 actuales (extender a 50+) |
| **Agentes 2026** (NUEVO) | Sistemas autónomos completos con loops propios, tools nativas, capability orquestada | Claude Code, Cline, Devin, OpenAI Operator, Manus v3, Project Mariner, UI TARS, Hermes, Lindy, Metis, Neo, etc. | 21 (de biblias canónicas) |
| **Herramientas AI Verticales** | Capability específica orquestable, sin loop autónomo | LlamaParse, Runway Gen-4, ElevenLabs, Spline AI, RoomGPT, Modsy, Luma | 16-25 (realtime fresh) |
| **Suppliers Humanos** | Personas que entregan trabajo (servicios profesionales) | Arquitectos, valuadores, fotógrafos, contratistas, abogados Sureste MX | 30+ |

**4 catastros paralelos canónicos.** DSC-G-007 evoluciona a DSC-G-007.1 firmado el 2026-05-06.

---

## 1. Audit pre-sprint

### Estado actual

- **Catastro Modelos LLM:** existe en kernel desde Sprint 89 (6 entries iniciales). Spec 89 lo extiende a 50+.
- **Catastro Agentes 2026:** NO existe. Las 21 biblias están en `docs/biblias_agentes_2026/` como markdown estático, sin estructura consultable.
- **Catastro Herramientas AI Verticales:** NO existe (Sprint 89 lo crea con 12-15 entries iniciales, este sprint lo pobla a 25+).
- **Catastro Suppliers Humanos:** NO existe (Sprint 89 lo crea con 3-6 entries placeholder, este sprint lo pobla a 30+).

### Velocity

- Manus cierra sprints en 15 min para tareas atómicas
- Investigación realtime + validación per entry: 5-10 min
- 75-110 min total cabe con velocity demostrada

### Dependencias

- **Bloqueante:** Sprint 89 cerrado (instala el `CatastroBase` y los 3 sub-catastros vacíos del original)
- **NO bloqueante:** Sprint S-001 (provee pre-commit hooks, pero no bloquea poblamiento de JSON públicos sin secrets)

### ⚠️ Reglas de credenciales aplicables a los 4 catastros (DSC-S-001 + DSC-S-003 + DSC-S-004)

**Los 4 archivos JSON (`catastro_models.json`, `catastro_agentes.json`, `catastro_tools.json`, `catastro_suppliers.json`) viven en repo público SIN credenciales.**

Cada entry contiene SOLO metadata pública: nombre, endpoint, capabilities, scoring, fallbacks, etc. Los secrets (API keys, JWTs, passwords) viven en env vars resueltas en runtime con `os.environ[VAR]` (fail loud).

Helper canónico `kernel/security/credential_resolver.py` (introducido en Sprint 89 v2): resolver de credenciales con fail-loud + validación al startup.

---

## 2. Tareas del sprint

### Tarea A — Catastro de Agentes 2026 (NUEVO, 21 entries)

**Descripción:** Parsear las 21 biblias canónicas de `docs/biblias_agentes_2026/*.md` y poblarlas en `kernel/data/catastro_agentes.json`.

**Las 21 biblias:**

```
BIBLIA_AGENT_S.md           BIBLIA_LAGUNA_XS2.md
BIBLIA_CLAUDE_CODE.md       BIBLIA_LINDY.md
BIBLIA_CLAUDE_COWORK.md     BIBLIA_MANUS_v3_REFERENCIA.md
BIBLIA_CLINE.md             BIBLIA_META_AI_AGENT.md
BIBLIA_DEVIN.md             BIBLIA_METIS.md
BIBLIA_GEMINI_ROBOTICS.md   BIBLIA_NEO.md
BIBLIA_GROK_VOICE.md        BIBLIA_OPENAI_OPERATOR.md
BIBLIA_HERMES_AGENT.md      BIBLIA_PERPLEXITY_COMPUTER.md
BIBLIA_KIMI_K2.6.md         BIBLIA_PERPLEXITY_ENTERPRISE.md
BIBLIA_KIRO.md              BIBLIA_PROJECT_MARINER.md
                            BIBLIA_UI_TARS.md
```

**Schema `AgenteEntry`:**

```python
@dataclass
class AgenteEntry:
    key: str  # "claude_code", "manus_v3", "devin"
    name: str  # "Claude Code", "Manus v3", "Devin"
    proveedor: str  # "Anthropic", "Cognition", "OpenAI", etc.
    biblia_path: str  # "docs/biblias_agentes_2026/BIBLIA_CLAUDE_CODE.md"
    capabilities: List[str]  # ["browser_autonomous", "code_writing", "shell_exec"]
    layer_l12_scores: Dict[str, int]  # {"reasoning": 90, "execution": 85, ...}
    auth_type: str  # "api_key", "oauth", "subscription", "free"
    cost_model: str  # "subscription", "per_token", "per_action", "free_tier"
    pricing_snapshot: Dict[str, Any]  # {"per_token_in": 0.000003, "subscription": "$20/mo"}
    pricing_refresh_date: str  # ISO date
    is_peer_of_manus: bool  # True para Claude Code, Cline, Devin, OpenAI Operator, Manus v3
    can_be_delegated_to: bool  # True para tools-callable como Project Mariner, UI TARS
    fallback_chain: List[str]  # ["alternative_agent_key", ...]
    active: bool
    last_verified: str  # ISO timestamp
    notes: str  # contexto operativo, cuándo usar, cuándo NO usar
```

**Validación per agente (DSC-V-002):**

- [ ] Endpoint / URL del proveedor verificado (HTTP 200 o login page)
- [ ] Pricing actualizado vs biblia (puede haber drift, snapshot fresco)
- [ ] Capabilities derivadas de biblia, validadas contra docs oficiales del proveedor
- [ ] Layer L12 scores extraídos de biblia (o calculados si la biblia no los tiene)

**Distribución esperada:**

- **Peers de Manus** (`is_peer_of_manus=True`): Claude Code, Cline, Devin, OpenAI Operator, Manus v3, Manus Cowork, Hermes, Project Mariner — para auto-aprendizaje
- **Delegables** (`can_be_delegated_to=True`): Project Mariner, UI TARS, Perplexity Computer, Gemini Robotics, Grok Voice, Hermes, Lindy, Metis, Neo, Laguna XS2 — para Manus invocar como tools
- **Referencia general:** Kimi K2.6, Meta AI Agent, Agent S, Kiro

**Deliverables:**
- File: `kernel/data/catastro_agentes.json` con 21 entries
- Tests: 21 unit tests (1 por agente) + integration test con `find_best`
- Documentación: `docs/CATASTRO_AGENTES_2026.md` con tabla de capabilities cross-referenced

---

### Tarea B — Catastro de Herramientas AI Verticales (16-25 entries)

**Descripción:** Investigar realtime y poblar herramientas AI verticales líderes 2026.

**Categorías + ejemplos canónicos:**

| Categoría | Tools (mínimo) | Líderes 2026 |
|---|---|---|
| Renderers 3D / spatial | 3+ | Spline AI, RoomGPT, Modsy, Luma |
| Video gen | 2+ | Runway Gen-4, Sora 2, Veo 3 |
| Voice / audio | 2+ | ElevenLabs, Suno |
| Document parsing | 2+ | LlamaParse, Unstructured.io, Reducto |
| Code gen vertical | 2+ | Cursor, Codeium, Cody |
| Image gen | 2+ | Midjourney, Flux, Ideogram |
| Data extraction | 1+ | Apify, Browse AI |
| Search / retrieval | 1+ | Exa, Tavily |

**Total objetivo:** 16-25 entries verticales (cobertura ancha sobre profundidad en una vertical).

**Schema `ToolEntry`** (de Sprint 89 v2 con sección "Reglas de credenciales" agregada — referencia al spec actualizado).

**Validación per tool (DSC-V-002 estricto):**

- [ ] Endpoint testeado (curl/HTTP 200 o login page)
- [ ] Auth method verificado (api_key / oauth / none)
- [ ] Rate limits documentados de docs oficiales
- [ ] Pricing snapshot timestamped
- [ ] Fallback tools verificados (si primary down → fallback tool funciona)
- [ ] Documentation link valid

**Deliverables:**
- File: `kernel/data/catastro_tools.json` con 16-25 entries
- Fallback chains: cada tool tiene 2-3 fallbacks
- Validation: 100% endpoints tested

---

### Tarea C — Catastro de Suppliers Humanos Sureste MX (30+ entries)

**Descripción:** Investigar realtime y poblar suppliers profesionales del Sureste de México (Mérida, Cancún, Campeche, Chetumal).

**Categorías:**

| Tipo | Mínimo | Fuente realtime |
|---|---|---|
| Arquitectos | 5+ | CIDEY (Colegio Ingenieros y Arquitectos Yucatán), LinkedIn local, redes profesionales |
| Valuadores certificados | 3+ | CONOCER, IMCRA Sureste, peritos valuadores SHCP |
| Fotógrafos profesionales | 5+ | Instagram, comunidades fotográficas Mérida |
| Contratistas / constructores | 5+ | CMICY (Cámara Mexicana de la Industria de la Construcción Yucatán) |
| Abogados / notarios | 5+ | BarMéx, Colegio Notarios Yucatán |
| Diseñadores de interiores | 3+ | Asociación Mexicana de Diseñadores de Interiores |
| Peritos topógrafos | 2+ | Colegio de Topógrafos Yucatán |
| Otros (electricistas, plomeros, gestores) | 5+ | Comunidades locales validadas |

**Schema `SupplierEntry`:**

```python
@dataclass
class SupplierEntry:
    key: str  # "arq_juan_perez_2026"
    name: str
    role: str  # "Arquitecto", "Valuador", etc.
    speciality: str  # "Residencial Sureste MX"
    region: str  # "MX-YUC", "MX-QR", "MX-CAM" — schema permite expansión a "MX-CDMX", "US-TX" en v1.x+
    contact_method: str  # "phone", "email", "whatsapp" — solo el MÉTODO, NO el dato
    contact_env_var: str  # "SUPPLIER_ARQ_JUAN_PEREZ_PHONE" — el dato real en env var
    certifications: List[str]  # ["DRO 2025", "Cédula 12345"]
    rating: float  # 0-5 en proyectos previos
    availability: str  # "Always", "Business hours", "Scheduled"
    rate_card: Dict[str, str]  # rangos públicos, valores específicos en env var si privados
    fallback_suppliers: List[str]
    active: bool
    last_verified: str
```

**⚠️ Sub-regla de credenciales para Suppliers (DSC-S-001):**

Datos de contacto sensibles (teléfonos personales, emails privados, tarifas confidenciales) NO van en el JSON. Solo el `contact_method` (qué canal usar) + `contact_env_var` (referencia a env var). Los datos reales viven en 1Password de Alfredo + env vars del proceso runtime.

**Validación per supplier:**

- [ ] Contacto verificado (llamada o email confirmando data)
- [ ] Disponibilidad confirmada
- [ ] Skills/certifications cross-referenced con cédula profesional / colegio
- [ ] Rating basado en proyectos previos verificables (no testimonial inventado)
- [ ] Última actividad < 30 días

**Deliverables:**
- File: `kernel/data/catastro_suppliers.json` con 30+ entries
- 1Password vault: Suppliers contact data privada con referencias a env vars
- Validation: 100% suppliers contact-verified

---

### Tarea D — 3 Interfaces operativas para Manus (consume el Catastro de Agentes)

**Descripción:** El Catastro de Agentes 2026 NO es tabla informativa — es **manual operativo** que Manus consume para 3 use cases distintos.

**Interface 1 — Catálogo de Delegación**

```python
# kernel/catastros/agentes.py
class CatastroAgentes(CatastroBase[AgenteEntry]):
    def find_best(
        self,
        task: Task,
        capability: str,
        budget: float | None = None,
        latency_max: int | None = None,
    ) -> AgenteEntry:
        """Find best agent to delegate task to.

        Filters by:
        - capability match
        - can_be_delegated_to=True
        - cost_per_action <= budget (if specified)
        - typical_latency <= latency_max (if specified)

        Returns highest-scoring match. Falls through fallback_chain if primary down.
        """
        candidates = [
            a for a in self.entries.values()
            if a.can_be_delegated_to
            and capability in a.capabilities
            and a.active
        ]
        if budget:
            candidates = [a for a in candidates if a.estimated_cost(task) <= budget]
        if latency_max:
            candidates = [a for a in candidates if a.typical_latency_ms <= latency_max]

        if not candidates:
            raise NoSuitableAgenteError(
                f"No agent matches: {capability}, budget={budget}, latency={latency_max}"
            )

        return max(candidates, key=lambda a: a.layer_l12_scores.get("execution", 0))

    def fallback_chain(self, agente_key: str) -> List[AgenteEntry]:
        """Get fallback chain for a primary agent."""
        primary = self.lookup(agente_key)
        return [self.lookup(k) for k in primary.fallback_chain if self.lookup(k).active]
```

**Caso de uso:** Manus tiene tarea de browser autónomo. Hoy hardcoded `dispatch_to("playwright_local")`. Con catastro:
```python
agente = catastro.agentes.find_best(
    task=current_task,
    capability="browser_autonomous",
    budget=current_task.budget,
    latency_max=current_task.deadline_ms
)
# → returns Project Mariner ($0.02/task, 8s avg) o UI TARS si Mariner down
result = await agente.dispatch(current_task)
```

**Interface 2 — Espejo Peer (auto-aprendizaje)**

```python
def peers_of(self, agente_key: str) -> List[AgenteEntry]:
    """Get peer agents (mirrors) for self-learning.

    Returns agents with is_peer_of_manus=True (excluyendo el query mismo).
    """
    return [
        a for a in self.entries.values()
        if a.is_peer_of_manus and a.key != agente_key and a.active
    ]

def diff_capabilities(self, agente_a: str, agente_b: str) -> Dict[str, List[str]]:
    """Compare capabilities between two agents.

    Returns:
        {
            "only_in_a": [capabilities only in agent A],
            "only_in_b": [capabilities only in agent B],
            "shared": [capabilities in both],
        }
    """
    a = self.lookup(agente_a)
    b = self.lookup(agente_b)
    set_a = set(a.capabilities)
    set_b = set(b.capabilities)
    return {
        "only_in_a": list(set_a - set_b),
        "only_in_b": list(set_b - set_a),
        "shared": list(set_a & set_b),
    }
```

**Caso de uso:** Manus en loop semanal de auto-mejora:
```python
peers = catastro.agentes.peers_of("manus_v3")
# → [claude_code, cline, devin, openai_operator, project_mariner]

for peer in peers:
    diff = catastro.agentes.diff_capabilities("manus_v3", peer.key)
    if diff["only_in_b"]:  # peer tiene capabilities que Manus no
        propose_capability_adoption(peer.key, diff["only_in_b"])
```

**Interface 3 — Self-reference (anti-Dory aplicado a Manus)**

```python
def my_canonical_spec(self) -> AgenteEntry:
    """Return Manus' own canonical spec (BIBLIA_MANUS_v3_REFERENCIA.md).

    Used for pre-flight checks before irreversible decisions.
    """
    return self.lookup("manus_v3")

def validate_against_spec(self, recent_decisions: List[Decision]) -> ValidationResult:
    """Check recent decisions against Manus' canonical spec.

    Used in Capa Memento (anti-Falso-Positivo-TiDB) before:
    - SQL prod operations
    - Credential rotation
    - Production deploys
    - Financial transactions

    Returns ValidationResult(is_consistent: bool, violations: List[str], context_drift_score: float).
    """
    spec = self.my_canonical_spec()
    violations = []
    for decision in recent_decisions:
        if not decision.matches_capability(spec.capabilities):
            violations.append(
                f"Decision {decision.id} uses capability not in spec: {decision.capability}"
            )
        if decision.violates_guardrail(spec.guardrails):
            violations.append(
                f"Decision {decision.id} violates guardrail: {decision.guardrail_violated}"
            )

    drift_score = compute_context_drift(recent_decisions, spec)

    return ValidationResult(
        is_consistent=len(violations) == 0,
        violations=violations,
        context_drift_score=drift_score,
    )
```

**Caso de uso:** Antes de operación crítica, Manus auto-valida:
```python
@requires_memento_preflight(operation="rotate_db_credentials")
async def rotate_credentials():
    # Decorator internamente:
    # - validation = catastro.agentes.validate_against_spec(recent_decisions)
    # - if not validation.is_consistent: raise PreflightError(validation.violations)
    # - if validation.context_drift_score > 0.7: raise ContextContaminatedError()

    # Solo si pre-flight verde, procede:
    await execute_rotation()
```

**Deliverables:**
- File: `kernel/catastros/agentes.py` con `CatastroAgentes` class + 3 interfaces
- Tests: unit tests para `find_best`, `peers_of`, `diff_capabilities`, `my_canonical_spec`, `validate_against_spec`
- Documentación: `docs/CATASTRO_AGENTES_INTERFACES.md` con casos de uso

---

### Tarea E — Integración con engine + tests E2E

**Descripción:** Conectar los 4 catastros (Modelos + Agentes + Tools + Suppliers) en `kernel/engine.py` startup + validar que las interfaces operativas funcionan.

**Implementación:**

```python
# kernel/engine.py startup
from kernel.catastros import (
    CatastroModelos, CatastroAgentes, CatastroTools, CatastroSuppliers
)
from kernel.security.env_validator import validate_env_at_startup

def init_catastros(context: KernelContext) -> None:
    validate_env_at_startup()  # DSC-S-003 — fail loud si env vars críticas faltan

    context.catastros = {
        'models': CatastroModelos(load_from_json('kernel/data/catastro_models.json')),
        'agentes': CatastroAgentes(load_from_json('kernel/data/catastro_agentes.json')),
        'tools': CatastroTools(load_from_json('kernel/data/catastro_tools.json')),
        'suppliers': CatastroSuppliers(load_from_json('kernel/data/catastro_suppliers.json')),
    }

    # Validación cruzada: fallback chains apuntan a entries existentes
    for catastro in context.catastros.values():
        catastro.validate_fallback_chains()
```

**Tests E2E:**
- `test_4_catastros_load_at_startup` — 4 catastros cargan sin error
- `test_find_best_agente_for_browser_autonomous` — devuelve Project Mariner
- `test_peers_of_manus_v3` — devuelve 5+ peers
- `test_validate_against_spec_clean_decisions` — passes
- `test_validate_against_spec_contaminated_decisions` — flagea violations

**Deliverables:**
- Integration tests pasando 100%
- Monitoring: Prometheus metrics (catastro_lookup_latency, catastro_fallback_count)

---

## 3. Aceptación

**Definición de Listo (las 5 tareas verde simultáneo):**

1. ✅ Catastro Agentes 2026 poblado con 21 entries (Tarea A)
2. ✅ Catastro Tools poblado con 16-25 entries (Tarea B)
3. ✅ Catastro Suppliers poblado con 30+ entries (Tarea C)
4. ✅ 3 interfaces operativas implementadas + tested (Tarea D)
5. ✅ Integración engine + tests E2E pasando (Tarea E)

**Quality gates:**
- Cero secrets en cualquiera de los 4 JSON públicos (audit con gitleaks pre-commit)
- 100% endpoints tested (DSC-V-002)
- Helper `credential_resolver.py` operando con fail-loud
- Schema con campo `region` en suppliers (permite expansión sin migración)

**Cierre formal:**

🏛️ **CATASTROS PARALELOS x4 — DECLARADOS**

+ Tabla de evidencia 5 filas (1 por catastro + 1 por integración)
+ DSC-G-007.1 referenciado como base canónica
+ Reporte al bridge con métricas de poblamiento

---

## 4. Notas técnicas

1. **Refresh periódico:** cada 30 días, cron del Embrión re-valida tools/suppliers (endpoints + pricing + availability). Si > 3 entries down simultáneo → alerta a Cowork.

2. **Suppliers privados (datos en 1Password):** los datos sensibles de contacto NO se commitean. Schema tiene `contact_env_var` que apunta a env var, dato real en bóveda primaria.

3. **Agentes peers vs delegables:** un agente puede ser ambos (`is_peer_of_manus=True` AND `can_be_delegated_to=True` para algunos como Project Mariner — peer en patrón, delegable en ejecución).

4. **Capa Memento integration:** la interface 3 (`validate_against_spec`) es base técnica de la Capa Memento mencionada en CLAUDE.md. Sin esta interface, el decorator `@requires_memento_preflight` no funciona.

---

## 5. Referencias cruzadas

- DSC-G-007.1 — 4 catastros canónicos (firmado 2026-05-06 con esta sesión)
- DSC-S-001 + S-003 + S-004 — cero secrets en JSON, env vars con fail loud
- DSC-V-002 — validación realtime obligatoria
- DSC-X-006 — convergencia diferida (los 4 catastros arrancan autónomos, convergen vía interfaces)
- `bridge/cowork_to_manus_AUDIT_PREVENTIVO_SPECS_2026_05_06.md` — Issue D que detonó este v2

---

**Cowork (Hilo A), spec v2 redactada 2026-05-06 post-conversación gap conceptual + audit preventivo**
**Reemplaza versión v1 (3 catastros) — backwards-incompatible firmado**
