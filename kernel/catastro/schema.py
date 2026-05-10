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


class ConfidentialityTier(str, Enum):
    """
    Sprint 86.8 - Tier de sensibilidad por modelo del Catastro.
    Habilita filtrado de candidatos por sensibilidad del prompt entrante (SMP).

    Orden semantico (de mas estricto a mas permisivo):
        local_only < tee_capable < cloud_anonymized_ok < cloud_only

    Spec: bridge/sprint_86_8_preinvestigation/spec_catastro_confidentiality_tier.md
    """
    LOCAL_ONLY = "local_only"                    # corre on-device
    TEE_CAPABLE = "tee_capable"                  # confidential computing
    CLOUD_ANONYMIZED_OK = "cloud_anonymized_ok"  # acepta prompts anonimizados
    CLOUD_ONLY = "cloud_only"                    # default conservador


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

    # Confidentiality (Sprint 86.8)
    confidentiality_tier: ConfidentialityTier = Field(
        default=ConfidentialityTier.CLOUD_ONLY,
        description="Tier de sensibilidad para filtrado SMP. Default conservador cloud_only.",
    )

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


# ============================================================================
# Sprint 88 - Macroarea AGENTES (DSC-G-007.2, DSC-MO-009)
# Migraciones SQL: 030_sprint88_catastro_agentes.sql + 031_sprint88_dominios_expandidos.sql
# ============================================================================

class DominioAgentes(str, Enum):
    """
    9 dominios canonicos dentro de Macroarea AGENTES.

    5 originales (Sprint 88 v1):
    - AGENTES_DESARROLLO: developer-pro IDEs/CLIs (Manus, Cowork, Claude Code, Codex, Cursor, Devin...)
    - AGENTES_INVESTIGACION: research/browser (Perplexity, Comet, Deep Research...)
    - AGENTES_EJECUTORES: workflow automation (n8n, Zapier, Lindy, Gumloop...)
    - AGENTES_MULTI_SWARM: orquestadores frameworks (LangGraph, CrewAI, AutoGen...)
    - INTERFACES_USUARIO: apps consumer general (ChatGPT Pro, Claude.ai, Gemini App)

    4 expandidos (Sprint 88 v2 - DSC-G-007.2):
    - AGENTES_VIBE_CODING: no-code/low-code app builders (Replit Agent, Lovable, Bolt, V0...)
    - AGENTES_CREACION_AUDIOVISUAL: cine/video largo + SFX/musica (Sora, Veo, Runway, Higgsfield, Suno, Udio...)
    - AGENTES_BRANDING_DISENO: logos/marca/identidad visual (Ideogram, Recraft, Looka, Kittl...)
    - AGENTES_MARKETING_VENTAS: pauta/leads/copy/outreach (Apollo, Clay, Agentforce, Sierra, Harvey, Jasper...)
    """
    # Originales
    AGENTES_DESARROLLO = "agentes_desarrollo"
    AGENTES_INVESTIGACION = "agentes_investigacion"
    AGENTES_EJECUTORES = "agentes_ejecutores"
    AGENTES_MULTI_SWARM = "agentes_multi_swarm"
    INTERFACES_USUARIO = "interfaces_usuario"
    # Expandidos Sprint 88 v2
    AGENTES_VIBE_CODING = "agentes_vibe_coding"
    AGENTES_CREACION_AUDIOVISUAL = "agentes_creacion_audiovisual"
    AGENTES_BRANDING_DISENO = "agentes_branding_diseno"
    AGENTES_MARKETING_VENTAS = "agentes_marketing_ventas"
    # Sprint 88.2 - migracion 038 (consenso 4 sabios)
    AGENTES_GENERALISTAS_AUTONOMOS = "agentes_generalistas_autonomos"
    AGENTES_SEGURIDAD = "agentes_seguridad"
    AGENTES_OBSERVABILIDAD_EVALS = "agentes_observabilidad_evals"


class PersistenciaMemoria(str, Enum):
    """Capacidad de persistencia entre sesiones del agente."""
    NONE = "none"
    SESSION = "session"
    PERSISTENT = "persistent"
    EXTERNAL_DB = "external_db"


class CostoPorUsoTipico(str, Enum):
    """Bucket de costo por uso tipico (subjetivo, snapshot 2026-05-10)."""
    GRATIS = "gratis"
    BAJO = "bajo"          # < $20/mes o < $0.50/run
    MEDIO = "medio"        # $20-100/mes o $0.50-5/run
    ALTO = "alto"          # $100-500/mes o $5-50/run
    ENTERPRISE = "enterprise"  # > $500/mes o pricing on-demand


