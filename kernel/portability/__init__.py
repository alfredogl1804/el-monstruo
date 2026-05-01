"""kernel/portability — Data Portability Engine (Sprint 62.2)"""
from kernel.portability.portability_engine import (
    PortabilityEngine,
    DataExporter,
    DataImporter,
    ExportResult,
    ImportResult,
    ExportacionFallida,
    ImportacionFallida,
    ManifiestoInvalido,
    get_portability_engine,
    init_portability_engine,
    EXPORT_VERSION,
    EXPORT_TABLES,
)

__all__ = [
    "PortabilityEngine", "DataExporter", "DataImporter",
    "ExportResult", "ImportResult",
    "ExportacionFallida", "ImportacionFallida", "ManifiestoInvalido",
    "get_portability_engine", "init_portability_engine",
    "EXPORT_VERSION", "EXPORT_TABLES",
]
