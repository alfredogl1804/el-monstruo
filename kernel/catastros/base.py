"""
CatastroBase — clase genérica para los 4 catastros DSC-G-007.1.

Provee interfaz uniforme (load_from_db, get, list, count, refresh) sobre
tablas o vistas en Supabase. Cada subclase fija su TABLE/VIEW y KEY_COLUMN.

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).
Spec: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_v2_OPCION_B_KICKOFF_2026_05_12.md §T3
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CatastroBase:
    """
    Base genérica para catastros DSC-G-007.1.

    Subclases DEBEN definir:
      - TABLE: str — nombre de tabla o vista en Supabase (público.<nombre>)
      - KEY_COLUMN: str — columna que actúa como clave lógica (default "key")

    Atributos:
      - _db: cliente con métodos .select(table, filters?) y .upsert(table, row, on_conflict?)
      - _cache: Dict[str, Dict] — cache opcional indexado por KEY_COLUMN
    """

    TABLE: str = ""
    KEY_COLUMN: str = "key"

    def __init__(self, db_client: Any) -> None:
        if not self.TABLE:
            raise ValueError(f"{self.__class__.__name__} debe definir TABLE en subclase")
        self._db = db_client
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._loaded: bool = False

    async def load_from_db(self) -> int:
        """
        Carga todas las rows desde DB/Vista al cache.

        Returns:
            Número de rows cargadas.
        """
        try:
            rows = await self._db.select(self.TABLE)
        except Exception as exc:
            logger.warning(
                "catastro_load_failed",
                extra={"table": self.TABLE, "error": str(exc)},
            )
            return 0

        self._cache.clear()
        for row in rows or []:
            key = row.get(self.KEY_COLUMN)
            if key is None:
                logger.warning(
                    "catastro_row_missing_key",
                    extra={"table": self.TABLE, "key_column": self.KEY_COLUMN},
                )
                continue
            self._cache[str(key)] = row

        self._loaded = True
        logger.info(
            "catastro_loaded",
            extra={"table": self.TABLE, "count": len(self._cache)},
        )
        return len(self._cache)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Devuelve la row con KEY_COLUMN==key o None si no existe."""
        return self._cache.get(str(key))

    def list(self) -> List[Dict[str, Any]]:
        """Devuelve todas las rows cargadas en cache."""
        return list(self._cache.values())

    def count(self) -> int:
        """Devuelve el número de rows en cache."""
        return len(self._cache)

    async def refresh(self) -> int:
        """Alias semántico para re-cargar el catastro desde DB."""
        return await self.load_from_db()

    @property
    def is_loaded(self) -> bool:
        return self._loaded
