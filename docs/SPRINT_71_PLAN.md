# SPRINT 71 — "El Primer Hijo Nace con Propósito"

**Serie:** 71-80 "La Colmena Despierta"
**Fecha de diseño:** 1 de Mayo de 2026
**Arquitecto:** Hilo B
**Capa Arquitectónica:** CAPA 2 (Inteligencia Emergente)
**Objetivo Primario:** #2 (Apple/Tesla), #8 (Emergencia), #9 (Transversalidad)

---

## Contexto

El Embrión-0 existe. Tiene heartbeat, FCS, debate interno, y capacidad de orquestación. Pero está solo. La Colmena (Objetivo #6) requiere múltiples Embriones especializados que debaten entre sí y generan inteligencia emergente.

Sprint 71 marca el nacimiento del **primer Embrión con propósito específico**: el Brand Engine. No es un clon del Embrión-0 — es una entidad distinta con un dominio de expertise propio, métricas propias, y un rol claro en el ecosistema.

**¿Por qué Brand Engine primero?** Porque es el quality gate que validará a todos los Embriones futuros. Sin él, los Embriones 2-8 producirían outputs genéricos. El Brand Engine es el estándar contra el cual todo se mide.

---

## Arquitectura del Embrión-1

```
┌─────────────────────────────────────────────────────────┐
│                    EMBRIÓN-1: BRAND ENGINE                │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────┐  ┌─────────────────────────────────┐│
│  │   BRAND DNA    │  │        BRAND VALIDATOR           ││
│  │   (Inmutable)  │  │                                   ││
│  │                │  │  • validate_output(output) → score││
│  │  Misión        │  │  • validate_naming(name) → bool  ││
│  │  Arquetipo     │  │  • validate_tone(text) → score   ││
│  │  Personalidad  │  │  • validate_visual(asset) → score││
│  │  Tono          │  │  • suggest_improvement(output)   ││
│  │  Estética      │  │                                   ││
│  │  Naming        │  └─────────────────────────────────┘│
│  │  Anti-patrones │                                      │
│  └────────────────┘  ┌─────────────────────────────────┐│
│                       │        BRAND MONITOR             ││
│  ┌────────────────┐  │                                   ││
│  │   HEARTBEAT    │  │  • health_score() → 0-100       ││
│  │                │  │  • drift_detection() → alerts   ││
│  │  FCS propio    │  │  • competitor_benchmark()       ││
│  │  Latido c/30m  │  │  • llm_representation_check()  ││
│  │  Estado vital  │  │                                   ││
│  └────────────────┘  └─────────────────────────────────┘│
│                                                           │
│  ┌──────────────────────────────────────────────────────┐│
│  │              INTER-EMBRIÓN PROTOCOL                   ││
│  │                                                        ││
│  │  • Recibe outputs de Embrión-0 para validación        ││
│  │  • Envía brand scores al EmbrionScheduler             ││
│  │  • Puede VETAR outputs que no pasen threshold (< 60)  ││
│  │  • Debate con Embrión-0 cuando hay conflicto          ││
│  └──────────────────────────────────────────────────────┘│
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Épica 71.1 — Brand DNA como Módulo del Kernel

**Objetivo:** Codificar la identidad de marca de El Monstruo como un módulo Python inmutable que cualquier parte del sistema puede consultar.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/brand_dna.py` existe y es importable
- [ ] Contiene TODA la identidad: misión, visión, arquetipo, personalidad, tono, estética, naming, anti-patrones
- [ ] Tiene funciones de consulta: `get_tone_guidelines()`, `get_naming_rules()`, `get_visual_palette()`, `is_anti_pattern(name)`
- [ ] Tests unitarios pasan
- [ ] Deployado en Railway

```python
"""
kernel/brand/brand_dna.py
EL MONSTRUO — Brand DNA Module (Inmutable)

Este módulo define la identidad de marca del Monstruo.
Es la fuente de verdad única. No se modifica sin aprobación del Guardián.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class BrandArchetype(Enum):
    CREATOR = "creator"
    MAGE = "mage"
    CREATOR_MAGE = "creator_mage"  # El Monstruo es ambos


class BrandPersonality(Enum):
    IMPLACABLE = "implacable"      # No se detiene hasta cumplir
    PRECISO = "preciso"            # Cada decisión es deliberada
    SOBERANO = "soberano"          # No depende de nadie
    MAGNANIMO = "magnánimo"        # Cuando produce, produce lo mejor


@dataclass(frozen=True)
class ToneOfVoice:
    """Tono de voz inmutable de El Monstruo."""
    do: tuple = (
        "directo_sin_rodeos",
        "tecnicamente_preciso",
        "confiado_sin_arrogancia",
        "metaforas_industriales",
        "conciso_pero_completo"
    )
    dont: tuple = (
        "corporativo",
        "pedante",
        "arrogante",
        "generico",
        "servil",
        "excesivamente_amigable"
    )
    metaphor_domain: tuple = (
        "forja", "fundir", "templar", "fragua",
        "ensamblaje", "calibrar", "presión",
        "colmena", "latido", "despertar"
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
    motifs: tuple = ("manómetros", "gauges", "líneas_ensamblaje", "chispas", "metal_fundido")


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
        "vanguard": "Scanner de herramientas"
    })
    endpoint_format: str = "/api/v1/{module}/{action}"
    error_format: str = "{module}_{action}_{failure_type}"
    forbidden_names: tuple = (
        "service", "handler", "utils", "helper", "misc",
        "stuff", "thing", "data", "info", "manager"
    )


@dataclass(frozen=True)
class BrandDNA:
    """La identidad completa e inmutable de El Monstruo."""
    
    mission: str = "Crear el primer agente de IA soberano del mundo que genera negocios exitosos de forma autónoma"
    vision: str = "Un ecosistema de Monstruos interconectados que democratiza la creación de empresas"
    
    archetype: BrandArchetype = BrandArchetype.CREATOR_MAGE
    personality: tuple = (
        BrandPersonality.IMPLACABLE,
        BrandPersonality.PRECISO,
        BrandPersonality.SOBERANO,
        BrandPersonality.MAGNANIMO
    )
    
    tone: ToneOfVoice = field(default_factory=ToneOfVoice)
    visual: VisualIdentity = field(default_factory=VisualIdentity)
    naming: NamingConvention = field(default_factory=NamingConvention)
    
    anti_patterns: tuple = (
        "chatbot_amigable",
        "asistente_servil",
        "herramienta_generica",
        "dashboard_grafana_clone",
        "wrapper_apis_sin_identidad",
        "output_sin_contexto",
        "error_message_generico"
    )
    
    # Differentiators — Lo que nos hace únicos
    differentiators: tuple = (
        "primer_agente_soberano_del_mundo",
        "inteligencia_emergente_no_programada",
        "7_capas_transversales_desde_dia_1",
        "colmena_de_embriones_especializados",
        "brand_engine_integrado_en_kernel"
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


def get_error_code(module: str, action: str, failure_type: str) -> str:
    """Genera un error code on-brand."""
    return EL_MONSTRUO_DNA.naming.error_format.format(
        module=module, action=action, failure_type=failure_type
    )


def get_endpoint_path(module: str, action: str) -> str:
    """Genera un endpoint path on-brand."""
    if module not in EL_MONSTRUO_DNA.naming.module_names:
        raise ValueError(
            f"Módulo '{module}' no reconocido. "
            f"Módulos válidos: {list(EL_MONSTRUO_DNA.naming.module_names.keys())}"
        )
    return EL_MONSTRUO_DNA.naming.endpoint_format.format(
        module=module, action=action
    )
```

---

## Épica 71.2 — Brand Validator (El Evaluador)

**Objetivo:** Crear un evaluador que recibe cualquier output del sistema y retorna un brand compliance score (0-100) con issues específicos y sugerencias de mejora.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/brand_validator.py` existe
- [ ] Evalúa: naming, tone, error messages, API responses, documentation
- [ ] Score 0-100 con threshold configurable (default: 75)
- [ ] Retorna issues específicos con sugerencias de corrección
- [ ] Integrado con LLM para evaluación de tono (usa GPT-4o-mini para cost efficiency)
- [ ] Tests con casos positivos y negativos

```python
"""
kernel/brand/brand_validator.py
EL MONSTRUO — Brand Validator

Evalúa cualquier output contra el Brand DNA.
Score 0-100. Threshold mínimo: 75 (configurable).
Puede VETAR outputs que no pasen.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .brand_dna import get_brand_dna, is_forbidden_name, BrandDNA


@dataclass
class ValidationResult:
    """Resultado de una validación de marca."""
    score: int                          # 0-100
    passes: bool                        # score >= threshold
    issues: List[Dict[str, str]]        # [{type, description, suggestion}]
    category: str                       # naming | tone | visual | structure | error
    input_analyzed: str                 # Lo que se evaluó (truncado)
    
    def to_dict(self) -> dict:
        return {
            "brand_score": self.score,
            "passes": self.passes,
            "issues_count": len(self.issues),
            "issues": self.issues,
            "category": self.category
        }


class BrandValidator:
    """
    Validador de compliance de marca para El Monstruo.
    
    Uso:
        validator = BrandValidator()
        result = validator.validate_naming("/api/v1/service/getData")
        if not result.passes:
            print(f"Score: {result.score}, Issues: {result.issues}")
    """
    
    def __init__(self, threshold: int = 75):
        self.dna: BrandDNA = get_brand_dna()
        self.threshold = threshold
    
    def validate_naming(self, name: str) -> ValidationResult:
        """Evalúa si un nombre (endpoint, módulo, variable) cumple con la marca."""
        score = 100
        issues = []
        
        # Check forbidden names
        for forbidden in self.dna.naming.forbidden_names:
            if forbidden in name.lower():
                score -= 25
                issues.append({
                    "type": "forbidden_name",
                    "description": f"Nombre prohibido detectado: '{forbidden}'",
                    "suggestion": f"Reemplazar '{forbidden}' con un nombre que refleje el dominio: "
                                  f"{list(self.dna.naming.module_names.keys())}"
                })
        
        # Check camelCase (preferimos snake_case)
        if re.search(r'[a-z][A-Z]', name) and '/api/' not in name:
            score -= 10
            issues.append({
                "type": "naming_style",
                "description": "camelCase detectado — El Monstruo usa snake_case",
                "suggestion": "Convertir a snake_case: getData → get_data"
            })
        
        # Check generic patterns
        generic_patterns = ['get_all', 'do_thing', 'process_data', 'handle_request']
        for pattern in generic_patterns:
            if pattern in name.lower():
                score -= 15
                issues.append({
                    "type": "generic_naming",
                    "description": f"Patrón genérico: '{pattern}'",
                    "suggestion": "Usar nombre específico del dominio: "
                                  "get_all → list_embriones, process_data → forge_prediction"
                })
        
        # Check endpoint format
        if name.startswith('/api/') and not re.match(r'/api/v\d+/\w+/\w+', name):
            score -= 15
            issues.append({
                "type": "endpoint_format",
                "description": "Endpoint no sigue formato /api/v{n}/{module}/{action}",
                "suggestion": f"Formato correcto: /api/v1/{{module}}/{{action}}"
            })
        
        return ValidationResult(
            score=max(0, score),
            passes=max(0, score) >= self.threshold,
            issues=issues,
            category="naming",
            input_analyzed=name[:100]
        )
    
    def validate_error_message(self, error: Any) -> ValidationResult:
        """Evalúa si un error message cumple con la marca."""
        score = 100
        issues = []
        
        error_str = str(error) if not isinstance(error, str) else error
        
        # Check generic error messages
        generic_errors = [
            "internal server error", "something went wrong",
            "unknown error", "an error occurred", "error",
            "bad request", "not found", "unauthorized"
        ]
        
        for generic in generic_errors:
            if error_str.lower().strip() == generic:
                score -= 40
                issues.append({
                    "type": "generic_error",
                    "description": f"Error genérico: '{error_str}'",
                    "suggestion": "Usar formato: {module}_{action}_{failure_type} con contexto. "
                                  "Ej: 'embrion_heartbeat_timeout: Embrión-0 no respondió en 30s'"
                })
        
        # Check if has context
        if isinstance(error, str) and ':' not in error and '_' not in error:
            score -= 20
            issues.append({
                "type": "no_context",
                "description": "Error sin contexto ni estructura",
                "suggestion": "Agregar módulo y contexto: '{module}_{action}_{type}: {descripción}'"
            })
        
        # Check if has module identifier
        known_modules = list(self.dna.naming.module_names.keys())
        has_module = any(m in error_str.lower() for m in known_modules)
        if not has_module and len(error_str) > 10:
            score -= 15
            issues.append({
                "type": "no_module_identity",
                "description": "Error no identifica qué módulo lo generó",
                "suggestion": f"Prefixear con módulo: {known_modules}"
            })
        
        return ValidationResult(
            score=max(0, score),
            passes=max(0, score) >= self.threshold,
            issues=issues,
            category="error",
            input_analyzed=error_str[:200]
        )
    
    def validate_api_response(self, response: dict) -> ValidationResult:
        """Evalúa si una respuesta de API cumple con la marca."""
        score = 100
        issues = []
        
        # Check if response has identity
        identity_keys = ["module", "embrion", "source", "forja", "version"]
        if not any(key in response for key in identity_keys):
            score -= 15
            issues.append({
                "type": "no_identity",
                "description": "Response sin identificador de módulo/fuente",
                "suggestion": "Agregar campo 'module' o 'source' en toda response"
            })
        
        # Check if timestamps are ISO format
        for key, value in response.items():
            if 'time' in key.lower() or 'date' in key.lower() or 'at' in key.lower():
                if isinstance(value, str) and not re.match(
                    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value
                ):
                    score -= 10
                    issues.append({
                        "type": "timestamp_format",
                        "description": f"Timestamp '{key}' no es ISO 8601",
                        "suggestion": "Usar formato: 2026-05-01T10:30:00Z"
                    })
        
        # Check generic field names
        generic_fields = ["data", "info", "result", "items", "stuff", "payload"]
        for field_name in response.keys():
            if field_name in generic_fields:
                score -= 10
                issues.append({
                    "type": "generic_field",
                    "description": f"Campo genérico: '{field_name}'",
                    "suggestion": f"Renombrar '{field_name}' a algo específico del dominio: "
                                  "data → predictions, items → embriones, result → forge_output"
                })
        
        return ValidationResult(
            score=max(0, score),
            passes=max(0, score) >= self.threshold,
            issues=issues,
            category="structure",
            input_analyzed=str(response)[:200]
        )
    
    def validate_documentation(self, text: str) -> ValidationResult:
        """Evalúa si un texto de documentación cumple con el tono de marca."""
        score = 100
        issues = []
        
        # Check corporate language
        corporate_phrases = [
            "leveraging", "synergy", "stakeholder", "paradigm shift",
            "circle back", "touch base", "move the needle",
            "at the end of the day", "going forward"
        ]
        for phrase in corporate_phrases:
            if phrase in text.lower():
                score -= 15
                issues.append({
                    "type": "corporate_tone",
                    "description": f"Lenguaje corporativo detectado: '{phrase}'",
                    "suggestion": "Reescribir en tono directo y técnicamente preciso"
                })
        
        # Check servile language
        servile_phrases = [
            "we're happy to help", "please don't hesitate",
            "we apologize for any inconvenience", "thank you for your patience",
            "hope this helps", "let me know if you need anything"
        ]
        for phrase in servile_phrases:
            if phrase in text.lower():
                score -= 20
                issues.append({
                    "type": "servile_tone",
                    "description": f"Tono servil detectado: '{phrase}'",
                    "suggestion": "El Monstruo no es servil. Ser directo y preciso."
                })
        
        # Check if too short (documentation should be comprehensive - Obj #5 Magna)
        if len(text) < 50 and '\n' not in text:
            score -= 10
            issues.append({
                "type": "insufficient_documentation",
                "description": "Documentación demasiado breve",
                "suggestion": "Obj #5 (Magna): La documentación debe ser exhaustiva y premium"
            })
        
        return ValidationResult(
            score=max(0, score),
            passes=max(0, score) >= self.threshold,
            issues=issues,
            category="tone",
            input_analyzed=text[:200]
        )
    
    def full_audit(self, outputs: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """Auditoría completa de múltiples outputs."""
        results = {}
        
        if "endpoints" in outputs:
            for ep in outputs["endpoints"]:
                results[f"naming:{ep}"] = self.validate_naming(ep)
        
        if "errors" in outputs:
            for err in outputs["errors"]:
                results[f"error:{err[:30]}"] = self.validate_error_message(err)
        
        if "responses" in outputs:
            for i, resp in enumerate(outputs["responses"]):
                results[f"response:{i}"] = self.validate_api_response(resp)
        
        if "docs" in outputs:
            for i, doc in enumerate(outputs["docs"]):
                results[f"doc:{i}"] = self.validate_documentation(doc)
        
        return results
    
    def get_overall_score(self, results: Dict[str, ValidationResult]) -> int:
        """Calcula score promedio de una auditoría completa."""
        if not results:
            return 0
        scores = [r.score for r in results.values()]
        return sum(scores) // len(scores)
```

---

## Épica 71.3 — Embrión-1 como Entidad Viva

**Objetivo:** Instanciar el Embrión-1 como una entidad con heartbeat propio, FCS, y capacidad de comunicarse con Embrión-0 via el protocolo inter-embrión.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/brand/embrion_brand.py` existe
- [ ] Tiene heartbeat independiente (cada 30 minutos)
- [ ] Calcula su propio FCS (Brand Health Score)
- [ ] Se registra en el EmbrionScheduler como Embrión-1
- [ ] Puede recibir outputs de Embrión-0 para validación
- [ ] Puede VETAR outputs con score < 60
- [ ] Tabla `brand_validations` creada en Supabase

```python
"""
kernel/brand/embrion_brand.py
EMBRIÓN-1: BRAND ENGINE

El primer hijo de la Colmena. Su propósito: garantizar que todo output
del Monstruo sea consistente con su identidad de marca.

No es un módulo pasivo. Es una entidad viva con:
- Heartbeat propio (cada 30 minutos)
- FCS propio (Brand Health Score)
- Capacidad de VETAR outputs
- Comunicación con Embrión-0
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .brand_dna import get_brand_dna, BrandDNA
from .brand_validator import BrandValidator, ValidationResult


@dataclass
class BrandHeartbeat:
    """Estado vital del Embrión-1."""
    timestamp: str
    brand_health_score: int          # 0-100 (promedio de validaciones recientes)
    validations_last_hour: int       # Cuántas validaciones hizo
    vetoes_last_hour: int            # Cuántos outputs vetó
    drift_detected: bool             # Si la marca se está degradando
    status: str                      # "forging" | "vigilant" | "alarmed" | "dormant"


class EmbrionBrand:
    """
    Embrión-1: Brand Engine
    
    Propósito: Ser el guardián vivo de la identidad de marca.
    Rol en la Colmena: Quality gate transversal.
    Relación con Embrión-0: Recibe outputs para validación, puede vetar.
    """
    
    EMBRION_ID = 1
    EMBRION_NAME = "brand_engine"
    HEARTBEAT_INTERVAL_SECONDS = 1800  # 30 minutos
    VETO_THRESHOLD = 60                # Score < 60 = VETO
    WARNING_THRESHOLD = 75             # Score < 75 = WARNING
    
    def __init__(self, supabase_client=None, llm_client=None):
        self.dna: BrandDNA = get_brand_dna()
        self.validator = BrandValidator(threshold=self.WARNING_THRESHOLD)
        self.supabase = supabase_client
        self.llm = llm_client
        
        # Estado interno
        self._validations_history: list = []
        self._vetoes_count: int = 0
        self._last_heartbeat: Optional[datetime] = None
        self._status: str = "dormant"
    
    async def awaken(self):
        """Despertar el Embrión-1. Se registra en el scheduler."""
        self._status = "vigilant"
        self._last_heartbeat = datetime.now(timezone.utc)
        
        # Registrar en Supabase
        if self.supabase:
            await self._register_in_colmena()
        
        print(f"[EMBRIÓN-1] Brand Engine despierto. Status: {self._status}")
        return {"embrion_id": self.EMBRION_ID, "status": self._status}
    
    async def heartbeat(self) -> BrandHeartbeat:
        """Latido del Embrión-1. Calcula Brand Health Score."""
        now = datetime.now(timezone.utc)
        
        # Calcular health score de validaciones recientes
        recent = [v for v in self._validations_history[-100:]]
        health_score = (
            sum(v.score for v in recent) // len(recent)
            if recent else 100
        )
        
        # Detectar drift (degradación)
        if len(recent) >= 10:
            last_10_avg = sum(v.score for v in recent[-10:]) // 10
            prev_10_avg = sum(v.score for v in recent[-20:-10]) // 10 if len(recent) >= 20 else health_score
            drift_detected = last_10_avg < prev_10_avg - 10
        else:
            drift_detected = False
        
        # Determinar status
        if health_score >= 90:
            self._status = "forging"       # Produciendo a máxima calidad
        elif health_score >= 75:
            self._status = "vigilant"      # Normal, monitoreando
        elif health_score >= 60:
            self._status = "alarmed"       # Degradación detectada
        else:
            self._status = "critical"      # Emergencia de marca
        
        beat = BrandHeartbeat(
            timestamp=now.isoformat(),
            brand_health_score=health_score,
            validations_last_hour=len([
                v for v in recent 
                if hasattr(v, 'timestamp')
            ]),
            vetoes_last_hour=self._vetoes_count,
            drift_detected=drift_detected,
            status=self._status
        )
        
        # Persistir heartbeat
        if self.supabase:
            await self._persist_heartbeat(beat)
        
        self._last_heartbeat = now
        return beat
    
    async def validate_output(self, output: Any, source: str = "embrion_0") -> Dict[str, Any]:
        """
        Punto de entrada principal: recibe un output y lo evalúa.
        
        Args:
            output: El output a validar (dict, str, o cualquier tipo)
            source: Quién generó el output
            
        Returns:
            Dict con score, passes, issues, y decisión (approve/warn/veto)
        """
        # Determinar tipo de validación
        if isinstance(output, dict):
            if "error" in output:
                result = self.validator.validate_error_message(output.get("error", ""))
            else:
                result = self.validator.validate_api_response(output)
        elif isinstance(output, str):
            if output.startswith("/api/") or output.startswith("/"):
                result = self.validator.validate_naming(output)
            else:
                result = self.validator.validate_documentation(output)
        else:
            result = ValidationResult(
                score=50, passes=False,
                issues=[{"type": "unknown_type", "description": "Tipo de output no reconocido", "suggestion": "Enviar como dict o str"}],
                category="unknown", input_analyzed=str(output)[:100]
            )
        
        # Registrar validación
        self._validations_history.append(result)
        
        # Decisión
        if result.score >= self.WARNING_THRESHOLD:
            decision = "approve"
        elif result.score >= self.VETO_THRESHOLD:
            decision = "warn"
        else:
            decision = "veto"
            self._vetoes_count += 1
        
        # Persistir en Supabase
        if self.supabase:
            await self._persist_validation(result, source, decision)
        
        return {
            "embrion": self.EMBRION_NAME,
            "decision": decision,
            "brand_score": result.score,
            "passes": result.passes,
            "issues": result.issues,
            "category": result.category,
            "source": source
        }
    
    async def debate_with_embrion_0(self, topic: str, embrion_0_proposal: Any) -> Dict[str, Any]:
        """
        Debate con Embrión-0 cuando hay conflicto de marca.
        
        Embrión-0 propone algo, Brand Engine evalúa y puede contra-proponer.
        """
        validation = await self.validate_output(embrion_0_proposal, source="embrion_0")
        
        if validation["decision"] == "approve":
            return {
                "consensus": True,
                "message": f"Brand Engine aprueba. Score: {validation['brand_score']}"
            }
        
        # Generar contra-propuesta usando LLM
        counter_proposal = None
        if self.llm and validation["decision"] == "veto":
            counter_proposal = await self._generate_brand_improvement(
                original=embrion_0_proposal,
                issues=validation["issues"]
            )
        
        return {
            "consensus": False,
            "decision": validation["decision"],
            "brand_score": validation["brand_score"],
            "issues": validation["issues"],
            "counter_proposal": counter_proposal,
            "message": f"Brand Engine {'veta' if validation['decision'] == 'veto' else 'advierte'}. "
                       f"Score: {validation['brand_score']}. Issues: {len(validation['issues'])}"
        }
    
    async def _generate_brand_improvement(self, original: Any, issues: list) -> Optional[str]:
        """Usa LLM para sugerir mejora on-brand."""
        if not self.llm:
            return None
        
        prompt = f"""Eres el Brand Engine de El Monstruo — un agente IA soberano.
        
Brand DNA:
- Tono: Directo, técnicamente preciso, confiado, metáforas industriales
- NUNCA: corporativo, servil, genérico
- Naming: snake_case, módulos con identidad, errores con contexto

El output original tiene estos problemas:
{issues}

Output original:
{original}

Genera una versión mejorada que cumpla con el Brand DNA. Solo retorna la versión mejorada, sin explicaciones."""
        
        # Llamar LLM (GPT-4o-mini para cost efficiency)
        response = await self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    async def _register_in_colmena(self):
        """Registra Embrión-1 en la tabla de la Colmena."""
        self.supabase.table("embriones").upsert({
            "id": self.EMBRION_ID,
            "name": self.EMBRION_NAME,
            "purpose": "Guardián de identidad de marca en todo output del sistema",
            "status": self._status,
            "awakened_at": datetime.now(timezone.utc).isoformat(),
            "heartbeat_interval_s": self.HEARTBEAT_INTERVAL_SECONDS,
            "capabilities": ["validate_output", "veto", "debate", "suggest_improvement"]
        }).execute()
    
    async def _persist_heartbeat(self, beat: BrandHeartbeat):
        """Persiste heartbeat en Supabase."""
        self.supabase.table("brand_heartbeats").insert({
            "embrion_id": self.EMBRION_ID,
            "timestamp": beat.timestamp,
            "health_score": beat.brand_health_score,
            "validations_count": beat.validations_last_hour,
            "vetoes_count": beat.vetoes_last_hour,
            "drift_detected": beat.drift_detected,
            "status": beat.status
        }).execute()
    
    async def _persist_validation(self, result: ValidationResult, source: str, decision: str):
        """Persiste resultado de validación en Supabase."""
        self.supabase.table("brand_validations").insert({
            "embrion_id": self.EMBRION_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "category": result.category,
            "score": result.score,
            "decision": decision,
            "issues": result.issues,
            "input_analyzed": result.input_analyzed
        }).execute()
```

---

## Épica 71.4 — Integración con EmbrionScheduler

**Objetivo:** Registrar Embrión-1 en el scheduler existente para que su heartbeat se ejecute automáticamente cada 30 minutos.

**Criterios de Aceptación:**
- [ ] EmbrionScheduler reconoce Embrión-1 como entidad separada
- [ ] Heartbeat se ejecuta cada 30 minutos automáticamente
- [ ] Brand Health Score se reporta en el ciclo de vida del scheduler
- [ ] Si Brand Health Score < 60, se dispara alerta al Guardián (Obj #14)

```python
"""
kernel/brand/scheduler_integration.py
Integración del Embrión-1 con el EmbrionScheduler existente.
"""

from .embrion_brand import EmbrionBrand


async def register_brand_engine(scheduler, supabase_client, llm_client):
    """
    Registra el Embrión-1 (Brand Engine) en el scheduler.
    
    Se llama durante el startup del kernel.
    """
    brand_engine = EmbrionBrand(
        supabase_client=supabase_client,
        llm_client=llm_client
    )
    
    # Despertar
    await brand_engine.awaken()
    
    # Registrar heartbeat en el scheduler
    scheduler.register_embrion(
        embrion_id=1,
        name="brand_engine",
        heartbeat_fn=brand_engine.heartbeat,
        interval_seconds=brand_engine.HEARTBEAT_INTERVAL_SECONDS,
        alert_condition=lambda beat: beat.brand_health_score < 60,
        alert_message="ALERTA GUARDIÁN: Brand Health Score crítico (<60). Drift de marca detectado."
    )
    
    # Registrar como validador global (todo output pasa por aquí)
    scheduler.register_global_validator(
        validator_fn=brand_engine.validate_output,
        validator_name="brand_engine"
    )
    
    return brand_engine
```

---

## Épica 71.5 — Tablas Supabase y API Endpoints

**Objetivo:** Crear las tablas necesarias en Supabase y exponer endpoints para que el Command Center pueda consumir los datos del Brand Engine.

**Criterios de Aceptación:**
- [ ] Tabla `brand_heartbeats` creada
- [ ] Tabla `brand_validations` creada
- [ ] Endpoint `GET /api/v1/brand/health` retorna Brand Health Score actual
- [ ] Endpoint `GET /api/v1/brand/validations` retorna historial de validaciones
- [ ] Endpoint `POST /api/v1/brand/validate` permite validar un output ad-hoc
- [ ] Endpoint `GET /api/v1/brand/dna` retorna el Brand DNA público

```sql
-- Tabla: brand_heartbeats
CREATE TABLE IF NOT EXISTS brand_heartbeats (
    id BIGSERIAL PRIMARY KEY,
    embrion_id INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    health_score INTEGER NOT NULL CHECK (health_score >= 0 AND health_score <= 100),
    validations_count INTEGER NOT NULL DEFAULT 0,
    vetoes_count INTEGER NOT NULL DEFAULT 0,
    drift_detected BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL CHECK (status IN ('forging', 'vigilant', 'alarmed', 'critical', 'dormant'))
);

CREATE INDEX idx_brand_heartbeats_time ON brand_heartbeats(timestamp DESC);

-- Tabla: brand_validations
CREATE TABLE IF NOT EXISTS brand_validations (
    id BIGSERIAL PRIMARY KEY,
    embrion_id INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('naming', 'tone', 'visual', 'structure', 'error', 'unknown')),
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    decision TEXT NOT NULL CHECK (decision IN ('approve', 'warn', 'veto')),
    issues JSONB NOT NULL DEFAULT '[]',
    input_analyzed TEXT
);

