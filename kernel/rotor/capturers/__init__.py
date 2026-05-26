"""
Capturers del Rotor — captura actividad real de 6 sources canónicos.

Sprint: ROTOR-001 (T2) — pieza diferencial Reloj Suizo
DSC enforzado: DSC-MO-010 (Reloj Suizo), DSC-G-017 (DSC-as-Contract)
Owner: Hilo Ejecutor 2 (manus_hilo_b)
Fecha: 2026-05-12

Cada capturer implementa BaseCapturer y persiste filas en rotor_activity_log
con energy_units=NULL (poblado posteriormente por energy_calculator).

Diseño:
  - Cada capturer es una función pura: recibe payload del trigger y retorna
    RotorActivity. La persistencia ocurre en BaseCapturer.persist().
  - Persistencia es opcional (allow inyección de psycopg connection o uso de
    persist_callable mock para tests sin DB).
  - Los 6 capturers tienen test 1:1 con fixture (tests/rotor/test_capturers_*.py).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping, Optional

from kernel.rotor.energy_calculator import VALID_SOURCES, RotorActivity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipo de la función de persistencia (inyectable para tests)
# ---------------------------------------------------------------------------
PersistCallable = Callable[[RotorActivity], Optional[str]]
"""
Función que persiste una RotorActivity y retorna el id (UUID) de la fila creada.
Default impl en kernel.rotor.persistence (que importa psycopg lazy).

Para tests, inyectar un mock que retorne un UUID fijo sin tocar DB.
"""


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------
class BaseCapturer(ABC):
    """
    Base class para capturers del Rotor.

    Subclases implementan capture() y declaran SOURCE como ClassVar.
    """

    SOURCE: str = ""  # Debe ser uno de VALID_SOURCES
    DEFAULT_ACTOR: str = ""  # Subclase debe definirlo

    def __init__(
        self,
        persist_fn: Optional[PersistCallable] = None,
    ) -> None:
        if self.SOURCE not in VALID_SOURCES:
            raise ValueError(f"{self.__class__.__name__}.SOURCE={self.SOURCE!r} no esta en VALID_SOURCES")
        self._persist_fn = persist_fn

    @abstractmethod
    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        Convierte el evento crudo del trigger en RotorActivity canónica.

        Subclase implementa la traducción específica por source.
        """
        ...

    def capture_and_persist(self, raw_event: Mapping[str, Any]) -> Optional[str]:
        """
        Captura el evento y lo persiste si hay persist_fn inyectada.
        Retorna el id de la fila persistida (o None si no se persistió).
        """
        activity = self.capture(raw_event)
        if self._persist_fn is None:
            logger.warning(
                "%s.capture_and_persist: persist_fn no inyectada, solo capture",
                self.__class__.__name__,
            )
            return None
        try:
            row_id = self._persist_fn(activity)
            logger.info(
                "rotor.capture: source=%s actor=%s row_id=%s",
                activity.source,
                activity.actor,
                row_id,
            )
            return row_id
        except Exception as exc:
            # Fail-soft: capturer never tira el caller process. Log + return None.
            logger.error(
                "rotor.capture FAIL: source=%s actor=%s err=%s",
                activity.source,
                activity.actor,
                exc,
            )
            return None


# REGISTRY canonico de los 6 capturers (exportable, lazy-built)
# Mapeo source -> BaseCapturer subclass. Los handlers de webhook / polling
# usan este registry para enrutar eventos al capturer correcto.
def _build_registry() -> dict:
    """Lazy build del registry para evitar circular imports."""
    from kernel.rotor.capturers.cowork_capturer import CoworkCapturer
    from kernel.rotor.capturers.github_capturer import GitHubCapturer
    from kernel.rotor.capturers.latido_capturer import LatidoCapturer
    from kernel.rotor.capturers.manus_capturer import ManusCapturer
    from kernel.rotor.capturers.supabase_capturer import SupabaseCapturer
    from kernel.rotor.capturers.telegram_capturer import TelegramCapturer

    return {
        "github_commit": GitHubCapturer,
        "supabase_query": SupabaseCapturer,
        "telegram_message": TelegramCapturer,
        "cowork_session": CoworkCapturer,
        "manus_session": ManusCapturer,
        "embrion_latido": LatidoCapturer,
    }


REGISTRY: dict = _build_registry()

__all__ = ["BaseCapturer", "PersistCallable", "REGISTRY"]
