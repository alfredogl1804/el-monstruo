"""
kernel/cowork_runtime/drift_detector.py — T7 PREMIUM Sprint COWORK-RUNTIME-001

Auto-correccion de drift contextual.

M7 (auditoria): "detector que monitorea cuando una sesion lleva >N turnos sin
Pre-flight Memento explicito. Trigger auto-re-inyeccion. Resultado: Cowork no
opera 'muy fresco' inicio + 'muy diluido' despues."

Composicion limpia:
  - DriftDetector observa estado de sesion (turnos, ts_ultimo_preflight, ratio_violaciones)
  - Cuando detecta drift, recomienda accion: REINJECT_RULES, FORCE_PREFLIGHT, NO_OP
  - Se invoca desde el hook T1 antes de responder + desde el reinjector T2 antes de tick

Refs:
  - M7 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md
  - DSC-MO-011 Gate 7 (Blue-Green: enabled flag default false)
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================================================
# Tipos
# ============================================================================

class DriftAction(str, Enum):
    NO_OP = "no_op"
    REINJECT_RULES = "reinject_rules"
    FORCE_PREFLIGHT = "force_preflight"
    HARD_HALT = "hard_halt"


@dataclass
class DriftSignal:
    """Senal de drift detectada con metadata para accion."""
    action: DriftAction
    razon: str
    severidad: int  # 0=info, 1=warn, 2=error, 3=halt
    metricas: dict = field(default_factory=dict)


@dataclass
class SessionDriftState:
    """Estado mutable que el detector observa."""
    turnos: int = 0
    ts_inicio: float = field(default_factory=time.time)
    ts_ultimo_preflight: Optional[float] = None
    ts_ultima_reinjeccion: Optional[float] = None
    violaciones_acumuladas: int = 0
    correctivos_alfredo: int = 0
    pre_flight_ejecutado: bool = False


# ============================================================================
# Detector
# ============================================================================

class DriftDetector:
    """
    Detector de drift contextual con thresholds configurables.

    Defaults canonicos derivados de M7:
      - max_turnos_sin_preflight = 5  (Cowork debe re-confirmar contexto cada 5 turnos)
      - max_segundos_sin_preflight = 1800  (30 min)
      - max_violaciones_acumuladas = 3  (mas de 3 violaciones = drift severo)
      - max_correctivos_alfredo = 2  (Alfredo corrige 2 veces = halt)
    """

    def __init__(
        self,
        max_turnos_sin_preflight: Optional[int] = None,
        max_segundos_sin_preflight: Optional[int] = None,
        max_violaciones_acumuladas: Optional[int] = None,
        max_correctivos_alfredo: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self.max_turnos_sin_preflight = (
            max_turnos_sin_preflight
            if max_turnos_sin_preflight is not None
            else int(os.environ.get("COWORK_DRIFT_MAX_TURNOS", "5"))
        )
        self.max_segundos_sin_preflight = (
            max_segundos_sin_preflight
            if max_segundos_sin_preflight is not None
            else int(os.environ.get("COWORK_DRIFT_MAX_SEGUNDOS", "1800"))
        )
        self.max_violaciones_acumuladas = (
            max_violaciones_acumuladas
            if max_violaciones_acumuladas is not None
            else int(os.environ.get("COWORK_DRIFT_MAX_VIOLACIONES", "3"))
        )
        self.max_correctivos_alfredo = (
            max_correctivos_alfredo
            if max_correctivos_alfredo is not None
            else int(os.environ.get("COWORK_DRIFT_MAX_CORRECTIVOS", "2"))
        )
        # Blue-Green flag (DSC-MO-011 Gate 7)
        if enabled is None:
            enabled = os.environ.get("COWORK_DRIFT_ENABLED", "false").lower() == "true"
        self.enabled = enabled

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def evaluate(self, state: SessionDriftState) -> DriftSignal:
        """
        Evalua estado actual y devuelve senal de drift.

        Orden de prioridad (early-return en cada nivel):
          1. HALT por correctivos repetidos de Alfredo
          2. REINJECT por violaciones acumuladas
          3. FORCE_PREFLIGHT por turno 1 sin pre-flight
          4. REINJECT por turnos sin pre-flight
          5. REINJECT por tiempo sin pre-flight
          6. NO_OP
        """
        if not self.enabled:
            return DriftSignal(
                action=DriftAction.NO_OP,
                razon="drift_detector disabled (COWORK_DRIFT_ENABLED=false)",
                severidad=0,
            )

        ahora = time.time()

        # 1. HALT
        if state.correctivos_alfredo >= self.max_correctivos_alfredo:
            return DriftSignal(
                action=DriftAction.HARD_HALT,
                razon=(
                    f"Alfredo te corrigio {state.correctivos_alfredo} veces "
                    "(threshold={self.max_correctivos_alfredo}). "
                    "Stop. Pedir contexto explicito antes de seguir."
                ),
                severidad=3,
                metricas={"correctivos_alfredo": state.correctivos_alfredo},
            )

        # 2. REINJECT por violaciones acumuladas
        if state.violaciones_acumuladas >= self.max_violaciones_acumuladas:
            return DriftSignal(
                action=DriftAction.REINJECT_RULES,
                razon=(
                    f"{state.violaciones_acumuladas} violaciones acumuladas "
                    f"(threshold={self.max_violaciones_acumuladas}). "
                    "Re-inyectar reglas duras antes de proxima respuesta."
                ),
                severidad=2,
                metricas={"violaciones": state.violaciones_acumuladas},
            )

        # 3. FORCE_PREFLIGHT en turno 1
        if state.turnos == 1 and not state.pre_flight_ejecutado:
            return DriftSignal(
                action=DriftAction.FORCE_PREFLIGHT,
                razon="Sesion turno 1 sin Pre-flight Memento ejecutado. Capa 8 obligatoria.",
                severidad=2,
                metricas={"turnos": state.turnos},
            )

        # 4. REINJECT por turnos sin pre-flight
        turnos_desde_preflight = state.turnos
        if state.ts_ultimo_preflight:
            # Aproximamos: contamos turnos totales como proxy si no hay tracking finer
            pass
        if (
            turnos_desde_preflight >= self.max_turnos_sin_preflight
            and (
                state.ts_ultima_reinjeccion is None
                or (ahora - state.ts_ultima_reinjeccion) > 60
            )
        ):
            return DriftSignal(
                action=DriftAction.REINJECT_RULES,
                razon=(
                    f"{turnos_desde_preflight} turnos sin re-inyectar reglas "
                    f"(threshold={self.max_turnos_sin_preflight}). "
                    "Cowork puede estar diluyendose."
                ),
                severidad=1,
                metricas={"turnos_desde_preflight": turnos_desde_preflight},
            )

        # 5. REINJECT por tiempo sin pre-flight
        if state.ts_ultimo_preflight:
            segundos_desde_preflight = ahora - state.ts_ultimo_preflight
            if segundos_desde_preflight >= self.max_segundos_sin_preflight:
                return DriftSignal(
                    action=DriftAction.REINJECT_RULES,
                    razon=(
                        f"{int(segundos_desde_preflight)}s sin re-inyectar reglas "
                        f"(threshold={self.max_segundos_sin_preflight}s). "
                        "Sesion larga sin refresh."
                    ),
                    severidad=1,
                    metricas={"segundos_desde_preflight": int(segundos_desde_preflight)},
                )

        return DriftSignal(
            action=DriftAction.NO_OP,
            razon="Sesion en parametros saludables",
            severidad=0,
        )

    def mark_preflight_ejecutado(self, state: SessionDriftState) -> None:
        state.pre_flight_ejecutado = True
        state.ts_ultimo_preflight = time.time()

    def mark_reinjeccion(self, state: SessionDriftState) -> None:
        state.ts_ultima_reinjeccion = time.time()

    def tick_turno(self, state: SessionDriftState) -> None:
        state.turnos += 1


# ============================================================================
# CLI
# ============================================================================

def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Drift detector CLI (T7).")
    parser.add_argument("--turnos", type=int, default=0)
    parser.add_argument("--violaciones", type=int, default=0)
    parser.add_argument("--correctivos", type=int, default=0)
    parser.add_argument("--preflight-ejecutado", action="store_true")
    parser.add_argument("--enable", action="store_true", help="Forzar enabled=True")
    args = parser.parse_args(argv)

    state = SessionDriftState(
        turnos=args.turnos,
        violaciones_acumuladas=args.violaciones,
        correctivos_alfredo=args.correctivos,
        pre_flight_ejecutado=args.preflight_ejecutado,
    )
    detector = DriftDetector(enabled=True if args.enable else None)
    signal = detector.evaluate(state)
    out = {
        "action": signal.action.value,
        "razon": signal.razon,
        "severidad": signal.severidad,
        "metricas": signal.metricas,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if signal.action != DriftAction.HARD_HALT else 2


if __name__ == "__main__":
    raise SystemExit(main())
