"""kernel/portability — Data Portability Engine (Sprint 62.2)"""

from kernel.portability.portability_engine import (
    EXPORT_TABLES,
    EXPORT_VERSION,
    DataExporter,
    DataImporter,
    ExportacionFallida,
    ExportResult,
    ImportacionFallida,
    ImportResult,
    ManifiestoInvalido,
    PortabilityEngine,
    get_portability_engine,
    init_portability_engine,
)

__all__ = [
    "PortabilityEngine",
    "DataExporter",
    "DataImporter",
    "ExportResult",
    "ImportResult",
    "ExportacionFallida",
    "ImportacionFallida",
    "ManifiestoInvalido",
    "get_portability_engine",
    "init_portability_engine",
    "EXPORT_VERSION",
    "EXPORT_TABLES",
]
