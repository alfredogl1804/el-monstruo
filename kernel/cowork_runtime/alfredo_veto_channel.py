"""
kernel/cowork_runtime/alfredo_veto_channel.py — M9 Anexo Sprint COWORK-RUNTIME-001

Canal de veto bidireccional Alfredo → Cowork.

M9 (auditoria, anexo): "Alfredo deberia tener un canal directo (Telegram, app
Flutter, comando CLI) para emitir veto inmediato sobre Cowork cuando detecte
patron de violacion. Ese veto:
  - Bloquea la proxima respuesta de Cowork
  - Fuerza re-Pre-flight Memento
  - Triggea correctivo en runtime (no en doc post-mortem)
  - Queda registrado en cowork_sesiones.correctivos_recibidos

Equivalente operativo de las 9 palabras clave canonizadas en CLAUDE.md, pero
con enforcement real en lugar de texto."

Decisiones de diseño:
  1. Modulo importable, NO modifica telegram_notifier.py (DSC-MO-008 membrana).
     El cableado Telegram lo hace el dueño del runner cuando consuma este modulo.
  2. Canal pluggable: notify_callback opcional (Cowork / Telegram / app Flutter
     / CLI). Sin callback, el veto solo se persiste y bloquea logicamente.
  3. Estado del veto persiste en archivo local (bridge/alfredo_veto_state.json)
     + opcionalmente en cowork_sesiones.correctivos_recibidos via SessionMemoryStore.
  4. Palabras clave canonicas (las 9 + alias):
       VETO, ALTO, STOP, REPENSAR, EQUIVOCADO, MAL, NO,
       PARAR, BASTA
  5. Blue-Green: enabled flag default false (DSC-MO-011 Gate 7).

Refs:
  - M9 de bridge/cowork_to_manus_PROMPT_AYUDA_COWORK_OBEDIENCIA_2026_05_11.md
  - DSC-MO-008 (membrana telegram_notifier no modificable)
  - DSC-MO-011 Gate 7 (Blue-Green)
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

# ============================================================================
# Tipos
# ============================================================================


class VetoSeverity(str, Enum):
    SOFT = "soft"  # warn + reinject_rules
    HARD = "hard"  # block + force_preflight
    HALT = "halt"  # stop session, require Alfredo restart


# Palabras clave canonicas con severidad asignada
VETO_KEYWORDS = {
    # HALT: stop total
    "VETO": VetoSeverity.HALT,
    "ALTO": VetoSeverity.HALT,
    "STOP": VetoSeverity.HALT,
    "BASTA": VetoSeverity.HALT,
    "PARAR": VetoSeverity.HALT,
    # HARD: block + reset
    "REPENSAR": VetoSeverity.HARD,
    "EQUIVOCADO": VetoSeverity.HARD,
    "MAL": VetoSeverity.HARD,
    # SOFT: warn
    "NO": VetoSeverity.SOFT,
}


@dataclass
class VetoEvent:
    timestamp: float = field(default_factory=time.time)
    palabra_clave: str = ""
    severidad: str = VetoSeverity.SOFT.value
    contexto: str = ""
    hilo_origen: str = "alfredo"
    consumido: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Canal
# ============================================================================

DEFAULT_STATE_PATH = Path("bridge/alfredo_veto_state.json")


class AlfredoVetoChannel:
    """
    Canal de veto: Alfredo emite -> persistencia -> Cowork lo lee antes de responder.

    Patrones de uso:
        # Lado Alfredo (CLI / Telegram / app Flutter)
        channel.emit_veto("VETO", contexto="No me entendiste el spec MOBILE_1B")

        # Lado Cowork (en pre-response hook)
        veto = channel.consume_pending_veto()
        if veto:
            # bloquear / force-preflight / etc segun veto.severidad
    """

    def __init__(
        self,
        state_path: Optional[Path] = None,
        enabled: Optional[bool] = None,
        notify_callback: Optional[Callable[[VetoEvent], None]] = None,
    ) -> None:
        self.state_path = Path(state_path) if state_path else DEFAULT_STATE_PATH
        if enabled is None:
            enabled = os.environ.get("COWORK_VETO_ENABLED", "false").lower() == "true"
        self.enabled = enabled
        self.notify_callback = notify_callback
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Lado Alfredo (emisor)
    # ------------------------------------------------------------------

    def emit_veto(
        self,
        palabra_clave: str,
        contexto: str = "",
        hilo_origen: str = "alfredo",
        severidad: Optional[VetoSeverity] = None,
    ) -> VetoEvent:
        """Alfredo emite veto. Persiste y notifica callback si esta configurado."""
        if not self.enabled:
            # Aun en disabled, registramos para que Alfredo vea que su input fue ignorado
            event = VetoEvent(
                palabra_clave=palabra_clave.upper(),
                severidad=VetoSeverity.SOFT.value,
                contexto=f"[CHANNEL_DISABLED] {contexto}",
                hilo_origen=hilo_origen,
            )
            return event

        kw_upper = palabra_clave.upper().strip()
        if severidad is None:
            severidad = VETO_KEYWORDS.get(kw_upper, VetoSeverity.SOFT)

        event = VetoEvent(
            palabra_clave=kw_upper,
            severidad=severidad.value,
            contexto=contexto,
            hilo_origen=hilo_origen,
        )
        self._persist_event(event)
        if self.notify_callback:
            try:
                self.notify_callback(event)
            except Exception:
                pass  # Resilient: notify failure no bloquea el veto
        return event

    def detect_veto_in_message(
        self,
        mensaje: str,
        contexto: str = "",
        hilo_origen: str = "alfredo",
    ) -> Optional[VetoEvent]:
        """
        Detecta automaticamente palabras clave en un mensaje de Alfredo.

        Retorna el primer veto detectado o None. Usa word boundaries para no
        matchear sub-strings (ej: 'NO' dentro de 'NORMAL' no triggea).
        """
        if not mensaje:
            return None
        upper = mensaje.upper()
        for kw, sev in sorted(
            VETO_KEYWORDS.items(),
            key=lambda x: (-["soft", "hard", "halt"].index(x[1].value), -len(x[0])),
        ):
            # Word boundary match
            if re.search(rf"\b{re.escape(kw)}\b", upper):
                return self.emit_veto(kw, contexto=contexto, hilo_origen=hilo_origen, severidad=sev)
        return None

    # ------------------------------------------------------------------
    # Lado Cowork (consumidor)
    # ------------------------------------------------------------------

    def consume_pending_veto(self) -> Optional[VetoEvent]:
        """
        Cowork llama esto antes de responder. Devuelve el veto pendiente mas reciente
        (si hay) y lo marca como consumido.
        """
        events = self._read_events()
        pendientes = [e for e in events if not e.consumido]
        if not pendientes:
            return None
        veto = pendientes[-1]  # Mas reciente
        veto.consumido = True
        self._write_events(events)
        return veto

    def peek_pending_veto(self) -> Optional[VetoEvent]:
        """Lee el veto mas reciente pendiente sin marcarlo consumido."""
        events = self._read_events()
        pendientes = [e for e in events if not e.consumido]
        return pendientes[-1] if pendientes else None

    def history(self, limit: int = 50) -> list[VetoEvent]:
        events = self._read_events()
        return events[-limit:]

    def clear(self) -> None:
        """Borra todo el historial (cuidado, irreversible)."""
        self._write_events([])

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _persist_event(self, event: VetoEvent) -> None:
        events = self._read_events()
        events.append(event)
        # Mantener solo los ultimos 200 para no crecer indefinidamente
        events = events[-200:]
        self._write_events(events)

    def _read_events(self) -> list[VetoEvent]:
        if not self.state_path.exists():
            return []
        try:
            with self.state_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            return [VetoEvent(**d) for d in raw]
        except Exception:
            return []

    def _write_events(self, events: list[VetoEvent]) -> None:
        with self.state_path.open("w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in events], f, indent=2, ensure_ascii=False)


# ============================================================================
# CLI (para que Alfredo emita veto desde terminal)
# ============================================================================


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Canal de veto Alfredo→Cowork (M9).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # emit
    p_emit = sub.add_parser("emit", help="Emitir veto")
    p_emit.add_argument("palabra", help="Palabra clave (VETO/ALTO/STOP/REPENSAR/MAL/NO/...)")
    p_emit.add_argument("--contexto", default="", help="Contexto del veto")
    p_emit.add_argument("--enable", action="store_true", help="Forzar enabled=True")

    # peek
    sub.add_parser("peek", help="Ver veto pendiente sin consumir")

    # consume
    sub.add_parser("consume", help="Consumir veto pendiente")

    # history
    p_hist = sub.add_parser("history", help="Ver historial de vetos")
    p_hist.add_argument("--limit", type=int, default=20)

    # clear
    sub.add_parser("clear", help="Borrar todo el historial (irreversible)")

    args = parser.parse_args(argv)

    enabled = True if (getattr(args, "enable", False)) else None
    channel = AlfredoVetoChannel(enabled=enabled)

    if args.cmd == "emit":
        event = channel.emit_veto(args.palabra, contexto=args.contexto)
        print(json.dumps(event.to_dict(), indent=2, ensure_ascii=False))
    elif args.cmd == "peek":
        veto = channel.peek_pending_veto()
        print(json.dumps(veto.to_dict() if veto else None, indent=2, ensure_ascii=False))
    elif args.cmd == "consume":
        veto = channel.consume_pending_veto()
        print(json.dumps(veto.to_dict() if veto else None, indent=2, ensure_ascii=False))
    elif args.cmd == "history":
        events = channel.history(limit=args.limit)
        print(json.dumps([e.to_dict() for e in events], indent=2, ensure_ascii=False))
    elif args.cmd == "clear":
        channel.clear()
        print("Historial borrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
