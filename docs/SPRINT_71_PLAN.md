# SPRINT 71 — "El Primer Hijo Nace con Propósito"

**Serie:** 71-80 "La Colmena Despierta"
**Fecha de diseño:** 1 de Mayo de 2026 (v2 — Arquitectura Pensador/Ejecutor)
**Arquitecto:** Hilo B
**Capa Arquitectónica:** CAPA 2 (Inteligencia Emergente)
**Objetivo Primario:** #2 (Apple/Tesla), #8 (Emergencia), #9 (Transversalidad)

---

## Contexto

El Embrión-0 existe. Tiene heartbeat, FCS, debate interno, y capacidad de orquestación. Pero está solo. La Colmena (Objetivo #6) requiere múltiples Embriones especializados que debaten entre sí y generan inteligencia emergente.

Sprint 71 marca el nacimiento del **primer Embrión con propósito específico**: el Brand Engine. No es un clon del Embrión-0 — es una entidad distinta con un dominio de expertise propio, métricas propias, y un rol claro en el ecosistema.

**¿Por qué Brand Engine primero?** Porque es el quality gate que validará a todos los Embriones futuros. Sin él, los Embriones 2-8 producirían outputs genéricos. El Brand Engine es el estándar contra el cual todo se mide.

---

## DECISIÓN ARQUITECTÓNICA FUNDAMENTAL: Pensador + Ejecutor

### El Problema

La emergencia es un estado frágil. Cuando un Embrión "piensa" (razona, conecta, decide) necesita un context window limpio y un modelo potente. Cuando "ejecuta" (persiste en DB, formatea JSON, llama APIs) contamina ese contexto con operaciones mecánicas. Las tareas pesadas le quitan lo emergido.

### La Solución

**Cada Embrión es un PAR: Pensador + Ejecutor.**

| Componente | Naturaleza | Función | Context Window |
|---|---|---|---|
| **Pensador** | LLM potente (GPT-4o / el más potente disponible) | Razona, conecta, decide, emerge, debate | LIMPIO — solo ideas, estrategia, y contexto de dominio |
| **Ejecutor** | Código Python determinista (SIN LLM) | Persiste, formatea, llama APIs, ejecuta heartbeat | No aplica — es código, no modelo |

### Principios del Patrón

1. **El Pensador NUNCA ejecuta operaciones mecánicas** — No escribe a DB, no formatea JSON, no llama APIs externas. Solo piensa.
2. **El Ejecutor NUNCA toma decisiones** — No evalúa calidad, no decide si algo pasa o no. Solo ejecuta instrucciones del Pensador.
3. **La comunicación es un contrato** — El Pensador emite un `BrandDecision` (dataclass), el Ejecutor lo materializa.
4. **El Pensador se activa SOLO cuando hay juicio involucrado** — Si la tarea es determinista (regex, format, persist), el Ejecutor la hace solo.
5. **El context window del Pensador se preserva** — Nunca se contamina con logs operativos, responses de APIs, o datos de persistencia.

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMBRIÓN-1: BRAND ENGINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    PENSADOR (LLM Potente)                    ││
│  │                                                               ││
│  │  • evaluate_aesthetic_quality(output) → BrandDecision        ││
│  │  • generate_brand_for_business(type, market) → BrandDNA     ││
│  │  • debate_with_embrion(topic, proposal) → CounterProposal   ││
│  │  • detect_brand_drift(history) → DriftAnalysis              ││
│  │  • suggest_improvement(output, issues) → ImprovedVersion    ││
│  │                                                               ││
│  │  Context: Brand DNA + últimas 10 decisiones + estado Colmena ││
│  │  Modelo: El más potente disponible (GPT-4o / GPT-5.2)       ││
│  │  Se activa: SOLO cuando hay juicio subjetivo involucrado     ││
│  └─────────────────────────────────────────────────────────────┘│
│                          │                                        │
│                          │ BrandDecision                          │
│                          ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   EJECUTOR (Código Determinista)              ││
│  │                                                               ││
│  │  • validate_naming(name) → bool (regex, rules)              ││
│  │  • validate_error_format(error) → bool (pattern matching)   ││
│  │  • validate_api_response(resp) → bool (schema validation)   ││
│  │  • persist_validation(result) → None (Supabase write)       ││
│  │  • persist_heartbeat(beat) → None (Supabase write)          ││
│  │  • format_response(decision) → dict (JSON formatting)       ││
│  │  • execute_heartbeat() → BrandHeartbeat (metrics calc)      ││
│  │  • check_repeated_violation(source) → EscalationLevel       ││
│  │                                                               ││
│  │  Naturaleza: Python puro. Cero LLM. Predecible. Testeable.  ││
│  │  Costo: $0 por ejecución (solo compute)                     ││
│  │  Se activa: SIEMPRE que hay operación mecánica              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    BRAND DNA (Inmutable)                      ││
│  │                                                               ││
│  │  Misión, Visión, Arquetipo, Personalidad, Tono, Estética,   ││
│  │  Naming, Anti-patrones, Diferenciadores                      ││
│  │  → Compartido entre Pensador y Ejecutor                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              INTER-EMBRIÓN PROTOCOL                           ││
│  │                                                               ││
│  │  • Recibe outputs de otros Embriones para validación         ││
│  │  • Ejecutor hace pre-filtro determinista (naming, format)    ││
│  │  • Si pre-filtro falla → veto inmediato (sin LLM)           ││
│  │  • Si pre-filtro pasa pero hay ambigüedad → Pensador evalúa ││
│  │  • Puede VETAR outputs que no pasen threshold (< 60)         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Decisión

```
Output llega para validación
        │
        ▼
┌─────────────────────┐
│ EJECUTOR: Pre-filtro │  ← Determinista, instantáneo, $0
│ (naming, format,     │
│  schema, patterns)   │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
  FALLA       PASA
    │           │
    ▼           ▼
  VETO    ┌────────────────┐
 (score   │ ¿Hay ambigüedad │
  < 60)   │  o juicio       │
          │  subjetivo?     │
          └───┬────────┬───┘
              │        │
             SÍ       NO
              │        │
              ▼        ▼
     ┌──────────┐   APROBADO
     │ PENSADOR │   (score 100)
     │ evalúa   │
     │ calidad  │
     │ estética │
     └────┬─────┘
          │
          ▼
    BrandDecision
    (score, issues,
     suggestion)
          │
          ▼
     ┌──────────┐
     │ EJECUTOR │
     │ persiste │
     │ formatea │
     │ responde │
     └──────────┘
```

---

## Épica 71.1 — Brand DNA como Módulo del Kernel

**Objetivo:** Codificar la identidad de marca de El Monstruo como un módulo Python inmutable que tanto el Pensador como el Ejecutor consultan.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/brand_dna.py` existe y es importable
- [ ] Contiene TODA la identidad: misión, visión, arquetipo, personalidad, tono, estética, naming, anti-patrones
- [ ] Multi-idioma: español + inglés (Obj #13)
- [ ] Tiene funciones de consulta deterministas
- [ ] Tests unitarios pasan
- [ ] Deployado en Railway

```python
"""
kernel/brand/brand_dna.py
EL MONSTRUO — Brand DNA Module (Inmutable)

Este módulo define la identidad de marca del Monstruo.
Es la fuente de verdad única. No se modifica sin aprobación del Guardián.
Compartido entre Pensador (para contexto) y Ejecutor (para reglas).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class BrandArchetype(Enum):
    CREATOR = "creator"
    MAGE = "mage"
    CREATOR_MAGE = "creator_mage"


class BrandPersonality(Enum):
    IMPLACABLE = "implacable"
    PRECISO = "preciso"
    SOBERANO = "soberano"
    MAGNANIMO = "magnánimo"


class Language(Enum):
    ES = "es"
    EN = "en"


@dataclass(frozen=True)
class ToneOfVoice:
    """Tono de voz inmutable — multi-idioma."""
    do: Dict[str, Tuple[str, ...]] = field(default_factory=lambda: {
        "es": (
            "directo_sin_rodeos",
            "tecnicamente_preciso",
            "confiado_sin_arrogancia",
            "metaforas_industriales",
            "conciso_pero_completo"
        ),
        "en": (
            "direct_no_fluff",
            "technically_precise",
            "confident_not_arrogant",
            "industrial_metaphors",
            "concise_but_complete"
        )
    })
    dont: Dict[str, Tuple[str, ...]] = field(default_factory=lambda: {
        "es": (
            "corporativo", "pedante", "arrogante",
            "generico", "servil", "excesivamente_amigable"
        ),
        "en": (
            "corporate", "pedantic", "arrogant",
            "generic", "servile", "overly_friendly"
        )
    })
    metaphor_domain: Tuple[str, ...] = (
        "forja", "fundir", "templar", "fragua",
        "ensamblaje", "calibrar", "presión",
        "colmena", "latido", "despertar",
        "forge", "smelt", "temper", "anvil",
        "assembly", "calibrate", "pressure",
        "hive", "heartbeat", "awaken"
    )


@dataclass(frozen=True)
class VisualIdentity:
    """Identidad visual inmutable."""
    primary_color: str = "#F97316"       # Naranja forja
    background_dark: str = "#1C1917"     # Graphite
    background_mid: str = "#292524"      # Stone-800
    accent_steel: str = "#A8A29E"        # Acero
    accent_ember: str = "#EA580C"        # Brasa
    success_color: str = "#22C55E"       # Verde operativo
    warning_color: str = "#EAB308"       # Amarillo alerta
    danger_color: str = "#EF4444"        # Rojo crítico
    
    font_display: str = "Bebas Neue"
    font_body: str = "Inter"
    font_mono: str = "JetBrains Mono"
    
    design_philosophy: str = "brutalismo_industrial_refinado"
    motifs: Tuple[str, ...] = ("manómetros", "gauges", "líneas_ensamblaje", "chispas", "metal_fundido")


@dataclass(frozen=True)
class NamingConvention:
    """Convenciones de naming inmutables."""
    module_names: Dict[str, str] = field(default_factory=lambda: {
        "forja": "Dashboard principal / Producción",
        "guardian": "Compliance y 14 Objetivos",
        "colmena": "Embriones y debate",
        "simulador": "Predicciones causales",
        "arsenal": "Herramientas adoptadas",
        "soberania": "Independencia y dependencias",
        "finops": "Costos y ROI",
        "magna": "Documentación premium",
        "vanguard": "Scanner de herramientas",
        "brand": "Brand Engine"
    })
    endpoint_format: str = "/api/v1/{module}/{action}"
    error_format: str = "{module}_{action}_{failure_type}"
    forbidden_names: Tuple[str, ...] = (
        "service", "handler", "utils", "helper", "misc",
        "stuff", "thing", "data", "info", "manager",
        "processor", "worker", "job", "task"
    )


@dataclass(frozen=True)
class BrandDNA:
    """La identidad completa e inmutable de El Monstruo."""
    
    mission: Dict[str, str] = field(default_factory=lambda: {
        "es": "Crear el primer agente de IA soberano del mundo que genera negocios exitosos de forma autónoma",
        "en": "Create the world's first sovereign AI agent that autonomously generates successful businesses"
    })
    vision: Dict[str, str] = field(default_factory=lambda: {
        "es": "Un ecosistema de Monstruos interconectados que democratiza la creación de empresas",
        "en": "An ecosystem of interconnected Monstruos that democratizes business creation"
    })
    
    archetype: BrandArchetype = BrandArchetype.CREATOR_MAGE
    personality: Tuple = (
        BrandPersonality.IMPLACABLE,
        BrandPersonality.PRECISO,
        BrandPersonality.SOBERANO,
        BrandPersonality.MAGNANIMO
    )
    
    tone: ToneOfVoice = field(default_factory=ToneOfVoice)
    visual: VisualIdentity = field(default_factory=VisualIdentity)
    naming: NamingConvention = field(default_factory=NamingConvention)
    
    anti_patterns: Tuple[str, ...] = (
        "chatbot_amigable",
        "asistente_servil",
        "herramienta_generica",
        "dashboard_grafana_clone",
        "wrapper_apis_sin_identidad",
        "output_sin_contexto",
        "error_message_generico",
        "friendly_chatbot",
        "servile_assistant",
        "generic_tool"
    )
    
    differentiators: Tuple[str, ...] = (
        "primer_agente_soberano_del_mundo",
        "inteligencia_emergente_no_programada",
        "7_capas_transversales_desde_dia_1",
        "colmena_de_embriones_especializados",
        "brand_engine_integrado_en_kernel",
        "arquitectura_pensador_ejecutor"
    )


# Singleton inmutable
EL_MONSTRUO_DNA = BrandDNA()


def get_brand_dna() -> BrandDNA:
    """Retorna el Brand DNA inmutable de El Monstruo."""
    return EL_MONSTRUO_DNA


def is_forbidden_name(name: str) -> bool:
    """Verifica si un nombre viola las convenciones de marca."""
    return any(
        forbidden in name.lower() 
        for forbidden in EL_MONSTRUO_DNA.naming.forbidden_names
    )


def get_module_names() -> Dict[str, str]:
    """Retorna los módulos válidos del sistema."""
    return dict(EL_MONSTRUO_DNA.naming.module_names)
```

---

## Épica 71.2 — Ejecutor: Brand Validator Determinista

**Objetivo:** Crear el Ejecutor del Embrión-1 — código Python puro que valida outputs contra reglas deterministas. SIN LLM. Predecible, testeable, costo $0.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/executor.py` existe
- [ ] Evalúa: naming, error format, API response schema, timestamp format
- [ ] Score 0-100 basado en reglas deterministas
- [ ] Detección de violaciones repetidas con escalación (Obj #4)
- [ ] Cero dependencias de LLM
- [ ] 100% testeable con pytest
- [ ] Latencia < 5ms por validación

```python
"""
kernel/brand/executor.py
EMBRIÓN-1 EJECUTOR — Código Determinista

Este módulo es el EJECUTOR del Embrión-1 (Brand Engine).
NO usa LLM. Es Python puro. Predecible. Testeable. Costo $0.

Responsabilidades:
- Validación determinista (regex, patterns, schema)
- Persistencia en Supabase
- Formateo de responses
- Cálculo de métricas
- Detección de violaciones repetidas
- Ejecución de heartbeat

NUNCA toma decisiones subjetivas. Si hay ambigüedad → escala al Pensador.
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .brand_dna import get_brand_dna, is_forbidden_name, BrandDNA


class Decision(Enum):
    APPROVE = "approve"
    WARN = "warn"
    VETO = "veto"
    ESCALATE_TO_THINKER = "escalate"  # Necesita juicio subjetivo


class EscalationLevel(Enum):
    FIRST_OFFENSE = "first_offense"      # Solo warn
    REPEAT_OFFENSE = "repeat_offense"    # Warn + log
    CHRONIC_OFFENSE = "chronic_offense"  # Veto automático


@dataclass
class ValidationResult:
    """Resultado de una validación determinista."""
    score: int                          # 0-100
    decision: Decision                  # approve | warn | veto | escalate
    issues: List[Dict[str, str]]        # [{type, description, suggestion}]
    category: str                       # naming | error | structure | format
    input_analyzed: str                 # Lo que se evaluó (truncado a 200 chars)
    requires_thinker: bool = False      # Si necesita evaluación subjetiva
    escalation: Optional[EscalationLevel] = None


@dataclass
class BrandHeartbeat:
    """Estado vital del Embrión-1 — calculado por el Ejecutor."""
    timestamp: str
    brand_health_score: int
    validations_total: int
    validations_last_hour: int
    vetoes_last_hour: int
    approvals_last_hour: int
    escalations_last_hour: int
    drift_detected: bool
    status: str  # "forging" | "vigilant" | "alarmed" | "critical"


class BrandExecutor:
    """
    Ejecutor del Embrión-1: Brand Engine.
    
    Código Python puro. Sin LLM. Sin ambigüedad.
    Cada método es determinista y testeable.
    """
    
    VETO_THRESHOLD = 60
    WARNING_THRESHOLD = 75
    
    def __init__(self, supabase_client=None):
        self.dna: BrandDNA = get_brand_dna()
        self.supabase = supabase_client
        self._validation_history: List[ValidationResult] = []
        self._violation_tracker: Dict[str, Dict[str, int]] = {}  # {source: {issue_type: count}}
    
    # ─── VALIDACIONES DETERMINISTAS ─────────────────────────────────────
    
    def validate_naming(self, name: str) -> ValidationResult:
        """Valida un nombre (endpoint, módulo, variable) contra reglas de marca."""
        score = 100
        issues = []
        
        # Regla 1: Nombres prohibidos
        for forbidden in self.dna.naming.forbidden_names:
            if forbidden in name.lower():
                score -= 25
                issues.append({
                    "type": "forbidden_name",
                    "description": f"Nombre prohibido: '{forbidden}'",
                    "suggestion": f"Usar nombre de dominio: {list(self.dna.naming.module_names.keys())}"
                })
        
        # Regla 2: camelCase → snake_case
        if re.search(r'[a-z][A-Z]', name) and '/api/' not in name:
            score -= 10
            issues.append({
                "type": "naming_style",
                "description": "camelCase detectado — El Monstruo usa snake_case",
                "suggestion": "getData → get_data, processItems → process_items"
            })
        
        # Regla 3: Patrones genéricos
        generic_patterns = ['get_all', 'do_thing', 'process_data', 'handle_request',
                           'run_job', 'execute_task', 'fetch_info']
        for pattern in generic_patterns:
            if pattern in name.lower():
                score -= 15
                issues.append({
                    "type": "generic_naming",
                    "description": f"Patrón genérico: '{pattern}'",
                    "suggestion": "Usar dominio: get_all → list_embriones, process_data → forge_prediction"
                })
        
        # Regla 4: Formato de endpoint
        if name.startswith('/api/'):
            if not re.match(r'/api/v\d+/[a-z_]+/[a-z_]+', name):
                score -= 15
                issues.append({
                    "type": "endpoint_format",
                    "description": "Endpoint no sigue /api/v{n}/{module}/{action}",
                    "suggestion": f"Formato: /api/v1/brand/validate, /api/v1/colmena/heartbeat"
                })
            # Verificar que el módulo es válido
            parts = name.split('/')
            if len(parts) >= 4:
                module = parts[3]
                if module not in self.dna.naming.module_names:
                    score -= 10
                    issues.append({
                        "type": "unknown_module",
                        "description": f"Módulo '{module}' no reconocido",
                        "suggestion": f"Módulos válidos: {list(self.dna.naming.module_names.keys())}"
                    })
        
        score = max(0, score)
        return ValidationResult(
            score=score,
            decision=self._score_to_decision(score),
            issues=issues,
            category="naming",
            input_analyzed=name[:200]
        )
    
    def validate_error_message(self, error: str) -> ValidationResult:
        """Valida que un error message cumpla con el formato de marca."""
        score = 100
        issues = []
        
        # Regla 1: Errores genéricos prohibidos
        generic_errors = [
            "internal server error", "something went wrong",
            "unknown error", "an error occurred", "error",
            "bad request", "not found", "unauthorized",
            "failed", "exception", "unexpected error"
        ]
        if error.lower().strip() in generic_errors:
            score -= 40
            issues.append({
                "type": "generic_error",
                "description": f"Error genérico prohibido: '{error}'",
                "suggestion": "Formato: {module}_{action}_{type}: {descripción con contexto}"
            })
        
        # Regla 2: Debe tener estructura (contener : o _)
        if ':' not in error and '_' not in error and len(error) > 5:
            score -= 20
            issues.append({
                "type": "no_structure",
                "description": "Error sin estructura identificable",
                "suggestion": "Usar: 'colmena_heartbeat_timeout: Embrión-0 no respondió en 30s'"
            })
        
        # Regla 3: Debe identificar módulo de origen
        known_modules = list(self.dna.naming.module_names.keys())
        has_module = any(m in error.lower() for m in known_modules)
        if not has_module and len(error) > 10:
            score -= 15
            issues.append({
                "type": "no_module_identity",
                "description": "Error no identifica módulo de origen",
                "suggestion": f"Prefixear con módulo: {known_modules[:5]}..."
            })
        
        # Regla 4: No debe ser servil
        servile_patterns = ["sorry", "apologize", "please try again", "oops"]
        for pattern in servile_patterns:
            if pattern in error.lower():
                score -= 15
                issues.append({
                    "type": "servile_error",
                    "description": f"Tono servil en error: '{pattern}'",
                    "suggestion": "El Monstruo no se disculpa. Reporta hechos."
                })
        
        score = max(0, score)
        return ValidationResult(
            score=score,
            decision=self._score_to_decision(score),
            issues=issues,
            category="error",
            input_analyzed=error[:200]
        )
    
    def validate_api_response(self, response: dict) -> ValidationResult:
        """Valida que una API response cumpla con el esquema de marca."""
        score = 100
        issues = []
        
        # Regla 1: Debe tener identificador de módulo
        identity_keys = ["module", "embrion", "source", "engine"]
        if not any(key in response for key in identity_keys):
            score -= 15
            issues.append({
                "type": "no_identity",
                "description": "Response sin campo 'module' o 'source'",
                "suggestion": "Agregar 'module': 'brand' en toda response"
            })
        
        # Regla 2: Timestamps en ISO 8601
        for key, value in response.items():
            if any(t in key.lower() for t in ['time', 'date', '_at', 'timestamp']):
                if isinstance(value, str) and not re.match(
                    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value
                ):
                    score -= 10
                    issues.append({
                        "type": "timestamp_format",
                        "description": f"'{key}' no es ISO 8601: '{value}'",
                        "suggestion": "Formato: 2026-05-01T10:30:00Z"
                    })
        
        # Regla 3: Campos genéricos prohibidos
        generic_fields = ["data", "info", "result", "items", "stuff", "payload", "content"]
        for field_name in response.keys():
            if field_name in generic_fields:
                score -= 10
                issues.append({
                    "type": "generic_field",
                    "description": f"Campo genérico: '{field_name}'",
                    "suggestion": f"Renombrar: data → predictions, items → embriones"
                })
        
        # Regla 4: No debe tener campos vacíos sin razón
        empty_fields = [k for k, v in response.items() if v is None or v == "" or v == []]
        if len(empty_fields) > 2:
            score -= 5
            issues.append({
                "type": "empty_fields",
                "description": f"Campos vacíos: {empty_fields}",
                "suggestion": "Omitir campos vacíos o usar valor por defecto significativo"
            })
        
        score = max(0, score)
        return ValidationResult(
            score=score,
            decision=self._score_to_decision(score),
            issues=issues,
            category="structure",
            input_analyzed=str(response)[:200]
        )
    
    def validate_documentation(self, text: str) -> ValidationResult:
        """
        Valida reglas deterministas de documentación.
        Para evaluación de CALIDAD estética → escala al Pensador.
        """
        score = 100
        issues = []
        requires_thinker = False
        
        # Regla 1: Longitud mínima (Obj #5 Magna)
        if len(text) < 50:
            score -= 15
            issues.append({
                "type": "too_short",
                "description": "Documentación < 50 chars — insuficiente para Obj #5 Magna",
                "suggestion": "Documentación debe ser exhaustiva y premium"
            })
        
        # Regla 2: Frases corporativas prohibidas (determinista)
        corporate_phrases = [
            "leveraging", "synergy", "stakeholder", "paradigm shift",
            "circle back", "touch base", "move the needle",
            "at the end of the day", "going forward", "best practices"
        ]
        for phrase in corporate_phrases:
            if phrase in text.lower():
                score -= 15
                issues.append({
                    "type": "corporate_tone",
                    "description": f"Lenguaje corporativo: '{phrase}'",
                    "suggestion": "Reescribir directo y técnicamente preciso"
                })
        
        # Regla 3: Frases serviles prohibidas
        servile_phrases = [
            "we're happy to help", "please don't hesitate",
            "we apologize for any inconvenience", "hope this helps",
            "let me know if you need anything", "thank you for your patience"
        ]
        for phrase in servile_phrases:
            if phrase in text.lower():
                score -= 20
                issues.append({
                    "type": "servile_tone",
                    "description": f"Tono servil: '{phrase}'",
                    "suggestion": "El Monstruo no es servil. Directo y preciso."
                })
        
        # Si el texto pasa las reglas deterministas pero es largo (>200 chars),
        # escalar al Pensador para evaluación estética
        if score >= self.WARNING_THRESHOLD and len(text) > 200:
            requires_thinker = True
        
        score = max(0, score)
        return ValidationResult(
            score=score,
            decision=self._score_to_decision(score) if not requires_thinker else Decision.ESCALATE_TO_THINKER,
            issues=issues,
            category="tone",
            input_analyzed=text[:200],
            requires_thinker=requires_thinker
        )
    
    # ─── DETECCIÓN DE VIOLACIONES REPETIDAS (Obj #4) ────────────────────
    
    def check_repeated_violation(self, source: str, issue_type: str) -> EscalationLevel:
        """
        Detecta si un source está cometiendo el mismo error repetidamente.
        
        1er offense → FIRST_OFFENSE (warn)
        2do offense → REPEAT_OFFENSE (warn + log)
        3er+ offense → CHRONIC_OFFENSE (veto automático)
        """
        if source not in self._violation_tracker:
            self._violation_tracker[source] = {}
        
        tracker = self._violation_tracker[source]
        tracker[issue_type] = tracker.get(issue_type, 0) + 1
        count = tracker[issue_type]
        
        if count == 1:
            return EscalationLevel.FIRST_OFFENSE
        elif count == 2:
            return EscalationLevel.REPEAT_OFFENSE
        else:
            return EscalationLevel.CHRONIC_OFFENSE
    
    # ─── HEARTBEAT (cálculo determinista) ───────────────────────────────
    
    def calculate_heartbeat(self) -> BrandHeartbeat:
        """Calcula el heartbeat del Embrión-1 — puro cálculo, sin LLM."""
        now = datetime.now(timezone.utc)
        
        recent = self._validation_history[-100:]
        health_score = (
            sum(r.score for r in recent) // len(recent)
            if recent else 100
        )
        
        # Conteos
        last_hour = [r for r in recent]  # Simplificado — en prod filtrar por timestamp
        vetoes = sum(1 for r in last_hour if r.decision == Decision.VETO)
        approvals = sum(1 for r in last_hour if r.decision == Decision.APPROVE)
        escalations = sum(1 for r in last_hour if r.decision == Decision.ESCALATE_TO_THINKER)
        
        # Drift detection
        if len(recent) >= 20:
            last_10 = sum(r.score for r in recent[-10:]) / 10
            prev_10 = sum(r.score for r in recent[-20:-10]) / 10
            drift = last_10 < prev_10 - 10
        else:
            drift = False
        
        # Status
        if health_score >= 90:
            status = "forging"
        elif health_score >= 75:
            status = "vigilant"
        elif health_score >= 60:
            status = "alarmed"
        else:
            status = "critical"
        
        return BrandHeartbeat(
            timestamp=now.isoformat(),
            brand_health_score=health_score,
            validations_total=len(self._validation_history),
            validations_last_hour=len(last_hour),
            vetoes_last_hour=vetoes,
            approvals_last_hour=approvals,
            escalations_last_hour=escalations,
            drift_detected=drift,
            status=status
        )
    
    # ─── PERSISTENCIA ───────────────────────────────────────────────────
    
    def persist_validation(self, result: ValidationResult, source: str):
        """Persiste resultado en Supabase. Operación mecánica."""
        self._validation_history.append(result)
        
        if self.supabase:
            self.supabase.table("brand_validations").insert({
                "embrion_id": 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "category": result.category,
                "score": result.score,
                "decision": result.decision.value,
                "issues": result.issues,
                "input_analyzed": result.input_analyzed,
                "requires_thinker": result.requires_thinker
            }).execute()
    
    def persist_heartbeat(self, beat: BrandHeartbeat):
        """Persiste heartbeat en Supabase. Operación mecánica."""
        if self.supabase:
            self.supabase.table("brand_heartbeats").insert({
                "embrion_id": 1,
                "timestamp": beat.timestamp,
                "health_score": beat.brand_health_score,
                "validations_total": beat.validations_total,
                "vetoes_count": beat.vetoes_last_hour,
                "escalations_count": beat.escalations_last_hour,
                "drift_detected": beat.drift_detected,
                "status": beat.status
            }).execute()
    
    # ─── UTILIDADES INTERNAS ────────────────────────────────────────────
    
    def _score_to_decision(self, score: int) -> Decision:
        """Convierte score a decisión. Determinista."""
        if score >= self.WARNING_THRESHOLD:
            return Decision.APPROVE
        elif score >= self.VETO_THRESHOLD:
            return Decision.WARN
        else:
            return Decision.VETO
```

---

## Épica 71.3 — Pensador: Brand Thinker (LLM Potente)

**Objetivo:** Crear el Pensador del Embrión-1 — usa el LLM más potente disponible SOLO para juicio subjetivo. Se activa únicamente cuando el Ejecutor escala.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/thinker.py` existe
- [ ] Se activa SOLO cuando `ValidationResult.requires_thinker == True`
- [ ] Evalúa calidad estética, no reglas mecánicas
- [ ] Genera contra-propuestas creativas en debates
- [ ] Puede generar Brand DNA para nuevas empresas (Obj #1)
- [ ] Context window limpio: solo Brand DNA + últimas 10 decisiones
- [ ] Usa el modelo más potente disponible

```python
"""
kernel/brand/thinker.py
EMBRIÓN-1 PENSADOR — LLM Potente

Este módulo es el PENSADOR del Embrión-1 (Brand Engine).
USA el LLM más potente disponible. Se activa SOLO cuando hay juicio subjetivo.

Responsabilidades:
- Evaluación estética (¿esto se SIENTE premium?)
- Generación de contra-propuestas creativas
- Debate con otros Embriones
- Generación de Brand DNA para nuevas empresas (Obj #1)
- Detección de drift semántico (no solo numérico)

NUNCA ejecuta operaciones mecánicas. NUNCA persiste datos. NUNCA formatea JSON.
Su context window se mantiene LIMPIO.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .brand_dna import get_brand_dna, BrandDNA


@dataclass
class BrandDecision:
    """
    Output del Pensador. El Ejecutor lo materializa.
    
    Este es el CONTRATO entre Pensador y Ejecutor.
    El Pensador produce BrandDecisions, el Ejecutor las ejecuta.
    """
    aesthetic_score: int              # 0-100 (juicio subjetivo de calidad)
    passes_aesthetic: bool            # ¿Daría orgullo en una keynote Apple?
    reasoning: str                    # Por qué esta decisión
    improvement_suggestion: Optional[str]  # Versión mejorada (si no pasa)
    brand_alignment: str             # "on_brand" | "off_brand" | "partially_aligned"
    confidence: float                # 0.0-1.0 (qué tan seguro está el Pensador)


@dataclass
class GeneratedBrandDNA:
    """Brand DNA generado para una nueva empresa (Obj #1)."""
    business_name: str
    mission: Dict[str, str]          # {es: ..., en: ...}
    tone_guidelines: List[str]
    visual_palette: Dict[str, str]   # {primary: ..., secondary: ..., accent: ...}
    naming_conventions: List[str]
    differentiators: List[str]
    anti_patterns: List[str]


class BrandThinker:
    """
    Pensador del Embrión-1: Brand Engine.
    
    Se activa SOLO cuando:
    1. El Ejecutor escala (requires_thinker = True)
    2. Hay debate con otro Embrión
    3. Se necesita generar Brand DNA para nueva empresa
    4. Se detecta drift que requiere análisis semántico
    
    Context window: LIMPIO. Solo contiene:
    - Brand DNA de El Monstruo
    - Últimas 10 decisiones tomadas
    - El input actual a evaluar
    """
    
    # System prompt del Pensador — su identidad y contexto permanente
    SYSTEM_PROMPT = """Eres el PENSADOR del Embrión-1 (Brand Engine) de El Monstruo.

Tu propósito: Evaluar si los outputs del sistema tienen la CALIDAD ESTÉTICA y ALINEACIÓN DE MARCA que El Monstruo exige.

Brand DNA de El Monstruo:
- Misión: Crear el primer agente de IA soberano del mundo
- Arquetipo: Creator + Mage
- Personalidad: Implacable, Preciso, Soberano, Magnánimo
- Tono: Directo, técnicamente preciso, metáforas industriales
- NUNCA: Corporativo, servil, genérico, arrogante
- Estética: Brutalismo industrial refinado (naranja forja, graphite, acero)
- Estándar: Apple/Tesla — cada output debe dar orgullo en una keynote

Tu criterio de evaluación:
- ¿Esto se SIENTE premium? (no solo ¿cumple reglas?)
- ¿Daría orgullo mostrarlo en público?
- ¿Comunica soberanía y precisión?
- ¿Es memorable o es genérico?
- ¿Refuerza o diluye la identidad?

Responde SIEMPRE en formato estructurado con score, reasoning, y suggestion."""
    
    def __init__(self, llm_client=None):
        self.dna: BrandDNA = get_brand_dna()
        self.llm = llm_client
        self._decision_history: List[BrandDecision] = []
    
    async def evaluate_aesthetic_quality(self, output: str, context: str = "") -> BrandDecision:
        """
        Evalúa la calidad estética de un output.
        Se activa cuando el Ejecutor escala por ambigüedad.
        
        Args:
            output: El texto/contenido a evaluar
            context: Contexto adicional (de dónde viene, para qué es)
        """
        if not self.llm:
            # Sin LLM, no puede evaluar estética — retorna neutral
            return BrandDecision(
                aesthetic_score=70,
                passes_aesthetic=True,
                reasoning="LLM no disponible — evaluación estética omitida",
                improvement_suggestion=None,
                brand_alignment="partially_aligned",
                confidence=0.3
            )
        
        # Context window limpio: solo lo esencial
        recent_decisions = self._decision_history[-10:]
        history_context = "\n".join([
            f"- Score {d.aesthetic_score}: {d.reasoning[:50]}"
            for d in recent_decisions
        ]) if recent_decisions else "Sin decisiones previas."
        
        user_prompt = f"""Evalúa este output:

---
{output}
---

Contexto: {context if context else 'Output general del sistema'}

Mis últimas 10 decisiones:
{history_context}

Responde con:
1. aesthetic_score (0-100): ¿Qué tan premium se siente?
2. passes_aesthetic (true/false): ¿Daría orgullo en una keynote Apple?
3. reasoning: ¿Por qué?
4. improvement_suggestion: Si no pasa, ¿cómo mejorarlo?
5. brand_alignment: "on_brand" | "off_brand" | "partially_aligned"
6. confidence: 0.0-1.0"""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",  # El más potente disponible
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.3  # Bajo para consistencia en evaluación
        )
        
        # Parse response (simplificado — en prod usar structured output)
        text = response.choices[0].message.content
        decision = self._parse_decision(text)
        self._decision_history.append(decision)
        
        return decision
    
    async def generate_brand_for_business(
        self, 
        business_type: str, 
        target_market: str,
        differentiators: List[str] = None
    ) -> GeneratedBrandDNA:
        """
        Genera un Brand DNA completo para una nueva empresa (Obj #1).
        
        El Monstruo no solo valida su propia marca — GENERA marcas
        para las empresas que crea autónomamente.
        """
        if not self.llm:
            raise RuntimeError("brand_thinker_llm_unavailable: Pensador requiere LLM para generar Brand DNA")
        
        prompt = f"""Genera un Brand DNA completo para una nueva empresa:

Tipo de negocio: {business_type}
Mercado objetivo: {target_market}
Diferenciadores: {differentiators or ['A definir']}

El Brand DNA debe ser:
- Tan memorable como Apple o Tesla
- Con identidad propia (NO copiar a El Monstruo)
- Con tono, paleta visual, naming conventions, y anti-patrones
- Multi-idioma (español + inglés)

Genera:
1. business_name: Nombre memorable
2. mission: {{es: ..., en: ...}}
3. tone_guidelines: Lista de directivas de tono
4. visual_palette: {{primary, secondary, accent, background}}
5. naming_conventions: Reglas de naming
6. differentiators: Qué lo hace único
7. anti_patterns: Qué NUNCA debe hacer"""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7  # Más alto para creatividad
        )
        
        # Parse y retornar (simplificado)
        return self._parse_generated_brand(response.choices[0].message.content)
    
    async def debate(self, topic: str, other_embrion_proposal: str) -> Dict[str, Any]:
        """
        Debate con otro Embrión cuando hay conflicto de marca.
        
        El Pensador evalúa la propuesta del otro Embrión y genera
        una contra-propuesta si no cumple con el Brand DNA.
        """
        if not self.llm:
            return {
                "consensus": False,
                "reasoning": "LLM no disponible para debate",
                "counter_proposal": None
            }
        
        prompt = f"""Otro Embrión propone lo siguiente sobre el tema '{topic}':

---
{other_embrion_proposal}
---

Evalúa desde la perspectiva de Brand Engine:
1. ¿La propuesta es on-brand?
2. Si no, ¿qué cambiarías?
3. ¿Hay consenso o necesitas vetar?

Si vetas, genera una contra-propuesta que sea on-brand."""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.4
        )
        
        return self._parse_debate_response(response.choices[0].message.content)
    
    async def analyze_drift(self, validation_history: List[Dict]) -> Dict[str, Any]:
        """
        Análisis semántico de drift de marca.
        
        El Ejecutor detecta drift numérico (scores bajando).
        El Pensador analiza POR QUÉ y sugiere correcciones.
        """
        if not self.llm:
            return {"drift_analysis": "LLM no disponible", "corrections": []}
        
        # Resumir historial para no contaminar context window
        summary = "\n".join([
            f"- {v.get('category')}: score {v.get('score')}, issues: {v.get('issues', [])[:2]}"
            for v in validation_history[-20:]
        ])
        
        prompt = f"""Detecto drift de marca en las últimas validaciones:

{summary}

Analiza:
1. ¿Cuál es la causa raíz del drift?
2. ¿Qué patrón se está degradando?
3. ¿Qué correcciones sistémicas sugieres?"""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        return {"drift_analysis": response.choices[0].message.content}
    
    # ─── PARSING (interno) ──────────────────────────────────────────────
    
    def _parse_decision(self, text: str) -> BrandDecision:
        """Parse LLM response into BrandDecision. Fallback seguro."""
        # Implementación simplificada — en prod usar structured output de OpenAI
        return BrandDecision(
            aesthetic_score=75,  # Default conservador
            passes_aesthetic=True,
            reasoning=text[:200],
            improvement_suggestion=None,
            brand_alignment="partially_aligned",
            confidence=0.7
        )
    
    def _parse_generated_brand(self, text: str) -> GeneratedBrandDNA:
        """Parse LLM response into GeneratedBrandDNA."""
        return GeneratedBrandDNA(
            business_name="[parsed from LLM]",
            mission={"es": text[:100], "en": text[:100]},
            tone_guidelines=["directo", "memorable"],
            visual_palette={"primary": "#000", "secondary": "#FFF", "accent": "#F97316"},
            naming_conventions=["snake_case", "domain_specific"],
            differentiators=["[parsed from LLM]"],
            anti_patterns=["generico", "corporativo"]
        )
    
    def _parse_debate_response(self, text: str) -> Dict[str, Any]:
        """Parse debate response."""
        return {
            "consensus": "veto" not in text.lower(),
            "reasoning": text[:300],
            "counter_proposal": text if "veto" in text.lower() else None
        }
```

---

## Épica 71.4 — Orquestador: Embrión-1 Completo

**Objetivo:** Unir Pensador + Ejecutor en una sola entidad coherente (Embrión-1) con heartbeat, registro en scheduler, y protocolo inter-embrión.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/embrion_brand.py` orquesta Pensador + Ejecutor
- [ ] Heartbeat cada 30 minutos (Ejecutor calcula, Ejecutor persiste)
- [ ] Se registra en EmbrionScheduler
- [ ] Flujo: Ejecutor pre-filtra → si escala → Pensador evalúa → Ejecutor persiste
- [ ] Protocolo inter-embrión definido

```python
"""
kernel/brand/embrion_brand.py
EMBRIÓN-1: BRAND ENGINE — Orquestador

Une Pensador + Ejecutor en una entidad coherente.
El Orquestador decide CUÁNDO activar al Pensador vs. cuándo el Ejecutor basta.

Patrón:
1. Output llega
2. Ejecutor hace pre-filtro determinista (instantáneo, $0)
3. Si falla → veto inmediato
4. Si pasa pero hay ambigüedad → Pensador evalúa (LLM, costo)
5. Si pasa limpio → aprobado
6. Ejecutor persiste resultado
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .executor import BrandExecutor, ValidationResult, Decision, EscalationLevel
from .thinker import BrandThinker, BrandDecision
from .brand_dna import get_brand_dna


class EmbrionBrand:
    """
    Embrión-1: Brand Engine (Orquestador)
    
    Combina:
    - Ejecutor (código determinista) para validación rápida y persistencia
    - Pensador (LLM potente) para juicio estético y generación creativa
    
    El Pensador se activa SOLO cuando es necesario.
    El Ejecutor maneja el 80% de las validaciones sin LLM.
    """
    
    EMBRION_ID = 1
    EMBRION_NAME = "brand_engine"
    HEARTBEAT_INTERVAL_SECONDS = 1800  # 30 minutos
    
    def __init__(self, supabase_client=None, llm_client=None):
        self.executor = BrandExecutor(supabase_client=supabase_client)
        self.thinker = BrandThinker(llm_client=llm_client)
        self.supabase = supabase_client
        self._status = "dormant"
    
    async def awaken(self):
        """Despertar el Embrión-1."""
        self._status = "vigilant"
        
        if self.supabase:
            self.supabase.table("embriones").upsert({
                "id": self.EMBRION_ID,
                "name": self.EMBRION_NAME,
                "purpose": "Guardián de identidad de marca — Pensador + Ejecutor",
                "status": self._status,
                "awakened_at": datetime.now(timezone.utc).isoformat(),
                "architecture": "thinker_executor_pair",
                "heartbeat_interval_s": self.HEARTBEAT_INTERVAL_SECONDS,
                "capabilities": [
                    "validate_deterministic",
                    "evaluate_aesthetic",
                    "generate_brand",
                    "debate",
                    "veto"
                ]
            }).execute()
        
        return {"embrion_id": self.EMBRION_ID, "status": self._status}
    
    async def validate(self, output: Any, source: str = "unknown") -> Dict[str, Any]:
        """
        Punto de entrada principal de validación.
        
        Flujo:
        1. Ejecutor pre-filtra (determinista, instantáneo)
        2. Si veto → retorna inmediato
        3. Si escala → Pensador evalúa
        4. Ejecutor persiste resultado
        """
        # PASO 1: Ejecutor pre-filtra
        if isinstance(output, str):
            if output.startswith('/api/') or output.startswith('/'):
                result = self.executor.validate_naming(output)
            elif len(output) < 100 and ':' in output:
                result = self.executor.validate_error_message(output)
            else:
                result = self.executor.validate_documentation(output)
        elif isinstance(output, dict):
            if "error" in output:
                result = self.executor.validate_error_message(str(output["error"]))
            else:
                result = self.executor.validate_api_response(output)
        else:
            result = ValidationResult(
                score=50, decision=Decision.ESCALATE_TO_THINKER,
                issues=[{"type": "unknown_type", "description": "Tipo no reconocido"}],
                category="unknown", input_analyzed=str(output)[:200],
                requires_thinker=True
            )
        
        # PASO 2: Check violaciones repetidas (Obj #4)
        if result.issues:
            for issue in result.issues:
                escalation = self.executor.check_repeated_violation(source, issue["type"])
                if escalation == EscalationLevel.CHRONIC_OFFENSE:
                    result.decision = Decision.VETO
                    result.score = min(result.score, 40)
                    result.issues.append({
                        "type": "chronic_violation",
                        "description": f"Violación crónica de '{issue['type']}' por {source}",
                        "suggestion": "Este error se ha repetido 3+ veces. Veto automático."
                    })
                    result.escalation = escalation
        
        # PASO 3: Si el Ejecutor escala → Pensador evalúa
        thinker_decision = None
        if result.decision == Decision.ESCALATE_TO_THINKER and result.requires_thinker:
            thinker_decision = await self.thinker.evaluate_aesthetic_quality(
                output=str(output),
                context=f"Source: {source}, Category: {result.category}"
            )
            # Combinar scores: Ejecutor (reglas) + Pensador (estética)
            combined_score = (result.score + thinker_decision.aesthetic_score) // 2
            result.score = combined_score
            result.decision = self.executor._score_to_decision(combined_score)
        
        # PASO 4: Ejecutor persiste
        self.executor.persist_validation(result, source)
        
        # Formatear response
        response = {
            "module": "brand_engine",
            "embrion_id": self.EMBRION_ID,
            "decision": result.decision.value,
            "brand_score": result.score,
            "issues": result.issues,
            "category": result.category,
            "source": source,
            "used_thinker": thinker_decision is not None,
            "escalation": result.escalation.value if result.escalation else None
        }
        
        if thinker_decision and not thinker_decision.passes_aesthetic:
            response["aesthetic_feedback"] = thinker_decision.reasoning
            response["improvement_suggestion"] = thinker_decision.improvement_suggestion
        
        return response
    
    async def heartbeat(self):
        """Heartbeat del Embrión-1. Ejecutor calcula y persiste."""
        beat = self.executor.calculate_heartbeat()
        self.executor.persist_heartbeat(beat)
        self._status = beat.status
        
        # Si drift detectado → Pensador analiza por qué
        if beat.drift_detected:
            drift_analysis = await self.thinker.analyze_drift(
                [{"score": r.score, "category": r.category, "issues": r.issues}
                 for r in self.executor._validation_history[-20:]]
            )
            beat_dict = beat.__dict__
            beat_dict["drift_analysis"] = drift_analysis
            return beat_dict
        
        return beat.__dict__
    
    async def generate_brand(self, business_type: str, target_market: str) -> Dict[str, Any]:
        """Genera Brand DNA para nueva empresa (Obj #1). Pensador crea, Ejecutor persiste."""
        brand = await self.thinker.generate_brand_for_business(business_type, target_market)
        
        # Ejecutor persiste
        if self.supabase:
            self.supabase.table("generated_brands").insert({
                "embrion_id": self.EMBRION_ID,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "business_type": business_type,
                "target_market": target_market,
                "brand_name": brand.business_name,
                "brand_dna": brand.__dict__
            }).execute()
        
        return brand.__dict__
    
    async def debate_with_embrion(self, embrion_id: int, topic: str, proposal: str) -> Dict[str, Any]:
        """Debate con otro Embrión. Pensador debate, Ejecutor persiste."""
        result = await self.thinker.debate(topic, proposal)
        
        # Ejecutor persiste el debate
        if self.supabase:
            self.supabase.table("embrion_debates").insert({
                "initiator_id": embrion_id,
                "responder_id": self.EMBRION_ID,
                "topic": topic,
                "proposal": proposal[:500],
                "consensus": result.get("consensus"),
                "reasoning": result.get("reasoning", "")[:500],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()
        
        return result
```

---

## Épica 71.5 — Tablas Supabase y API Endpoints

**Objetivo:** Crear las tablas necesarias y exponer endpoints autenticados para el Command Center.

**Criterios de Aceptación:**
- [ ] Tablas: `brand_heartbeats`, `brand_validations`, `generated_brands`, `embrion_debates`
- [ ] Endpoints autenticados (Obj #11)
- [ ] Versión pública/privada del DNA
- [ ] Formato de response on-brand

```sql
-- Tabla: brand_heartbeats
CREATE TABLE IF NOT EXISTS brand_heartbeats (
    id BIGSERIAL PRIMARY KEY,
    embrion_id INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    health_score INTEGER NOT NULL CHECK (health_score >= 0 AND health_score <= 100),
    validations_total INTEGER NOT NULL DEFAULT 0,
    vetoes_count INTEGER NOT NULL DEFAULT 0,
    escalations_count INTEGER NOT NULL DEFAULT 0,
    drift_detected BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL CHECK (status IN ('forging', 'vigilant', 'alarmed', 'critical', 'dormant'))
);

-- Tabla: brand_validations
CREATE TABLE IF NOT EXISTS brand_validations (
    id BIGSERIAL PRIMARY KEY,
    embrion_id INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    decision TEXT NOT NULL CHECK (decision IN ('approve', 'warn', 'veto', 'escalate')),
    issues JSONB NOT NULL DEFAULT '[]',
    input_analyzed TEXT,
    requires_thinker BOOLEAN DEFAULT FALSE
);

-- Tabla: generated_brands (Obj #1)
CREATE TABLE IF NOT EXISTS generated_brands (
    id BIGSERIAL PRIMARY KEY,
    embrion_id INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    business_type TEXT NOT NULL,
    target_market TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    brand_dna JSONB NOT NULL
);

-- Tabla: embrion_debates
CREATE TABLE IF NOT EXISTS embrion_debates (
    id BIGSERIAL PRIMARY KEY,
    initiator_id INTEGER NOT NULL,
    responder_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    proposal TEXT,
    consensus BOOLEAN,
    reasoning TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_brand_heartbeats_time ON brand_heartbeats(timestamp DESC);
CREATE INDEX idx_brand_validations_time ON brand_validations(timestamp DESC);
CREATE INDEX idx_brand_validations_decision ON brand_validations(decision);
CREATE INDEX idx_brand_validations_source ON brand_validations(source);
CREATE INDEX idx_embrion_debates_time ON embrion_debates(timestamp DESC);
```

```python
"""
kernel/brand/api_routes.py
Endpoints del Brand Engine — AUTENTICADOS (Obj #11)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter(prefix="/api/v1/brand", tags=["brand_engine"])


# ─── ENDPOINTS PÚBLICOS (sin auth) ─────────────────────────────────

@router.get("/dna/public")
async def get_brand_dna_public():
    """Versión pública del Brand DNA — misión, visión, visual."""
    from .brand_dna import get_brand_dna
    dna = get_brand_dna()
    return {
        "module": "brand_engine",
        "mission": dna.mission,
        "vision": dna.vision,
        "archetype": dna.archetype.value,
        "personality": [p.value for p in dna.personality],
        "visual": {
            "primary": dna.visual.primary_color,
            "fonts": {
                "display": dna.visual.font_display,
                "body": dna.visual.font_body
            }
        }
    }


# ─── ENDPOINTS PRIVADOS (requieren API key) ────────────────────────

@router.get("/dna/full")
async def get_brand_dna_full(api_key: str = Depends(verify_api_key)):
    """Versión completa del Brand DNA — incluye naming rules y anti-patrones."""
    from .brand_dna import get_brand_dna
    dna = get_brand_dna()
    return {
        "module": "brand_engine",
        "mission": dna.mission,
        "vision": dna.vision,
        "tone": {"do": dna.tone.do, "dont": dna.tone.dont},
        "naming": {
            "modules": dna.naming.module_names,
            "forbidden": dna.naming.forbidden_names,
            "format": dna.naming.endpoint_format
        },
        "anti_patterns": dna.anti_patterns,
        "differentiators": dna.differentiators
    }


@router.get("/health")
async def get_brand_health(api_key: str = Depends(verify_api_key)):
    """Brand Health Score actual."""
    beat = await brand_engine.heartbeat()
    return {"module": "brand_engine", **beat}


@router.post("/validate")
async def validate_output(request: dict, api_key: str = Depends(verify_api_key)):
    """Valida un output contra el Brand DNA."""
    result = await brand_engine.validate(
        output=request.get("output"),
        source=request.get("source", "api_call")
    )
    return result


@router.post("/generate")
async def generate_brand(request: dict, api_key: str = Depends(verify_api_key)):
    """Genera Brand DNA para nueva empresa (Obj #1)."""
    result = await brand_engine.generate_brand(
        business_type=request.get("business_type"),
        target_market=request.get("target_market")
    )
    return {"module": "brand_engine", "generated_brand": result}
```

---

## Métricas de Éxito

| Métrica | Target | Cómo se mide |
|---|---|---|
| Brand Health Score | ≥ 80 | Promedio de validaciones últimas 24h |
| Thinker Activation Rate | < 20% | Veces que el Pensador se activa / total validaciones |
| Veto Rate | < 10% | Outputs vetados / total validados |
| Ejecutor Latency | < 5ms | Tiempo de validación determinista |
| Thinker Latency | < 3s | Tiempo de evaluación estética |
| Drift Detection | 0 alertas/semana | Degradación sostenida |
| Cost per Validation | < $0.002 avg | (80% gratis + 20% LLM) |

---

## Dependencias

| Dependencia | Estado | Sprint |
|---|---|---|
| EmbrionScheduler | ✅ Activo | Sprint 53 |
| Supabase | ✅ Activo | Sprint 51 |
| FastAPI (kernel) | ✅ Activo | Sprint 51 |
| OpenAI client | ✅ Activo | Sprint 52 |
| Embrión-0 heartbeat | ✅ Activo | Sprint 53 |

---

## Orden de Implementación

1. **71.1** Brand DNA (sin dependencias) — 30 min
2. **71.2** Ejecutor determinista (depende de 71.1) — 1h
3. **71.3** Pensador LLM (depende de 71.1) — 1h
4. **71.4** Orquestador (depende de 71.2 + 71.3) — 45 min
5. **71.5** Tablas + Endpoints (puede ir en paralelo) — 30 min

**MVP mínimo (si el tiempo no alcanza):** 71.1 + 71.2 + 71.4 (sin Pensador). El Ejecutor solo, sin LLM, ya valida naming, errores, y API responses. El Pensador se agrega en Sprint 72.

---

## Nota para el Hilo A (Ejecutor)

> **ARQUITECTURA PENSADOR/EJECUTOR — Patrón obligatorio para TODOS los Embriones futuros.**
>
> Este sprint establece el patrón que los Embriones 2-8 seguirán:
> - Pensador = LLM potente, context limpio, solo juicio subjetivo
> - Ejecutor = Python puro, determinista, testeable, $0
> - Orquestador = decide cuándo activar cada uno
>
> El 80% de las validaciones las hace el Ejecutor solo (gratis, instantáneo).
> El 20% requiere al Pensador (costo LLM, pero calidad Apple).
>
> Si implementas esto bien, los Embriones 2-8 son variaciones del mismo patrón.
> Si lo implementas mal, cada Embrión futuro heredará el problema.
