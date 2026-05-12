"""Budget tracker del Brand Engine — kill-switch por gasto diario.

Lleva el contador acumulado de USD gastados por el Brand Engine en el día
corriente UTC. Persistencia simple en archivo JSON (no requiere DB para
cumplir su rol, y sobrevive a redeploys de Railway si el volumen es
persistente; si no, el contador se resetea — comportamiento aceptable y
documentado, es preferible reset accidental a no tener kill-switch).

Estados:

- ``OK``  cuando ``gasto_hoy < budget_alerta``.
- ``ALERT`` cuando ``budget_alerta ≤ gasto_hoy < budget_kill``.
- ``KILLED`` cuando ``gasto_hoy ≥ budget_kill`` — ``BrandEngine.validate()``
  debe degradar a ``approved`` sintético (fail-open) por el resto del día.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T5 budget).
DSC: DSC-MO-010 (cost accounting Mainspring).
"""

from __future__ import annotations

import datetime as _dt
import enum
import json
import logging
import os
import threading
from pathlib import Path

log = logging.getLogger(__name__)


class BudgetState(enum.Enum):
    OK = "ok"
    ALERT = "alert"
    KILLED = "killed"


_DEFAULT_STATE_PATH = Path(
    os.environ.get(
        "BRAND_ENGINE_BUDGET_PATH",
        "/tmp/brand_engine_budget.json",  # Railway: /tmp es escribible.
    )
)


class BudgetTracker:
    """Contador thread-safe de gasto diario del Brand Engine.

    Se construye una vez por proceso. Mantiene el día UTC actual y resetea
    automáticamente al cambio de día. El estado se persiste en disco para
    sobrevivir restarts del proceso (best-effort — si falla la escritura,
    se logea warning pero el contador sigue funcionando en memoria).
    """

    def __init__(
        self,
        budget_alerta_usd: float,
        budget_kill_usd: float,
        state_path: Path | None = None,
    ) -> None:
        self._budget_alerta = float(budget_alerta_usd)
        self._budget_kill = float(budget_kill_usd)
        self._state_path = state_path or _DEFAULT_STATE_PATH
        self._lock = threading.Lock()
        self._gasto_hoy: float = 0.0
        self._fecha_utc: str = _dt.datetime.now(_dt.timezone.utc).date().isoformat()
        self._load_from_disk()

    # ── Estado público ──────────────────────────────────────────────────

    @property
    def gasto_hoy_usd(self) -> float:
        with self._lock:
            self._roll_if_new_day()
            return self._gasto_hoy

    def state(self) -> BudgetState:
        gasto = self.gasto_hoy_usd
        if gasto >= self._budget_kill:
            return BudgetState.KILLED
        if gasto >= self._budget_alerta:
            return BudgetState.ALERT
        return BudgetState.OK

    def is_killed(self) -> bool:
        return self.state() == BudgetState.KILLED

    def record(self, cost_usd: float) -> None:
        """Registra un costo y persiste a disco."""
        if cost_usd <= 0:
            return
        with self._lock:
            self._roll_if_new_day()
            self._gasto_hoy += float(cost_usd)
            self._save_to_disk()
        log.debug(
            "brand_engine_budget_recorded",
            extra={"delta_usd": cost_usd, "total_hoy_usd": self._gasto_hoy},
        )

    # ── Internals ──────────────────────────────────────────────────────

    def _roll_if_new_day(self) -> None:
        today = _dt.datetime.now(_dt.timezone.utc).date().isoformat()
        if today != self._fecha_utc:
            log.info(
                "brand_engine_budget_rolled_over",
                extra={"prev_date": self._fecha_utc, "prev_total": self._gasto_hoy},
            )
            self._fecha_utc = today
            self._gasto_hoy = 0.0
            self._save_to_disk()

    def _load_from_disk(self) -> None:
        try:
            if not self._state_path.exists():
                return
            with open(self._state_path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("fecha_utc") == self._fecha_utc:
                self._gasto_hoy = float(data.get("gasto_hoy_usd", 0.0))
            # Si la fecha es distinta, el contador queda en 0 (correcto).
        except (OSError, ValueError, json.JSONDecodeError) as e:
            log.warning("brand_engine_budget_load_failed", extra={"error": str(e)})

    def _save_to_disk(self) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._state_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"fecha_utc": self._fecha_utc, "gasto_hoy_usd": self._gasto_hoy},
                    f,
                )
            tmp_path.replace(self._state_path)
        except OSError as e:
            log.warning("brand_engine_budget_save_failed", extra={"error": str(e)})
