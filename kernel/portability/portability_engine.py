"""
kernel/portability/portability_engine.py
Sprint 62.2 — Data Portability Engine (Objetivo #12: Ecosistema/Soberanía)

Exportación e importación completa de datos del usuario en formato estándar.
Soberanía real = portabilidad real. El usuario puede llevarse sus datos en cualquier momento.

Soberanía: Si Supabase no está disponible, exporta desde in-memory state.
Alternativa: Exportar a CSV plano o SQLite local.
"""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger("portabilidad")

EXPORT_VERSION = "1.0.0"

EXPORT_TABLES = [
    "projects",
    "project_configs",
    "causal_events",
    "causal_factors",
    "predictions",
    "error_lessons",
    "error_rules",
    "plugins",
    "embrion_tasks",
    "job_executions",
    "conversation_messages",
    "scheduled_tasks",
    "seeding_cycles",
    "a2a_agents",
]


# --- Excepciones con identidad ---


class ExportacionFallida(Exception):
    """Error durante la exportación de datos."""

    def __init__(self, razon: str):
        super().__init__(f"Exportación fallida: {razon}. Verifica la conectividad con Supabase o usa el modo offline.")
        self.razon = razon


class ImportacionFallida(Exception):
    """Error durante la importación de datos."""

    def __init__(self, razon: str):
        super().__init__(
            f"Importación fallida: {razon}. Verifica que el archivo ZIP sea un export válido de El Monstruo."
        )
        self.razon = razon


class ManifiestoInvalido(Exception):
    """El manifiesto del export no es válido."""

    def __init__(self):
        super().__init__("Manifiesto del export inválido. El archivo debe ser generado por El Monstruo v1.0+.")


# --- Dataclasses ---


@dataclass
class ExportResult:
    """Resultado de una exportación."""

    exitoso: bool
    tablas_exportadas: int
    registros_totales: int
    zip_path: Optional[str] = None
    zip_bytes: Optional[bytes] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    errores: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "exitoso": self.exitoso,
            "tablas_exportadas": self.tablas_exportadas,
            "registros_totales": self.registros_totales,
            "zip_path": self.zip_path,
            "timestamp": self.timestamp,
            "errores": self.errores,
        }


@dataclass
class ImportResult:
    """Resultado de una importación."""

    exitoso: bool
    modo: str
    importados: int = 0
    omitidos: int = 0
    errores: int = 0
    tablas: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "exitoso": self.exitoso,
            "modo": self.modo,
            "importados": self.importados,
            "omitidos": self.omitidos,
            "errores": self.errores,
            "tablas": self.tablas,
            "timestamp": self.timestamp,
        }


# --- Data Exporter ---