class CatastroAgente(BaseModel):
    """
    Tabla: catastro_agentes - macroarea AGENTES del Catastro (Sprint 88).

    Productos/sustratos completos clasificados por dominio. Distinto de
    `CatastroModelo` (LLM puro): agrega capas de ejecucion (sandbox, fs,
    internet, multi-step, multi-swarm) y FK opcional al LLM base.

    Cruza con DSC-MO-009 (arsenal seleccionable por Catastro) y
    DSC-G-007.2 (Macroarea AGENTES con 9 dominios canonizados).
    """
    # Identidad
    id: str = Field(..., min_length=2, max_length=100, description="slug ej. 'manus', 'claude-cowork'")
    nombre: str
    proveedor: str

    # Taxonomia
    macroarea: Macroarea = Macroarea.AGENTES
    dominio: DominioAgentes
    subcapacidades: list[str] = Field(default_factory=list)

    # LLM base (opcional)
    llm_base_id: Optional[str] = Field(
        None,
        description="FK a catastro_modelos.id - LLM principal que envuelve. NULL si agnostico de LLM.",
    )
    llm_bases_alternativos: list[str] = Field(default_factory=list)

    # Dimensiones tecnicas booleanas
    tiene_sandbox: bool = False
    acceso_filesystem: bool = False
    acceso_internet: bool = False
    multi_step_capable: bool = False
    multi_swarm_capable: bool = False

    # Persistencia
    persistencia_memoria: PersistenciaMemoria = PersistenciaMemoria.NONE

    # Tools y casos de uso
    tools_nativas: list[str] = Field(default_factory=list)
    casos_de_uso_primarios: list[str] = Field(default_factory=list)

    # Performance / costo
    costo_por_uso_tipico: Optional[CostoPorUsoTipico] = None
    latencia_tipica_segundos: Optional[int] = Field(None, ge=0)

    # Estado
    estado: EstadoModelo = EstadoModelo.PRODUCTION
    open_weights: bool = False
    api_endpoint: Optional[str] = None

    # Metricas Trono AGENTES (formula: 0.30*CT + 0.25*A + 0.20*E + 0.15*I + 0.10*CE)
    capacidad_tecnica: Optional[float] = Field(None, ge=0.0, le=100.0)
    adopcion_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    estabilidad_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    integracion_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    costo_eficiencia_score: Optional[float] = Field(None, ge=0.0, le=100.0)

    trono_dominio: Optional[float] = Field(None, ge=0.0, le=100.0)
    trono_delta: Optional[float] = None
    rank_dominio: Optional[int] = Field(None, ge=1)

    # Datos extensibles
    fortalezas: list[str] = Field(default_factory=list)
    debilidades: list[str] = Field(default_factory=list)
    limitaciones: list[str] = Field(default_factory=list)

    # Citation tracking obligatorio (DSC-G-007.1)
    fuentes_evidencia: list[FuenteEvidencia] = Field(default_factory=list)
    quorum_alcanzado: bool = False
    confidence: float = Field(0.50, ge=0.0, le=1.0)
    curador_responsable: Optional[str] = None
    validacion_adversarial: dict[str, Any] = Field(
        default_factory=dict,
        description="Resultado validacion adversarial DSC-G-007.1: {sabios, acuerdo_pct, discrepancias}",
    )

    # Tier de seed (DSC-G-007.3 - escalonamiento de profundidad)
    tier_seed: int = Field(1, ge=1, le=2, description="1=validacion profunda 3 sabios, 2=validacion ligera 1 sabio")

    # Bonus curador (DSC-G-007.4 + DSC-G-007.5 - desempates documentados, rango 0-50)
    bonus_curador: int = Field(0, ge=0, le=50, description="Bonus aditivo (0-50) en desempates de tronos. Requiere bonus_curador_razon.")
    bonus_curador_razon: Optional[str] = None

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
        if v != v.lower():
            raise ValueError(f"id debe ser lowercase: {v!r}")
        if " " in v or "_" in v:
            raise ValueError(f"id debe usar guiones (-), no espacios ni underscores: {v!r}")
        return v

    @field_validator("multi_swarm_capable")
    @classmethod
    def swarm_implies_multistep(cls, v: bool, info) -> bool:
        """Invariante: multi_swarm_capable=True implica multi_step_capable=True (espejo del CHECK SQL)."""
        if v:
            multi_step = info.data.get("multi_step_capable") if info.data else None
            if multi_step is False:
                raise ValueError(
                    "Invariante violado: multi_swarm_capable=True requiere multi_step_capable=True"
                )
        return v



