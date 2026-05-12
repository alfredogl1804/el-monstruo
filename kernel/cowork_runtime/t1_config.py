"""
kernel/cowork_runtime/t1_config.py — Configuracion central de la fase T1.

T1 Pre-Response Hook: tres modos discretos.

    OFF           El hook no intercepta nada (legacy).
    OBSERVE_ONLY  El hook intercepta, clasifica, registra en audit log,
                  pero NO bloquea ningun output. Es el modo de entrada
                  obligatorio de la fase T1 segun acuerdo operativo
                  2026-05-12 (este archivo).
    ENFORCE       El hook intercepta, clasifica, registra y BLOQUEA
                  outputs cuya severidad sea P0 o P1. P2 nunca bloquea
                  aun en ENFORCE.

Regla dura: la transicion automatica OBSERVE_ONLY -> ENFORCE esta
PROHIBIDA. ENFORCE solo se activa via:

  (a) Llamada explicita en codigo (p.ej. T1Config.enforce_after_manual_audit())
      con `audit_completed=True` y `confirmed_p0_p1_count >= MIN_AUDITED`, y
  (b) Variable de entorno COWORK_T1_ALLOW_ENFORCE=true presente.

Si una de las dos condiciones falla, intentar activar ENFORCE devuelve
ValueError y el modo queda en OBSERVE_ONLY. NO existe "contador simple
>5 bloqueos" que escale automaticamente — ese path es explicitamente
no-implementado (ver tests).

Origen del requisito: spec T1 fase 1 (2026-05-12). Auditoria manual de
50 claims materiales sobre el audit log es prerequisito para considerar
ENFORCE.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class T1Mode(str, Enum):
    OFF = "off"
    OBSERVE_ONLY = "observe_only"
    ENFORCE = "enforce"


MIN_AUDITED_CLAIMS_FOR_ENFORCE = 50
MIN_PRECISION_FOR_ENFORCE = 0.80  # 80% precision sobre claims sin licencia
MAX_FALSE_POSITIVES_P2_FOR_ENFORCE = 0  # cero falsos positivos sobre P2

ENV_MODE = "COWORK_T1_MODE"
ENV_ALLOW_ENFORCE = "COWORK_T1_ALLOW_ENFORCE"


@dataclass
class T1Config:
    """
    Config inmutable del hook T1. Construir via factory:

        cfg = T1Config.observe_only()
        cfg = T1Config.from_env()
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=37,
        )
    """
    mode: T1Mode = T1Mode.OBSERVE_ONLY
    allow_enforce: bool = False
    audit_log_path: str = "bridge/t1_audit_log.jsonl"

    # -- factories ------------------------------------------------------

    @classmethod
    def off(cls) -> "T1Config":
        return cls(mode=T1Mode.OFF, allow_enforce=False)

    @classmethod
    def observe_only(cls) -> "T1Config":
        return cls(mode=T1Mode.OBSERVE_ONLY, allow_enforce=False)

    @classmethod
    def from_env(cls) -> "T1Config":
        """
        Lee modo desde env. Si COWORK_T1_MODE no esta seteada, default
        OBSERVE_ONLY (no OFF — el hook arranca observando por defecto).

        ENFORCE via env requiere AMBAS:
          COWORK_T1_MODE=enforce
          COWORK_T1_ALLOW_ENFORCE=true

        Si solo una de las dos esta presente, el modo cae a OBSERVE_ONLY
        (NO se hace auto-escalada).
        """
        raw_mode = os.environ.get(ENV_MODE, "").strip().lower()
        allow_enforce = os.environ.get(ENV_ALLOW_ENFORCE, "").lower() in (
            "1", "true", "yes", "on",
        )

        if raw_mode == "off":
            return cls(mode=T1Mode.OFF, allow_enforce=False)
        if raw_mode == "enforce":
            if not allow_enforce:
                # Intento de ENFORCE sin guardrail explicito -> degrada
                return cls(mode=T1Mode.OBSERVE_ONLY, allow_enforce=False)
            return cls(mode=T1Mode.ENFORCE, allow_enforce=True)
        # Default y "observe_only" -> OBSERVE_ONLY
        return cls(mode=T1Mode.OBSERVE_ONLY, allow_enforce=allow_enforce)

    @classmethod
    def enforce_after_manual_audit(
        cls,
        audit_completed: bool,
        confirmed_p0_p1_count: int,
        env_allow_enforce: Optional[bool] = None,
        precision: Optional[float] = None,
        false_positives_p2: Optional[int] = None,
        auditor: Optional[str] = None,
    ) -> "T1Config":
        """
        Construye un T1Config en ENFORCE solo si:
          - audit_completed is True
          - confirmed_p0_p1_count >= MIN_AUDITED_CLAIMS_FOR_ENFORCE (50)
          - precision >= MIN_PRECISION_FOR_ENFORCE (80%) sobre claims
            sin licencia (convergencia Copilot 365 — 2026-05-12)
          - false_positives_p2 <= MAX_FALSE_POSITIVES_P2_FOR_ENFORCE (0)
          - env COWORK_T1_ALLOW_ENFORCE=true (o env_allow_enforce override)
          - auditor == "alfredo" (T1 humano, no auto-promotion)

        precision y false_positives_p2 son opcionales para compatibilidad
        hacia atras con tests previos al spec convergencia 7 Sabios.
        Si NO se proporcionan, el guardrail nuevo se omite (modo legacy),
        pero ese path quedara deprecado.

        En cualquier otro caso lanza ValueError. NO degrada silencioso a
        OBSERVE_ONLY — el caller pidio ENFORCE explicitamente y debe saber
        si fallo el guardrail.
        """
        if env_allow_enforce is None:
            env_allow_enforce = os.environ.get(ENV_ALLOW_ENFORCE, "").lower() in (
                "1", "true", "yes", "on",
            )
        if not audit_completed:
            raise ValueError(
                "ENFORCE requiere auditoria manual completada. "
                "Pasa audit_completed=True solo despues de revisar los "
                f"{MIN_AUDITED_CLAIMS_FOR_ENFORCE} claims materiales."
            )
        if confirmed_p0_p1_count < MIN_AUDITED_CLAIMS_FOR_ENFORCE:
            raise ValueError(
                f"ENFORCE requiere >= {MIN_AUDITED_CLAIMS_FOR_ENFORCE} "
                f"claims P0/P1 confirmados. Recibido: {confirmed_p0_p1_count}."
            )
        if precision is not None and precision < MIN_PRECISION_FOR_ENFORCE:
            raise ValueError(
                f"ENFORCE requiere precision >= {MIN_PRECISION_FOR_ENFORCE:.0%} "
                f"sobre claims sin licencia. Recibido: {precision:.2%}."
            )
        if (
            false_positives_p2 is not None
            and false_positives_p2 > MAX_FALSE_POSITIVES_P2_FOR_ENFORCE
        ):
            raise ValueError(
                f"ENFORCE requiere {MAX_FALSE_POSITIVES_P2_FOR_ENFORCE} "
                f"falsos positivos sobre claims P2. Recibido: "
                f"{false_positives_p2}."
            )
        if auditor is not None and auditor != "alfredo":
            raise ValueError(
                f"ENFORCE solo legitimable con auditor='alfredo' (T1 humano). "
                f"Recibido: {auditor!r}."
            )
        if not env_allow_enforce:
            raise ValueError(
                f"ENFORCE requiere variable de entorno "
                f"{ENV_ALLOW_ENFORCE}=true. Guardrail anti-escalada-automatica."
            )
        return cls(mode=T1Mode.ENFORCE, allow_enforce=True)

    # -- queries --------------------------------------------------------

    def is_observing(self) -> bool:
        return self.mode in (T1Mode.OBSERVE_ONLY, T1Mode.ENFORCE)

    def is_enforcing(self) -> bool:
        return self.mode == T1Mode.ENFORCE and self.allow_enforce

    def blocks_severity(self, severity: str) -> bool:
        """
        Reglas duras de bloqueo:
        - OFF / OBSERVE_ONLY: nunca bloquea (return False)
        - ENFORCE: bloquea solo P0 y P1. P2 nunca bloquea aun en ENFORCE.
        """
        if not self.is_enforcing():
            return False
        return severity.upper() in ("P0", "P1")
