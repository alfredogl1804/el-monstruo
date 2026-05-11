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
    ) -> None:
        """
        Args:
            session_start: timestamp UTC de inicio de sesion.
            enabled: Blue-Green flag (canon DSC-MO-011 Gate 7). Default False:
                el hook se construye pero NO bloquea outputs (modo shadow).
                Activacion gradual via `enable()` despues de verificar que no
                rompe runtime existente. Tambien controlable por env var
                COWORK_HOOK_ENABLED=true.
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

        if verdict.passed:
            return True, cowork_output

        # Modo shadow (enabled=False): registramos lo que HABRiA bloqueado
        # pero dejamos pasar el output. Permite calibrar antes de activar.
        if not self.enabled:
            self.shadow_would_block += 1
            self._record_block(verdict)
            return True, cowork_output

        self._record_block(verdict)
        feedback = self._format_correction_feedback(verdict, cowork_output, user_message)
        return False, feedback

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