# ============================================================================
# Sprint 88.3 - Macroarea VISION_GENERATIVA (DSC-G-007.5)
# Migraciones SQL: 040..045 (catastro_vision_generativa + 12 subdominios + 38 seeds)
# ============================================================================

class SubdominioVisionGenerativa(str, Enum):
    """12 subdominios canonicos VISION_GENERATIVA validados por Perplexity."""
    IMAGEN_ESTATICA_PREMIUM = "imagen_estatica_premium"
    VIDEO_CLIP_GENERATIVO = "video_clip_generativo"
    VIDEO_NARRATIVO_CINEMATICO = "video_narrativo_cinematico"
    AVATAR_HUMANO_ANIMADO = "avatar_humano_animado"
    REALTIME_VIDEO_AGENTS_CHARACTERS = "realtime_video_agents_characters"
    LIP_SYNC_VISUAL_DUBBING = "lip_sync_visual_dubbing"
    TTS_VOCES_SINTETICAS = "tts_voces_sinteticas"
    MUSICA_GENERADA = "musica_generada"
    EFECTOS_SONIDO_SFX = "efectos_sonido_sfx"
    GENERATIVE_EDITING_INPAINTING = "generative_editing_inpainting"
    UPSCALING_RESTAURACION_ENHANCEMENT = "upscaling_restauracion_enhancement"
    THREE_D_MOCAP_ASSETS = "3d_mocap_assets"


class LicensingRisk(str, Enum):
    """Riesgo de licenciamiento de outputs (DSC-G-007.5)."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CatastroVisionGenerativa(BaseModel):
    """
    Tabla: catastro_vision_generativa - macroarea VISION_GENERATIVA (Sprint 88.3).
    Espejo Pydantic de migracion 040 + 12 subdominios + 38 seeds.
    """
    # Identidad
    id: str = Field(..., min_length=2, max_length=100)
    nombre: str
    proveedor: str

    # Taxonomia
    macroarea: Macroarea = Macroarea.VISION_GENERATIVA
    subdominio_primario: SubdominioVisionGenerativa
    subdominios_secundarios: list[SubdominioVisionGenerativa] = Field(default_factory=list)
    url_oficial: Optional[str] = None

    # Capacidades tecnicas especificas
    modalidad_input: list[str] = Field(default_factory=list)
    modalidad_output: list[str] = Field(default_factory=list)
    duracion_max_clip_sec: Optional[int] = Field(None, ge=0)
    resolucion_max: Optional[str] = None
    audio_nativo: bool = False
    multi_shot_capable: bool = False
    consistencia_personaje: bool = False
    api_disponible: bool = False
    mcp_server_disponible: bool = False

    # Doctrina + cumplimiento
    licensing_risk: LicensingRisk = LicensingRisk.LOW
    consent_required: bool = False
    c2pa_provenance: bool = False
    watermark_native: bool = False

    # Estado
    estado: EstadoModelo = EstadoModelo.PRODUCTION
    costo_por_uso_tipico: Optional[CostoPorUsoTipico] = None
    open_weights: bool = False

    # Curaduria + scoring
    tier_seed: int = Field(1, ge=1, le=2)
    bonus_curador: int = Field(0, ge=0, le=50)
    bonus_curador_razon: Optional[str] = None
    score_subdominio_origen: Optional[int] = Field(None, ge=0, le=100)
    riesgo_adversarial: Optional[str] = None

    # Validacion
    fuentes_evidencia: list[FuenteEvidencia] = Field(default_factory=list)
    validacion_adversarial: dict[str, Any] = Field(default_factory=dict)
    data_extra: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(0.50, ge=0.0, le=1.0)

    # Timestamps
    schema_version: int = 1
    ultima_validacion: datetime = Field(default_factory=datetime.utcnow)
    proxima_revalidacion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("id")
    @classmethod
    def slug_format_vg(cls, v: str) -> str:
        if v != v.lower():
            raise ValueError(f"id debe ser lowercase: {v!r}")
        if " " in v:
            raise ValueError(f"id no puede contener espacios: {v!r}")
        return v

    @field_validator("subdominios_secundarios")
    @classmethod
    def secundarios_no_incluyen_primario(cls, v: list, info) -> list:
        primario = info.data.get("subdominio_primario") if info.data else None
        if primario is not None and primario in v:
            raise ValueError(f"subdominio_primario {primario} no puede estar tambien en subdominios_secundarios")
        return v