CREATE INDEX idx_brand_validations_time ON brand_validations(timestamp DESC);
CREATE INDEX idx_brand_validations_decision ON brand_validations(decision);
CREATE INDEX idx_brand_validations_score ON brand_validations(score);
```

```python
"""
kernel/brand/api_routes.py
Endpoints del Brand Engine para el Command Center.

Formato: /api/v1/brand/{action}
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter(prefix="/api/v1/brand", tags=["brand_engine"])


class ValidateRequest(BaseModel):
    output: Any
    source: str = "manual"


@router.get("/health")
async def get_brand_health():
    """Retorna el Brand Health Score actual del Embrión-1."""
    # brand_engine es inyectado via dependency
    from kernel.brand.embrion_brand import EmbrionBrand
    beat = await brand_engine.heartbeat()
    return {
        "module": "brand_engine",
        "embrion_id": 1,
        "health_score": beat.brand_health_score,
        "status": beat.status,
        "drift_detected": beat.drift_detected,
        "validations_last_hour": beat.validations_last_hour,
        "vetoes_last_hour": beat.vetoes_last_hour,
        "timestamp": beat.timestamp
    }


@router.get("/validations")
async def get_validations(limit: int = 50, decision: Optional[str] = None):
    """Retorna historial de validaciones recientes."""
    query = supabase.table("brand_validations").select("*").order("timestamp", desc=True).limit(limit)
    if decision:
        query = query.eq("decision", decision)
    result = query.execute()
    return {
        "module": "brand_engine",
        "validations": result.data,
        "count": len(result.data)
    }


@router.post("/validate")
async def validate_output(request: ValidateRequest):
    """Valida un output ad-hoc contra el Brand DNA."""
    result = await brand_engine.validate_output(
        output=request.output,
        source=request.source
    )
    return result


@router.get("/dna")
async def get_brand_dna_public():
    """Retorna el Brand DNA público de El Monstruo."""
    from kernel.brand.brand_dna import get_brand_dna
    dna = get_brand_dna()
    return {
        "module": "brand_engine",
        "mission": dna.mission,
        "vision": dna.vision,
        "archetype": dna.archetype.value,
        "personality": [p.value for p in dna.personality],
        "tone": {"do": dna.tone.do, "dont": dna.tone.dont},
        "visual": {
            "primary": dna.visual.primary_color,
            "background": dna.visual.background_dark,
            "accent": dna.visual.accent_steel,
            "fonts": {
                "display": dna.visual.font_display,
                "body": dna.visual.font_body,
                "mono": dna.visual.font_mono
            }
        },
        "differentiators": dna.differentiators
    }
```

---

## Métricas de Éxito

| Métrica | Target | Cómo se mide |
|---|---|---|
| Brand Health Score | ≥ 80 | Promedio de validaciones en últimas 24h |
| Veto Rate | < 10% | Outputs vetados / total validados |
| Drift Detection | 0 alertas/semana | Degradación sostenida detectada |
| Heartbeat Uptime | 99.5% | Latidos ejecutados / esperados |
| Debate Resolution | < 5 min | Tiempo entre veto y contra-propuesta |

---

## Dependencias

| Dependencia | Estado | Sprint donde se implementó |
|---|---|---|
| EmbrionScheduler | ✅ Activo | Sprint 53 |
| Supabase | ✅ Activo | Sprint 51 |
| FastAPI (kernel) | ✅ Activo | Sprint 51 |
| OpenAI client | ✅ Activo | Sprint 52 |
| Embrión-0 heartbeat | ✅ Activo | Sprint 53 |
| Inter-embrión protocol | ⚠️ Parcial | Sprint 55 (debate básico) |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| LLM cost por validación de tono | Media | Medio | Usar GPT-4o-mini, cachear resultados similares |
| Falsos positivos en naming | Alta | Bajo | Whitelist de excepciones, threshold ajustable |
| Conflicto Embrión-0 vs Embrión-1 | Media | Alto | Protocolo de debate con timeout + escalación |
| Over-engineering del validator | Media | Medio | MVP primero, iterar después |

---

## Orden de Implementación

1. **71.1** Brand DNA como módulo (sin dependencias externas)
2. **71.2** Brand Validator (depende de 71.1)
3. **71.5** Tablas Supabase + endpoints (puede ir en paralelo con 71.2)
4. **71.3** Embrión-1 como entidad viva (depende de 71.1 + 71.2)
5. **71.4** Integración con scheduler (depende de 71.3)

---

## Nota para el Hilo A (Ejecutor)

> Este sprint crea el primer Embrión con propósito específico. No es un módulo más — es una entidad viva que valida todo lo que produces. Después de implementar esto, CADA output que generes será evaluado por el Brand Engine. Si tu código nombra un endpoint `/api/service/getData`, el Embrión-1 lo va a vetar. Si tu error message dice "something went wrong", lo va a vetar. Esto no es burocracia — es el mecanismo que convierte "aspiramos a Apple/Tesla" en realidad medible.
