"""
El Catastro — Schema Pydantic de las 5 tablas Supabase.

Espejo Python del SQL en scripts/016_sprint86_catastro_schema.sql.
Mantener AMBOS sincronizados — si cambia el SQL, actualizar este módulo
y el test de integridad en tests/test_sprint86_schema.py.

Sprint 86 Bloque 1 — [Hilo Manus Catastro] — 2026-05-04.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS — espejo de los CHECK CONSTRAINTS del SQL
# ============================================================================

class EstadoModelo(str, Enum):
    PRODUCTION = "production"
    BETA = "beta"
    OPEN_SOURCE = "open-source"
    DEPRECATED = "deprecated"
    ALPHA = "alpha"
    PREVIEW = "preview"


class TipoLicencia(str, Enum):
    PROPIETARIO = "propietario"
    OPEN_WEIGHTS = "open-weights"
    OPEN_WEIGHTS_RESTRICTED = "open-weights-restricted"
    OPEN_SOURCE_MIT = "open-source-mit"
    OPEN_SOURCE_APACHE = "open-source-apache"


class Macroarea(str, Enum):
    """
    Sprint 86 = solo INTELIGENCIA. Sprints 87+ amplían.
    """
    INTELIGENCIA = "inteligencia"
    VISION_GENERATIVA = "vision_generativa"  # Sprint 87
    AGENTES = "agentes"                      # Sprint 88
    # macroáreas futuras: voz, datos, infraestructura, seguridad, etc.


class DominioInteligencia(str, Enum):
    """Dominios dentro de Macroarea INTELIGENCIA (Sprint 86)."""
    LLM_FRONTIER = "llm_frontier"
    LLM_OPEN_SOURCE = "llm_open_source"
    CODING_LLMS = "coding_llms"
    SMALL_EDGE = "small_edge"


class PrioridadEvento(str, Enum):
    CRITICO = "critico"
    IMPORTANTE = "importante"
    INFO = "info"


class TipoEvento(str, Enum):
    TOP3_CHANGE = "top3_change"
    DEPRECATION = "deprecation"
    PRICE_CHANGE = "price_change"
    NEW_MODEL = "new_model"
    CVE = "cve"
    MODEL_DRIFT_DETECTED = "model_drift_detected"  # Addendum 002 decisión 3
    QUORUM_FAILED = "quorum_failed"
    SOURCE_DOWN = "source_down"


class RolCurador(str, Enum):
    CURADOR = "curador"      # propone valores
    VALIDADOR = "validador"  # confirma o rechaza valores propuestos
    ARBITRO = "arbitro"      # desempata cuando 2 validadores discrepan


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class FuenteEvidencia(BaseModel):
    """
    Una entrada del array `fuentes_evidencia` JSONB.
    Citation tracking obligatorio anti-alucinación (Addendum 001 cambio 1).
    """
    url: str
    fetched_at: datetime
    payload_hash: str = Field(..., min_length=8, description="SHA-256 truncado del payload original")
    curador: str = Field(..., description="ID del curador que extrajo el dato (ej. 'claude-opus-4.7-inteligencia')")
    tipo_dato: str = Field(..., description="Qué dato específico extrajo de esta fuente (ej. 'precio_input', 'quality_score')")


class CatastroModelo(BaseModel):
    """
    Tabla 1: catastro_modelos — fuente de verdad viva.
    """
    # Identidad
    id: str = Field(..., min_length=2, max_length=100, description="slug ej. 'gpt-5-5-mini'")
    nombre: str
    proveedor: str

    # Taxonomía
    macroarea: Macroarea = Macroarea.INTELIGENCIA
    dominios: list[str] = Field(default_factory=list)
    subcapacidades: list[str] = Field(default_factory=list)

    # Estado
    estado: EstadoModelo = EstadoModelo.PRODUCTION
    tipo: TipoLicencia = TipoLicencia.PROPIETARIO
    licencia: Optional[str] = None
    open_weights: bool = False
    api_endpoint: Optional[str] = None

    # Métricas Trono
    quality_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    quality_delta: Optional[float] = None
    cost_efficiency: Optional[float] = Field(None, ge=0.0, le=100.0)
    speed_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    reliability_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    brand_fit: Optional[float] = Field(None, ge=0.0, le=1.0)
    sovereignty: Optional[float] = Field(None, ge=0.0, le=1.0)
    velocity: Optional[float] = Field(None, ge=0.0, le=1.0)

    trono_global: Optional[float] = Field(None, ge=0.0, le=100.0)
    trono_delta: Optional[float] = None
    rank_dominio: Optional[int] = Field(None, ge=1)

    # Comerciales
    precio_input_per_million: Optional[float] = Field(None, ge=0.0)
    precio_output_per_million: Optional[float] = Field(None, ge=0.0)

    # Datos extensibles
    capacidades_tecnicas: dict[str, Any] = Field(default_factory=dict)
    velocidad: dict[str, Any] = Field(default_factory=dict)
    limitaciones: list[str] = Field(default_factory=list)
    fortalezas: list[str] = Field(default_factory=list)
    debilidades: list[str] = Field(default_factory=list)
    casos_uso_recomendados_monstruo: list[str] = Field(default_factory=list)

    # Citation tracking
    fuentes_evidencia: list[FuenteEvidencia] = Field(default_factory=list)
    quorum_alcanzado: bool = False
    confidence: float = Field(0.50, ge=0.0, le=1.0)
    curador_responsable: Optional[str] = None

    # Embedding (no se serializa al SQL desde aquí — se genera por separado)
    embedding: Optional[list[float]] = Field(None, exclude=True)

    # Extensibilidad
    data_extra: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = 1

    # Audit
    ultima_validacion: datetime = Field(default_factory=datetime.utcnow)
    proxima_revalidacion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("id")
    @classmethod
    def slug_format(cls, v: str) -> str:
        """slug debe ser kebab-case, sin espacios ni mayúsculas."""
        if v != v.lower():
            raise ValueError(f"id debe ser lowercase: {v!r}")
        if " " in v or "_" in v:
            raise ValueError(f"id debe usar guiones (-), no espacios ni underscores: {v!r}")
        return v

    @field_validator("dominios")
    @classmethod
    def dominios_no_vacios(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("dominios no puede estar vacío — al menos un dominio requerido")
        return v


class CatastroHistorial(BaseModel):
    """Tabla 2: catastro_historial — snapshots diarios."""
    fecha: date
    modelo_id: str
    snapshot: dict[str, Any]
    trono_global: Optional[float] = None
    rank_dominio: Optional[int] = None


class CatastroEvento(BaseModel):
    """Tabla 3: catastro_eventos — alertas y feed."""
    id: UUID = Field(default_factory=uuid4)
    fecha: datetime = Field(default_factory=datetime.utcnow)
    tipo: TipoEvento
    prioridad: PrioridadEvento = PrioridadEvento.INFO
    modelo_id: Optional[str] = None
    descripcion: str
    contexto: dict[str, Any] = Field(default_factory=dict)
    notificado: bool = False
    curador_origen: Optional[str] = None


class CatastroNota(BaseModel):
    """Tabla 4: catastro_notas — anotaciones humanas / agentes."""
    id: UUID = Field(default_factory=uuid4)
    modelo_id: str
    autor: str
    contenido: str
    caso_uso: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    fecha: datetime = Field(default_factory=datetime.utcnow)


class CatastroCurador(BaseModel):
    """Tabla 5: catastro_curadores — Trust Score por LLM curador."""
    id: str = Field(..., description="ej. 'claude-opus-4.7-inteligencia'")
    macroarea: Macroarea
    modelo_llm: str
    proveedor: str
    rol: RolCurador = RolCurador.CURADOR
    trust_score: float = Field(1.00, ge=0.0, le=1.0)
    total_validaciones: int = Field(0, ge=0)
    aciertos_quorum: int = Field(0, ge=0)
    fallos_quorum: int = Field(0, ge=0)
    requiere_hitl: bool = False
    last_run: Optional[datetime] = None
    notas: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("requiere_hitl")
    @classmethod
    def hitl_consistency(cls, v: bool, info) -> bool:
        """Si trust_score < 0.70 → requiere_hitl debe ser True (consistencia con SQL trigger futuro)."""
        # Pydantic v2: info.data tiene los campos ya validados
        trust = info.data.get("trust_score") if info.data else None
        if trust is not None and trust < 0.70 and not v:
            # Auto-corrige en lugar de fallar — el sistema debe ser tolerante
            return True
        return v
