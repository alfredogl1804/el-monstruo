"""
kernel/catastro/schema_generated.py

GENERADO AUTOMÁTICAMENTE — NO EDITAR A MANO.
Fuente: scripts/016_sprint86_catastro_schema.sql + 018 + 019 + 019.1
Generador: scripts/_gen_catastro_pydantic_from_sql.py

Si necesitás cambiar este archivo:
1. Modificá la migration SQL correspondiente
2. Corré: python3 scripts/_gen_catastro_pydantic_from_sql.py
3. Verificá: python3 scripts/_audit_catastro_schema_drift.py

Doctrina (Mini-Sprint 86.4.5 pre-B2):
- Schema authority único: PostgreSQL DDL es la única fuente de verdad.
- schema.py (manual) está siendo deprecado gradualmente; cuando haya
  divergencia con este archivo, este archivo manda.
- Mappings provistos como `TABLE_COLUMNS` para introspect runtime
  (útil en pre-flight de queries y para detectar drift desde código).

Generado por Hilo Manus · 2026-05-05
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Source hash — para drift detection rápida sin re-parsear
# ============================================================================

__SOURCE_HASH__ = "9e3e4e28375944a2af4bd0bc34e56c07fd7652e88b5df7d024a18416eb1b9790"
__GENERATED_AT__ = "2026-05-05T17:15:40Z"
__MIGRATIONS__ = ['scripts/016_sprint86_catastro_schema.sql', 'scripts/018_sprint86_catastro_rpc.sql', 'scripts/019_sprint86_catastro_trono.sql', 'scripts/019_1_hotfix_validated_by_column.sql', 'scripts/027_sprint86_8_confidentiality_tier_schema.sql']


# ============================================================================
# Pydantic models — uno por tabla
# ============================================================================


class CatastroCuradorRow(BaseModel):
    """Espejo bit-perfect de la tabla `catastro_curadores` (PostgreSQL DDL).

    Generado automáticamente desde las migrations.
    """
    model_config = ConfigDict(extra="ignore")

    id: str
    macroarea: str
    modelo_llm: str
    proveedor: str
    rol: str = Field(default=None)  # SQL default: 'curador'
    trust_score: float = Field(default=None)  # SQL default: 1.00
    total_validaciones: int = Field(default=None)  # SQL default: 0
    aciertos_quorum: int = Field(default=None)  # SQL default: 0
    fallos_quorum: int = Field(default=None)  # SQL default: 0
    requiere_hitl: bool = Field(default=None)  # SQL default: FALSE
    last_run: Optional[datetime] = None
    notas: Optional[str] = None
    created_at: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()
    updated_at: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()
    curator_alias: list[str] = Field(default=None)  # SQL default: '{}'

class CatastroEventoRow(BaseModel):
    """Espejo bit-perfect de la tabla `catastro_eventos` (PostgreSQL DDL).

    Generado automáticamente desde las migrations.
    """
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default=None)  # SQL default: UUID()
    fecha: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()
    tipo: str
    prioridad: str = Field(default=None)  # SQL default: 'info'
    modelo_id: Optional[str] = None
    descripcion: str
    contexto: dict[str, Any] = Field(default=None)  # SQL default: '{}'
    notificado: bool = Field(default=None)  # SQL default: FALSE
    curador_origen: Optional[str] = None

class CatastroHistorialRow(BaseModel):
    """Espejo bit-perfect de la tabla `catastro_historial` (PostgreSQL DDL).

    Generado automáticamente desde las migrations.
    """
    model_config = ConfigDict(extra="ignore")

    fecha: date
    modelo_id: str
    snapshot: dict[str, Any]
    trono_global: Optional[float] = None
    rank_dominio: Optional[int] = None

class CatastroModeloRow(BaseModel):
    """Espejo bit-perfect de la tabla `catastro_modelos` (PostgreSQL DDL).

    Generado automáticamente desde las migrations.
    """
    model_config = ConfigDict(extra="ignore")

    id: str
    nombre: str
    proveedor: str
    macroarea: str
    dominios: list[str] = Field(default=None)  # SQL default: '{}'
    subcapacidades: Optional[list[str]] = None
    estado: str = Field(default=None)  # SQL default: 'production'
    tipo: str = Field(default=None)  # SQL default: 'propietario'
    licencia: Optional[str] = None
    open_weights: bool = Field(default=None)  # SQL default: FALSE
    api_endpoint: Optional[str] = None
    quality_score: Optional[float] = None
    quality_delta: Optional[float] = None
    cost_efficiency: Optional[float] = None
    speed_score: Optional[float] = None
    reliability_score: Optional[float] = None
    brand_fit: Optional[float] = None
    sovereignty: Optional[float] = None
    velocity: Optional[float] = None
    trono_global: Optional[float] = None
    trono_delta: Optional[float] = None
    rank_dominio: Optional[int] = None
    precio_input_per_million: Optional[float] = None
    precio_output_per_million: Optional[float] = None
    capacidades_tecnicas: dict[str, Any] = Field(default=None)  # SQL default: '{}'
    velocidad: dict[str, Any] = Field(default=None)  # SQL default: '{}'
    limitaciones: Optional[list[str]] = None
    fortalezas: Optional[list[str]] = None
    debilidades: Optional[list[str]] = None
    casos_uso_recomendados_monstruo: Optional[list[str]] = None
    fuentes_evidencia: dict[str, Any] = Field(default=None)  # SQL default: '[]'
    quorum_alcanzado: bool = Field(default=None)  # SQL default: FALSE
    confidence: float = Field(default=None)  # SQL default: 0.50
    curador_responsable: Optional[str] = None
    embedding: Optional[list[float]] = None
    data_extra: dict[str, Any] = Field(default=None)  # SQL default: '{}'
    schema_version: int = Field(default=None)  # SQL default: 1
    ultima_validacion: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()
    proxima_revalidacion: Optional[datetime] = None
    created_at: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()
    updated_at: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()
    validated_by: Optional[str] = None
    confidentiality_tier: str = Field(default=None)  # SQL default: 'cloud_only'

class CatastroNotaRow(BaseModel):
    """Espejo bit-perfect de la tabla `catastro_notas` (PostgreSQL DDL).

    Generado automáticamente desde las migrations.
    """
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default=None)  # SQL default: UUID()
    modelo_id: str
    autor: str
    contenido: str
    caso_uso: Optional[str] = None
    rating: Optional[int] = None
    fecha: datetime = Field(default=None)  # SQL default: CURRENT_TIMESTAMP()

# ============================================================================
# Introspección runtime — útil para pre-flight de queries SQL
# ============================================================================

TABLE_COLUMNS: dict[str, list[str]] = {
    "catastro_curadores": ['id', 'macroarea', 'modelo_llm', 'proveedor', 'rol', 'trust_score', 'total_validaciones', 'aciertos_quorum', 'fallos_quorum', 'requiere_hitl', 'last_run', 'notas', 'created_at', 'updated_at', 'curator_alias'],
    "catastro_eventos": ['id', 'fecha', 'tipo', 'prioridad', 'modelo_id', 'descripcion', 'contexto', 'notificado', 'curador_origen'],
    "catastro_historial": ['fecha', 'modelo_id', 'snapshot', 'trono_global', 'rank_dominio'],
    "catastro_modelos": ['id', 'nombre', 'proveedor', 'macroarea', 'dominios', 'subcapacidades', 'estado', 'tipo', 'licencia', 'open_weights', 'api_endpoint', 'quality_score', 'quality_delta', 'cost_efficiency', 'speed_score', 'reliability_score', 'brand_fit', 'sovereignty', 'velocity', 'trono_global', 'trono_delta', 'rank_dominio', 'precio_input_per_million', 'precio_output_per_million', 'capacidades_tecnicas', 'velocidad', 'limitaciones', 'fortalezas', 'debilidades', 'casos_uso_recomendados_monstruo', 'fuentes_evidencia', 'quorum_alcanzado', 'confidence', 'curador_responsable', 'embedding', 'data_extra', 'schema_version', 'ultima_validacion', 'proxima_revalidacion', 'created_at', 'updated_at', 'validated_by', 'confidentiality_tier'],
    "catastro_notas": ['id', 'modelo_id', 'autor', 'contenido', 'caso_uso', 'rating', 'fecha'],
}
