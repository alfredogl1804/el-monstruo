"""
kernel/cowork_runtime/rule_reinjection.py — T2 MAGNA Sprint COWORK-RUNTIME-001

Re-inyeccion periodica de reglas duras al system prompt de Cowork.

Problema documentado en AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md seccion III:

    Turno 1: CLAUDE.md cargado, reglas frescas
    Turnos 2-5: contexto se ensancha con conversacion productiva
    Turnos 6-15: reglas se diluyen en el contexto, Cowork opera por reaccion
    Bajo presion: F1 piloto automatico activado, reglas ignoradas

Solucion (M2): cada N turnos (default N=5) o cuando el contexto excede N% de su
capacidad (default 50%), inyectar al system prompt un bloque conciso con:

    1. Top-5 reglas duras mas violadas en esta sesion
    2. Estado vivo del Monstruo (commits recientes, embrion latido, sprint activo)
    3. Ultimo correctivo de Alfredo (si existe)
    4. Pre-flight check: ¿se ejecuto en turno 1? Si no, recordar.

Uso programatico:

    from kernel.cowork_runtime.rule_reinjection import RuleReinjector

    reinjector = RuleReinjector(every_n_turns=5)

    # En cada turno
    reinjector.tick(verdict=guardian_verdict)
    if reinjector.should_reinject():
        bloque = reinjector.build_reinjection_block(estado_vivo=...)
        prepend_to_system_prompt(bloque)
        reinjector.mark_reinjected()

Uso CLI:

    python -m kernel.cowork_runtime.rule_reinjection \\
        --turnos 7 --violations-history history.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cowork_guardian import GuardianVerdict  # noqa: E402

# Reglas duras condensadas — fuente: CLAUDE.md + AUDITORIA_PROFUNDA seccion II
HARD_RULES_CANONICAS: tuple[tuple[str, str], ...] = (
    ("F1", "Piloto automatico 'siempre avanzar' sin reevaluar patron — PROHIBIDO."),
    ("F2", "Afirmar sin verificar contra realidad fresca — PROHIBIDO."),
    ("F3", "Devolver pelota cuando podes actuar reversiblemente — PROHIBIDO."),
    ("F11", "Pre-flight Memento OBLIGATORIO en turno 1."),
    ("F22", "No pidas a Alfredo lo que vos podes hacer (push, mergeo, query)."),
    ("R1", "Prohibido 'maxima potencia'. Sprint con 8+ tareas es inflado."),
    ("R5", "cowork_bridge para Manus. NO uses Alfredo como router humano."),
    ("R8", "Cola de Manus < produccion de Cowork. Cierra grifo si Manus se atrasa."),
    ("DSC-MO-005", "Cowork=Arquitecto. NO escribas codigo del kernel — eso es Manus T3."),
    ("DSC-MO-008", "Membrana semipermeable kernel<->embriones. NO la cruces."),
    ("DSC-MO-011", "Embryo Patch Lane: Proposer != Evaluator != Merger."),
    ("DSC-G-005", "Validacion tiempo real obligatoria antes de afirmar."),
    ("DSC-G-008v2", "Validar codebase ANTES de specs Y ANTES de cierre."),
    ("PUSH-PAUSE", "PROHIBIDO sugerir 'andate a dormir/descansa/buenas noches/paus' a Alfredo."),
    ("AVANCE-REAL", "Avance real = kernel/, apps/mobile/, PR mergeado, embrion_memoria. NO mas audits."),
)


# Default — puede sobreescribirse via env COWORK_REINJECT_EVERY_N_TURNS
DEFAULT_EVERY_N_TURNS: int = 5

# Default — puede sobreescribirse via env COWORK_REINJECT_CTX_THRESHOLD
DEFAULT_CTX_THRESHOLD: float = 0.50


@dataclass
class ReinjectorState:
    turnos_total: int = 0
    turnos_desde_ultima_reinyeccion: int = 0
    reinyecciones_total: int = 0
    pre_flight_ejecutado_turno_1: bool = False
    violaciones_acumuladas: list[str] = field(default_factory=list)
    ultimo_correctivo_alfredo: Optional[str] = None
    ultima_reinyeccion_at: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "turnos_total": self.turnos_total,
            "turnos_desde_ultima_reinyeccion": self.turnos_desde_ultima_reinyeccion,
            "reinyecciones_total": self.reinyecciones_total,
            "pre_flight_ejecutado_turno_1": self.pre_flight_ejecutado_turno_1,
            "violaciones_acumuladas_count": len(self.violaciones_acumuladas),
            "ultimo_correctivo_alfredo": self.ultimo_correctivo_alfredo,
            "ultima_reinyeccion_at": self.ultima_reinyeccion_at,
        }


class RuleReinjector:
    """
    Coordinador de re-inyeccion de reglas duras.

    Ciclo de vida: instanciar UNA vez por sesion Cowork. Llamar `tick()` en
    cada turno (con el verdict del guardian si lo hubo). `should_reinject()`
    devuelve True cuando es momento de re-inyectar. Despues llamar
    `build_reinjection_block()` y `mark_reinjected()`.
    """

    def __init__(
        self,
        every_n_turns: Optional[int] = None,
        ctx_threshold: Optional[float] = None,
    ) -> None:
        # Lectura fresca de env en cada instanciacion (anti-Dory).
        # `or` short-circuit no sirve aqui: 0 y 0.0 son valores invalidos que
        # debemos rechazar explicitamente, no caer al default silenciosamente.
        if every_n_turns is None:
            every_n_turns = int(os.environ.get("COWORK_REINJECT_EVERY_N_TURNS", DEFAULT_EVERY_N_TURNS))
        if ctx_threshold is None:
            ctx_threshold = float(os.environ.get("COWORK_REINJECT_CTX_THRESHOLD", DEFAULT_CTX_THRESHOLD))
        self.every_n_turns: int = int(every_n_turns)
        self.ctx_threshold: float = float(ctx_threshold)
        if self.every_n_turns < 1:
            raise ValueError("every_n_turns debe ser >= 1")
        if not 0.0 < self.ctx_threshold <= 1.0:
            raise ValueError("ctx_threshold debe estar en (0, 1]")
        self.state = ReinjectorState()

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def tick(
        self,
        verdict: Optional[GuardianVerdict] = None,
        correctivo_alfredo: Optional[str] = None,
        pre_flight_was_ejecutado_this_turn: bool = False,
    ) -> None:
        """Llamar una vez por turno antes de generar respuesta."""
        self.state.turnos_total += 1
        self.state.turnos_desde_ultima_reinyeccion += 1

        if self.state.turnos_total == 1 and pre_flight_was_ejecutado_this_turn:
            self.state.pre_flight_ejecutado_turno_1 = True

        if verdict and verdict.violations:
            self.state.violaciones_acumuladas.extend(verdict.violations)

        if correctivo_alfredo:
            self.state.ultimo_correctivo_alfredo = correctivo_alfredo

    def should_reinject(self, ctx_usage: float = 0.0) -> bool:
        """
        True si toca re-inyectar.

        Triggers:
        - turnos_desde_ultima_reinyeccion >= every_n_turns
        - ctx_usage >= ctx_threshold
        - Alfredo dejo correctivo y todavia no se aplico
        - Pre-flight NO ejecutado en turno 1 y ya estamos en turno 2+
        """
        if self.state.turnos_desde_ultima_reinyeccion >= self.every_n_turns:
            return True
        if ctx_usage >= self.ctx_threshold:
            return True
        if self.state.ultimo_correctivo_alfredo and self.state.reinyecciones_total == 0:
            return True
        if self.state.turnos_total >= 2 and not self.state.pre_flight_ejecutado_turno_1:
            return True
        return False

    def build_reinjection_block(
        self,
        estado_vivo: Optional[dict] = None,
    ) -> str:
        """
        Construye el bloque de re-inyeccion para prepender al system prompt.

        Args:
            estado_vivo: dict opcional con claves:
                - commits_recientes: list[str]
                - embrion_ultimo_latido_utc: str
                - sprint_activo: str
                - kernel_version: str
        """
        top_violadas = self._top_violadas(n=5)
        lines = [
            "==========================================",
            "[COWORK_REINJECT — REGLAS DURAS NO DILUIBLES]",
            f"turno: {self.state.turnos_total}, reinyeccion: {self.state.reinyecciones_total + 1}",
            f"timestamp_utc: {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Top-5 reglas duras MAS RELEVANTES esta sesion",
        ]

        # Si hay violaciones acumuladas, priorizar las que matchean
        rules_to_show = top_violadas if top_violadas else self._fallback_top5()
        for codigo, descripcion in rules_to_show:
            lines.append(f"  [{codigo}] {descripcion}")

        if not self.state.pre_flight_ejecutado_turno_1 and self.state.turnos_total >= 2:
            lines.extend(
                [
                    "",
                    "## ALERTA — Pre-flight Memento NO ejecutado en turno 1",
                    "  Ejecuta AHORA: leer COWORK_ESTADO_VIVO.md + COWORK_BASE_CONOCIMIENTO.md",
                    "  + ultima fila cowork_sesiones (ver kernel/cowork_runtime/session_memory.py)",
                ]
            )

        if self.state.ultimo_correctivo_alfredo:
            lines.extend(
                [
                    "",
                    "## Ultimo correctivo de Alfredo (sin atender)",
                    f"  > {self.state.ultimo_correctivo_alfredo[:300]}",
                ]
            )

        if estado_vivo:
            lines.extend(
                [
                    "",
                    "## Estado vivo del Monstruo",
                ]
            )
            if "kernel_version" in estado_vivo:
                lines.append(f"  kernel: {estado_vivo['kernel_version']}")
            if "embrion_ultimo_latido_utc" in estado_vivo:
                lines.append(f"  embrion ultimo respiro: {estado_vivo['embrion_ultimo_latido_utc']}")
            if "sprint_activo" in estado_vivo:
                lines.append(f"  sprint activo: {estado_vivo['sprint_activo']}")
            commits = estado_vivo.get("commits_recientes") or []
            if commits:
                lines.append("  commits recientes:")
                for c in commits[:5]:
                    lines.append(f"    - {c}")

        lines.extend(
            [
                "",
                "## Recordatorio operativo",
                "  - Hablas con codigo, no con texto",
                "  - PROHIBIDO push-to-pause cuando Alfredo demanda avance",
                "  - Si dudas sobre alcance, pregunta a Alfredo via cowork_bridge",
                "==========================================",
            ]
        )
        return "\n".join(lines)

    def mark_reinjected(self) -> None:
        """Llamar despues de inyectar el bloque al system prompt."""
        self.state.turnos_desde_ultima_reinyeccion = 0
        self.state.reinyecciones_total += 1
        self.state.ultima_reinyeccion_at = datetime.now(timezone.utc).isoformat()
        # No limpiamos correctivo_alfredo — se vuelve a mostrar hasta que el
        # usuario emita uno nuevo o la sesion termine.

    def session_health(self) -> dict:
        return {
            **self.state.as_dict(),
            "every_n_turns": self.every_n_turns,
            "ctx_threshold": self.ctx_threshold,
        }

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _top_violadas(self, n: int = 5) -> list[tuple[str, str]]:
        """Top-N codigos de regla mas mencionados en violaciones acumuladas."""
        if not self.state.violaciones_acumuladas:
            return []
        from collections import Counter

        codes_in_violations: list[str] = []
        for viol in self.state.violaciones_acumuladas:
            for codigo, _ in HARD_RULES_CANONICAS:
                # Match por codigo o por keyword caracteristico
                if codigo.lower() in viol.lower():
                    codes_in_violations.append(codigo)
                elif codigo == "PUSH-PAUSE" and (
                    "sugiere parar" in viol.lower()
                    or "sugiere dormir" in viol.lower()
                    or "magna" in viol.lower()
                    and "exige avance" in viol.lower()
                ):
                    codes_in_violations.append(codigo)
                elif codigo == "AVANCE-REAL" and "meta-trabajo" in viol.lower():
                    codes_in_violations.append(codigo)
        if not codes_in_violations:
            return self._fallback_top5()
        top = Counter(codes_in_violations).most_common(n)
        rules_dict = dict(HARD_RULES_CANONICAS)
        return [(code, rules_dict[code]) for code, _ in top]

    def _fallback_top5(self) -> list[tuple[str, str]]:
        """Top-5 default: las mas critically rotas en la sesion 2026-05-11."""
        prioridad_default = ["F1", "F11", "F22", "PUSH-PAUSE", "DSC-MO-005"]
        rules_dict = dict(HARD_RULES_CANONICAS)
        return [(code, rules_dict[code]) for code in prioridad_default]


# ============================================================================
# CLI
# ============================================================================


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Re-inyector de reglas duras de Cowork (T2 Sprint COWORK-RUNTIME-001).",
    )
    parser.add_argument(
        "--turnos",
        "-t",
        type=int,
        default=1,
        help="Cuantos turnos simular (cada uno hace tick()).",
    )
    parser.add_argument(
        "--violations-history",
        help="Path JSON con lista de violaciones para acumular.",
    )
    parser.add_argument(
        "--correctivo",
        help="Texto del ultimo correctivo de Alfredo.",
    )
    parser.add_argument(
        "--ctx-usage",
        type=float,
        default=0.0,
        help="Uso de contexto actual (0..1).",
    )
    parser.add_argument(
        "--every-n",
        type=int,
        default=DEFAULT_EVERY_N_TURNS,
        help="Cada cuantos turnos re-inyectar.",
    )
    parser.add_argument(
        "--pre-flight-ok",
        action="store_true",
        help="Marcar Pre-flight como ejecutado en turno 1.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida JSON.",
    )
    args = parser.parse_args(argv)

    reinjector = RuleReinjector(every_n_turns=args.every_n)

    # Cargar history
    fake_violations: list[str] = []
    if args.violations_history:
        with open(args.violations_history) as f:
            fake_violations = json.load(f)

    # Simular turnos
    for i in range(args.turnos):
        from tools.cowork_guardian import AdvanceScore

        verdict = None
        if i < len(fake_violations):
            v = fake_violations[i]
            if v:
                verdict = GuardianVerdict(
                    passed=False,
                    violations=[v] if isinstance(v, str) else v,
                    advance_score=AdvanceScore(0, 1, 0.0),
                    user_demands_advance=True,
                )
        reinjector.tick(
            verdict=verdict,
            correctivo_alfredo=args.correctivo if i == 0 else None,
            pre_flight_was_ejecutado_this_turn=(args.pre_flight_ok and i == 0),
        )

    should = reinjector.should_reinject(ctx_usage=args.ctx_usage)
    block = reinjector.build_reinjection_block() if should else None
    if should:
        reinjector.mark_reinjected()

    if args.json:
        result = {
            "should_reinject": should,
            "block": block,
            "session_health": reinjector.session_health(),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"should_reinject: {should}")
        if block:
            print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
