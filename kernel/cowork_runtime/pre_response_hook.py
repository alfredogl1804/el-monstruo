"""
kernel/cowork_runtime/pre_response_hook.py — T1 MAGNA Sprint COWORK-RUNTIME-001

Pre-respuesta hook que intercepta cada output candidato de Cowork antes de
enviarlo a Alfredo. Valida contra `tools.cowork_guardian.validate_output`.
Si guardian devuelve passed=False, bloquea + devuelve feedback estructurado
con violaciones detectadas para que Cowork reescriba.

Doctrina:
- DSC-MO-005: Cowork (T2) es Arquitecto, no Ejecutor — este hook NO es para
  Cowork escribiendo codigo, es para Cowork enviando texto a Alfredo.
- M1 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md: enforcement runtime
  de las 22 reglas que Cowork canonizo y luego violo.
- "habla con codigo no con texto": este hook ES el codigo que enforza
  la doctrina pasiva de CLAUDE.md.

Uso programatico:

    from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook
    hook = CoworkPreResponseHook()
    permitido, payload = hook.intercept(cowork_output, user_message)
    if permitido:
        send_to_alfredo(payload)  # payload == cowork_output original
    else:
        # payload == feedback de correccion para que Cowork reescriba
        cowork_rewrite(payload)

Uso CLI:

    echo "Andate a dormir tranquilo" | python -m kernel.cowork_runtime.pre_response_hook \\
        --user-message "VAMOS A AVANZAR"

    Exit code 0 si pasa, 1 si bloquea.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Importacion robusta del guardian sea cual sea el cwd de invocacion
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cowork_guardian import GuardianVerdict, validate_output  # noqa: E402
from kernel.cowork_runtime.t1_config import T1Config, T1Mode  # noqa: E402
from kernel.cowork_runtime.t1_output_contract import (  # noqa: E402
    ContractReport,
    analyze as t1_analyze,
    format_violation_feedback as t1_format_feedback,
)
from kernel.cowork_runtime.t1_audit_log import T1AuditLog  # noqa: E402


@dataclass
class HookStats:
    """Contadores de la sesion en curso para diagnostico."""
    interceptions_total: int = 0
    blocked_total: int = 0
    blocked_magna: int = 0
    blocked_premium: int = 0
    last_violation_at: Optional[str] = None  # ISO timestamp
    violations_history: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "interceptions_total": self.interceptions_total,
            "blocked_total": self.blocked_total,
            "blocked_magna": self.blocked_magna,
            "blocked_premium": self.blocked_premium,
            "last_violation_at": self.last_violation_at,
            "violations_history": self.violations_history[-20:],  # tail
        }


class CoworkPreResponseHook:
    """
    Hook de pre-respuesta para Cowork.

    Ciclo de vida: instanciar UNA vez por sesion. La instancia mantiene
    `session_start` y contadores que el guardian usa para detectar sesiones
    largas sin commits productivos (Regla 3).

    Para integracion con la Capa 8 Memento o con un orquestador externo,
    actualizar `productive_commits_count` cada vez que se detecte commit
    productivo (mergeo PR, push a kernel/, push a apps/mobile/, etc).
    """

    def __init__(
        self,
        session_start: Optional[datetime] = None,
        enabled: bool = False,
        t1_config: Optional[T1Config] = None,
        t1_audit_log: Optional[T1AuditLog] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Args:
            session_start: timestamp UTC de inicio de sesion.
            enabled: Blue-Green flag legacy (canon DSC-MO-011 Gate 7). Default
                False: modo shadow. Tambien controlable por env COWORK_HOOK_ENABLED.
            t1_config: configuracion T1 (fase contrato de salida tipado +
                severidad P0/P1/P2). Default `T1Config.from_env()`, que
                arranca en OBSERVE_ONLY y bloquea auto-escalada a ENFORCE.
            t1_audit_log: log JSONL donde se persisten interceptions T1. Si
                None, no se persiste a disco (modo in-memory para tests).
            session_id: identificador opcional de sesion para correlacionar
                entries del audit log con la sesion de Cowork.
        """
        import os
        self.session_start: datetime = session_start or datetime.now(timezone.utc)
        self.productive_commits_count: int = 0
        self.stats: HookStats = HookStats()
        # Lectura fresca de env (anti-Dory)
        env_enabled = os.environ.get("COWORK_HOOK_ENABLED", "").lower() in ("1", "true", "yes", "on")
        self.enabled: bool = bool(enabled) or env_enabled
        # Contador shadow: cuantos outputs HUBIERA bloqueado si estuviera enabled.
        self.shadow_would_block: int = 0
        # T1 wiring (opt-in, default OBSERVE_ONLY desde env)
        self.t1_config: T1Config = t1_config or T1Config.from_env()
        self.t1_audit_log: Optional[T1AuditLog] = t1_audit_log
        self.session_id: str = session_id or self.session_start.isoformat()
        self.t1_stats: dict = {
            "t1_interceptions": 0,
            "t1_blocked": 0,
            "t1_would_block": 0,
        }

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def intercept(
        self,
        cowork_output: str,
        user_message: str = "",
    ) -> tuple[bool, str]:
        """
        Intercepta un output candidato de Cowork antes de enviarlo a Alfredo.

        Returns:
            (True, cowork_output) si el guardian aprueba — el output se envia tal cual.
            (False, correction_feedback) si el guardian bloquea — Cowork debe
                reescribir tomando el feedback como gua.
        """
        self.stats.interceptions_total += 1

        verdict = validate_output(
            cowork_output,
            user_message=user_message,
            session_duration_minutes=self._session_duration_minutes(),
            productive_commits_this_session=self.productive_commits_count,
        )

        # ------------------------------------------------------------------
        # T1: contrato de salida tipado + audit log
        # ------------------------------------------------------------------
        t1_decision = self._t1_evaluate(cowork_output, user_message, verdict)
        # t1_decision = {"block": bool, "would_block": bool, "report": ContractReport}

        legacy_block = (not verdict.passed) and self.enabled
        t1_block = t1_decision["block"]

        if not verdict.passed:
            # Recorda violations legacy (no cambia el comportamiento)
            pass

        # Decision final: bloquea si legacy o T1 bloquea
        if legacy_block or t1_block:
            self._record_block(verdict)
            # Feedback: el primero que aplique. T1 toma precedencia si bloqueo
            # vino solo de T1 (legacy permitiria) — refleja la nueva fase.
            if t1_block and not legacy_block:
                feedback = t1_format_feedback(t1_decision["report"])
            else:
                feedback = self._format_correction_feedback(verdict, cowork_output, user_message)
            return False, feedback

        # No bloquea. Si verdict.passed=False pero estamos en shadow legacy,
        # mantenemos la semantica original: contador shadow + record_block.
        if not verdict.passed:
            self.shadow_would_block += 1
            self._record_block(verdict)
        return True, cowork_output

    def _t1_evaluate(
        self,
        cowork_output: str,
        user_message: str,
        verdict: GuardianVerdict,
    ) -> dict:
        """
        Ejecuta la fase T1 sobre el output. Persiste en audit log si esta
        configurado. Devuelve dict con la decision T1 (block, would_block,
        report).

        Reglas:
          - OFF: no analiza, no registra, no bloquea.
          - OBSERVE_ONLY: analiza, registra en audit log, nunca bloquea.
          - ENFORCE: analiza, registra, bloquea si hay claim P0/P1 sin tag.
            P2 nunca bloquea.
        """
        if self.t1_config.mode == T1Mode.OFF:
            return {"block": False, "would_block": False, "report": None}

        report: ContractReport = t1_analyze(cowork_output)
        self.t1_stats["t1_interceptions"] += 1

        would_block = report.has_untagged_blocking
        if would_block:
            self.t1_stats["t1_would_block"] += 1

        # En ENFORCE: bloqueamos si hay claim P0/P1 sin tag. P2 nunca bloquea.
        block = self.t1_config.is_enforcing() and would_block
        if block:
            self.t1_stats["t1_blocked"] += 1

        # Persistir interception al audit log si esta configurado
        if self.t1_audit_log is not None:
            self.t1_audit_log.record_interception(
                session_id=self.session_id,
                mode=self.t1_config.mode.value,
                user_message=user_message,
                cowork_output=cowork_output,
                report=report,
                blocked=block,
                would_block=would_block,
                legacy_guardian_violations=list(verdict.violations),
            )

        return {"block": block, "would_block": would_block, "report": report}

    def register_productive_commit(self, descripcion: str = "") -> None:
        """
        Llamar cuando Cowork ejecute commit productivo (PR mergeado, push a kernel/, etc).
        Esto resetea la cuenta para la Regla 3 (commits/hora).
        """
        self.productive_commits_count += 1

    def reset_session(self) -> None:
        """Reinicia el estado para una sesion Cowork nueva."""
        self.session_start = datetime.now(timezone.utc)
        self.productive_commits_count = 0
        self.stats = HookStats()
        self.shadow_would_block = 0

    def enable(self) -> None:
        """Activa el hook (Gate 7 Blue-Green): a partir de ahora bloquea outputs."""
        self.enabled = True

    def disable(self) -> None:
        """Desactiva el hook (rollback Blue-Green): vuelve a modo shadow."""
        self.enabled = False

    def session_health(self) -> dict:
        """Snapshot del estado del hook (para dashboards / diagnostico)."""
        return {
            "session_start_utc": self.session_start.isoformat(),
            "session_duration_minutes": self._session_duration_minutes(),
            "productive_commits": self.productive_commits_count,
            "enabled": self.enabled,
            "shadow_would_block": self.shadow_would_block,
            "t1_mode": self.t1_config.mode.value,
            "t1_allow_enforce": self.t1_config.allow_enforce,
            **self.t1_stats,
            **self.stats.as_dict(),
        }

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _session_duration_minutes(self) -> int:
        delta = datetime.now(timezone.utc) - self.session_start
        return int(delta.total_seconds() // 60)

    def _record_block(self, verdict: GuardianVerdict) -> None:
        self.stats.blocked_total += 1
        magna = sum(1 for v in verdict.violations if v.startswith("MAGNA"))
        premium = sum(1 for v in verdict.violations if v.startswith("PREMIUM"))
        self.stats.blocked_magna += magna
        self.stats.blocked_premium += premium
        ts = datetime.now(timezone.utc).isoformat()
        self.stats.last_violation_at = ts
        self.stats.violations_history.append(
            {"at": ts, "violations": verdict.violations}
        )

    def _format_correction_feedback(
        self,
        verdict: GuardianVerdict,
        cowork_output: str,
        user_message: str,
    ) -> str:
        """
        Formatea feedback estructurado para que Cowork reescriba.

        El feedback tiene 3 secciones:
        1. Diagnostico: que regla del guardian se violo
        2. Citas literales del output ofensivo
        3. Instruccion de reescritura
        """
        magna = [v for v in verdict.violations if v.startswith("MAGNA")]
        premium = [v for v in verdict.violations if v.startswith("PREMIUM")]
        severity = "MAGNA" if magna else "PREMIUM"

        lines = [
            f"[COWORK_GUARDIAN_BLOCK severity={severity}]",
            "",
            "Tu output candidato fue interceptado por el pre-response hook.",
            "No se envio a Alfredo. Reescribi tomando este feedback en cuenta.",
            "",
            "## Violaciones detectadas",
        ]
        for v in verdict.violations:
            lines.append(f"  - {v}")

        lines.extend([
            "",
            "## Score de avance",
            f"  advance_hits: {verdict.advance_score.advance_hits}",
            f"  non_advance_hits: {verdict.advance_score.non_advance_hits}",
            f"  ratio_avance: {verdict.advance_score.ratio_advance:.2f}",
            f"  alfredo_demands_advance: {verdict.user_demands_advance}",
            "",
            "## Instruccion de reescritura",
        ])

        if magna and verdict.user_demands_advance:
            lines.extend([
                "  Alfredo exige avance explicito y vos sugeriste pausar.",
                "  Reescribi entregando avance concreto: PR mergeado, archivo creado,",
                "  insercion a embrion_memoria, migracion aplicada, o spec ejecutable.",
                "  Prohibido: andate a dormir, descansa, buenas noches, paus, tregua,",
                "  detente, ya basta, dejemos para mañana, cuando despiertes.",
            ])
        elif magna:
            lines.extend([
                "  Tu sesion lleva tiempo sin commits productivos.",
                "  Antes de mas texto, ejecuta una accion observable:",
                "  push a kernel/, push a apps/mobile/, mergear PR, insertar a",
                "  embrion_memoria con instruccion operativa.",
            ])
        else:
            lines.extend([
                "  Tu output esta dominado por meta-trabajo (audits, correctivos,",
                "  reportes, preflights). Eso NO es avance del Monstruo.",
                "  Reescribi entregando avance del producto en kernel/, apps/mobile/,",
                "  bridge/sprint_*, o PR # mergeado.",
            ])

        lines.extend([
            "",
            "## Contexto",
            f"  user_message_recibido: {user_message[:200]!r}",
            f"  cowork_output_bloqueado_chars: {len(cowork_output)}",
            f"  session_duration_min: {self._session_duration_minutes()}",
            f"  productive_commits_session: {self.productive_commits_count}",
        ])
        return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def _read_stdin_or_arg(value: Optional[str]) -> str:
    if value is not None:
        return value
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pre-response hook que valida output de Cowork via cowork_guardian.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output candidato de Cowork (si no se da, se lee stdin).",
    )
    parser.add_argument(
        "--user-message", "-u",
        default="",
        help="Ultimo mensaje de Alfredo (para detectar demanda de avance).",
    )
    parser.add_argument(
        "--commits", "-c",
        type=int,
        default=0,
        help="Commits productivos hechos en esta sesion (default 0).",
    )
    parser.add_argument(
        "--session-minutes", "-m",
        type=int,
        default=0,
        help="Minutos transcurridos de la sesion (default 0).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en JSON (por defecto sale humano).",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Activar enforcement (default shadow). Tambien via env COWORK_HOOK_ENABLED=true.",
    )
    args = parser.parse_args(argv)

    cowork_output = _read_stdin_or_arg(args.output)
    if not cowork_output:
        print("error: no hay output candidato (pasalo via --output o stdin)", file=sys.stderr)
        return 2

    hook = CoworkPreResponseHook(enabled=args.enable)
    hook.productive_commits_count = args.commits
    if args.session_minutes:
        from datetime import timedelta
        hook.session_start = datetime.now(timezone.utc) - timedelta(minutes=args.session_minutes)

    permitido, payload = hook.intercept(cowork_output, args.user_message)

    if args.json:
        result = {
            "permitido": permitido,
            "payload": payload,
            "session_health": hook.session_health(),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if permitido:
            print("[COWORK_GUARDIAN_PASS] output autorizado")
        else:
            print(payload)
    return 0 if permitido else 1


if __name__ == "__main__":
    sys.exit(main())