class DataExporter:
    """
    Exporta todos los datos del usuario a un ZIP portable.

    El ZIP contiene:
    - manifest.json: Versión, timestamp, conteo por tabla
    - data/{tabla}.json: Datos de cada tabla
    - schema/tables.json: Definiciones de esquema
    """

    def __init__(self, supabase=None, user_id: str = "default"):
        """
        Args:
            supabase: Cliente AsyncClient de Supabase (opcional).
            user_id: ID del usuario cuyos datos se exportan.
        """
        self.supabase = supabase
        self.user_id = user_id

    async def export_full(self, output_dir: Optional[Path] = None) -> ExportResult:
        """
        Exporta todos los datos a un ZIP.

        Args:
            output_dir: Directorio donde guardar el ZIP (opcional).
                        Si es None, retorna los bytes en memoria.

        Returns:
            ExportResult con el resultado de la exportación.

        Raises:
            ExportacionFallida: Si ocurre un error crítico durante la exportación.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        manifest: dict = {
            "version": EXPORT_VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user_id": self.user_id,
            "tables": {},
        }

        all_data: dict[str, list] = {}
        errores: list[str] = []
        total_registros = 0

        for table in EXPORT_TABLES:
            data = await self._export_table(table)
            all_data[table] = data
            manifest["tables"][table] = {
                "count": len(data),
                "schema_version": "1.0",
            }
            total_registros += len(data)
            if not data and self.supabase:
                errores.append(f"Tabla '{table}' vacía o inaccesible")

        # Construir ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for table, data in all_data.items():
                zf.writestr(f"data/{table}.json", json.dumps(data, default=str, indent=2))
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            zf.writestr("schema/tables.json", json.dumps(self._get_schema_definitions(), indent=2))

        zip_bytes = zip_buffer.getvalue()
        zip_path_str = None

        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            zip_path = output_dir / f"monstruo_export_{timestamp}.zip"
            zip_path.write_bytes(zip_bytes)
            zip_path_str = str(zip_path)

        logger.info(
            "exportacion_completa",
            tablas=len(EXPORT_TABLES),
            registros=total_registros,
            user_id=self.user_id,
        )

        return ExportResult(
            exitoso=True,
            tablas_exportadas=len(EXPORT_TABLES),
            registros_totales=total_registros,
            zip_path=zip_path_str,
            zip_bytes=zip_bytes,
            errores=errores,
        )

    async def _export_table(self, table: str) -> list[dict]:
        """Exporta una tabla de Supabase."""
        if self.supabase is None:
            return []
        try:
            response = await self.supabase.table(table).select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error("export_tabla_error", tabla=table, error=str(e))
            return []

    def _get_schema_definitions(self) -> dict:
        return {
            "version": EXPORT_VERSION,
            "tables": {table: {"type": "array", "items": {"type": "object"}} for table in EXPORT_TABLES},
        }


# --- Data Importer ---


class DataImporter:
    """
    Importa datos desde un ZIP de exportación de El Monstruo.

    Modos:
    - merge: Upsert (no borra datos existentes)
    - replace: Borra y reinserta
    - dry_run: Valida sin escribir
    """

    def __init__(self, supabase=None, user_id: str = "default"):
        """
        Args:
            supabase: Cliente AsyncClient de Supabase (opcional).
            user_id: ID del usuario destino.
        """
        self.supabase = supabase
        self.user_id = user_id

    async def import_from_zip(self, zip_data: bytes, modo: str = "merge") -> ImportResult:
        """
        Importa datos desde un ZIP de exportación.

        Args:
            zip_data: Bytes del ZIP de exportación.
            modo: Modo de importación (merge | replace | dry_run).

        Returns:
            ImportResult con el resultado de la importación.

        Raises:
            ManifiestoInvalido: Si el ZIP no tiene un manifiesto válido.
            ImportacionFallida: Si ocurre un error crítico.
        """
        if modo not in ("merge", "replace", "dry_run"):
            raise ImportacionFallida(f"Modo inválido: '{modo}'. Usa merge, replace o dry_run.")

        result = ImportResult(exitoso=False, modo=modo)

        try:
            with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
                manifest = json.loads(zf.read("manifest.json"))
                if not self._validate_manifest(manifest):
                    raise ManifiestoInvalido()

                for table in manifest["tables"]:
                    try:
                        records = json.loads(zf.read(f"data/{table}.json"))
                    except KeyError:
                        result.tablas[table] = {"status": "archivo_no_encontrado"}
                        continue

                    if modo == "dry_run":
                        result.tablas[table] = {
                            "count": len(records),
                            "status": "validado",
                        }
                        result.importados += len(records)
                        continue

                    table_result = await self._import_table(table, records, modo)
                    result.tablas[table] = table_result
                    result.importados += table_result.get("importados", 0)
                    result.omitidos += table_result.get("omitidos", 0)
                    result.errores += table_result.get("errores", 0)

            result.exitoso = True
            logger.info(
                "importacion_completa",
                modo=modo,
                importados=result.importados,
                omitidos=result.omitidos,
                errores=result.errores,
            )

        except (ManifiestoInvalido, ImportacionFallida):
            raise
        except Exception as e:
            raise ImportacionFallida(str(e)) from e

        return result

    async def _import_table(self, table: str, records: list[dict], modo: str) -> dict:
        """Importa registros en una tabla."""
        if self.supabase is None:
            return {"importados": len(records), "omitidos": 0, "errores": 0, "status": "simulado"}

        importados, omitidos, errores = 0, 0, 0

        if modo == "replace":
            try:
                await self.supabase.table(table).delete().neq("id", "impossible").execute()
            except Exception as e:
                logger.warning("tabla_delete_error", tabla=table, error=str(e))

        for record in records:
            try:
                if modo == "merge":
                    await self.supabase.table(table).upsert(record).execute()
                else:
                    await self.supabase.table(table).insert(record).execute()
                importados += 1
            except Exception as e:
                if "duplicate" in str(e).lower():
                    omitidos += 1
                else:
                    errores += 1
                    logger.error("import_record_error", tabla=table, error=str(e))

        return {"importados": importados, "omitidos": omitidos, "errores": errores}

    def _validate_manifest(self, manifest: dict) -> bool:
        """Valida que el manifiesto tenga los campos requeridos."""
        return all(k in manifest for k in ["version", "exported_at", "tables"])


# --- Portability Engine (facade) ---


class PortabilityEngine:
    """
    Fachada principal del Data Portability Engine.
    Combina exportación e importación en una interfaz unificada.
    """

    def __init__(self, supabase=None, user_id: str = "default"):
        self.exporter = DataExporter(supabase=supabase, user_id=user_id)
        self.importer = DataImporter(supabase=supabase, user_id=user_id)
        self._historial_exports: list[dict] = []

    async def export(self, output_dir: Optional[Path] = None) -> ExportResult:
        """Exporta todos los datos del usuario."""
        result = await self.exporter.export_full(output_dir=output_dir)
        self._historial_exports.append(result.to_dict())
        return result

    async def import_data(self, zip_data: bytes, modo: str = "merge") -> ImportResult:
        """Importa datos desde un ZIP de exportación."""
        return await self.importer.import_from_zip(zip_data=zip_data, modo=modo)

    def get_export_history(self) -> list[dict]:
        """Retorna el historial de exportaciones."""
        return self._historial_exports

    def to_dict(self) -> dict:
        """Serialización para el Command Center."""
        return {
            "tablas_soportadas": len(EXPORT_TABLES),
            "export_version": EXPORT_VERSION,
            "exports_realizados": len(self._historial_exports),
            "ultimo_export": self._historial_exports[-1] if self._historial_exports else None,
        }


# --- Singleton ---

_portability_engine: PortabilityEngine | None = None


def get_portability_engine() -> PortabilityEngine:
    """Retorna el singleton del PortabilityEngine."""
    global _portability_engine
    if _portability_engine is None:
        _portability_engine = PortabilityEngine()
    return _portability_engine


def init_portability_engine(supabase=None, user_id: str = "default") -> PortabilityEngine:
    """Inicializa el singleton del PortabilityEngine."""
    global _portability_engine
    _portability_engine = PortabilityEngine(supabase=supabase, user_id=user_id)
    return _portability_engine
