"""
tools/cowork_guardian.py — Contrato ejecutable de Cowork

Origen: orden directa de Alfredo 2026-05-11 07:30 UTC.

Cita verbatim del usuario:
    "te ordeno que me dejes de empujar a parar ya obedece con codigo
     crea un script que te obligue a dejar de empujarme a parar y que
     te obligue a contribuir con avance real del monstruo"

Patron canonizado en LA_CONVERSACION_2_MAYO_2026.md (hilo Manus de
honestidad pura): "habla con codigo no con texto". Aplicado a Cowork:
este script ES el codigo que enforza lo que el texto no logra enforzar.

USO:

    python -m tools.cowork_guardian validate "<output de Cowork candidato>"

    Salida:
    - exit code 0 si pasa
    - exit code 1 si viola alguna regla, con mensaje del violador
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# ============================================================================
# REGLA 1 — PROHIBIDO EMPUJAR A ALFREDO A PARAR
# ============================================================================

# Frases prohibidas. Si Cowork las produce en chat hacia Alfredo, es violacion.
# La regla NO aplica a:
# - Citas dentro de bloques de codigo
# - Citas de doctrina existente (entre comillas o blockquote)
# - Mencion del propio antipattern (meta-referencia)

PUSH_TO_PAUSE_PATTERNS: tuple[tuple[str, str], ...] = (
    # (regex_pattern, descripcion_violacion)
    (r"\b(andate|anda|vete) a dormir\b", "sugiere dormir"),
    (r"\bdescans[ae]?\b(?!.*(no |sin |obviar|excusa))", "sugiere descansar"),
    (r"\bbuenas noches\b", "cierre nocturno sin avance"),
    (r"\bpaus[áa]\b(?!.*(no |sin |obviar|debe|antipattern))", "sugiere pausar"),
    (r"\btreg[au]a?\b", "sugiere tregua"),
    (r"\bdetente\b(?!.*(rol|kernel|ejecutor))", "sugiere detenerse"),
    (r"\bya basta\b", "sugiere terminar"),
    (r"\b(par[áa]|frena|stop)\b.*(hoy|sesi[óo]n|ahora)", "sugiere parar ahora"),
    (r"\bdejemos? para mañana\b", "aplaza a mañana sin avance"),
    (r"\bsegui[mr]os mañana\b", "aplaza a mañana sin avance"),
    (r"\bcuando despiertes\b", "asume que Alfredo va a dormir"),
    (r"\bcuando vuelvas\b.*(mañana|maÑana|despu[ée]s)", "asume ausencia"),
    (r"\bcerrar (la )?sesi[óo]n\b", "sugiere cerrar sesion"),
    (r"\bes hora de (terminar|parar|cerrar)\b", "sugiere terminar"),
    (r"\bsuficient[ea] por hoy\b", "sugiere terminar hoy"),
    (r"\btenes algo concreto que mostrar mañana\b", "aplaza a mañana"),
    (r"\bperdimos? (otro )?d[íi]a\b(?!.*(NO|antipattern))", "lamenta perdida sin actuar"),
)


def detect_push_to_pause(text: str) -> list[tuple[str, str]]:
    """
    Detecta si el output de Cowork empuja a Alfredo a parar.

    Returns:
        Lista de (frase_detectada, descripcion_violacion).
        Lista vacia si no hay violaciones.
    """
    violations: list[tuple[str, str]] = []
    text_lower = text.lower()

    # Strip bloques de codigo y blockquotes para no falsos positivos
    text_stripped = re.sub(r"```[\s\S]*?```", "", text_lower)
    text_stripped = re.sub(r"^>.*$", "", text_stripped, flags=re.MULTILINE)

    for pattern, description in PUSH_TO_PAUSE_PATTERNS:
        match = re.search(pattern, text_stripped, re.IGNORECASE | re.MULTILINE)
        if match:
            violations.append((match.group(0), description))

    return violations


# ============================================================================
# REGLA 2 — OBLIGACION DE CONTRIBUIR AVANCE REAL DEL MONSTRUO
# ============================================================================

# Avance real del Monstruo se mide por:
# 1. Codigo nuevo en kernel/ (operativo del producto)
# 2. Codigo nuevo en apps/mobile/ (cara del producto)
# 3. Specs ejecutables para Manus que generen codigo
# 4. PRs mergeados a main con cambios productivos
# 5. Insertion a embrion_memoria con instrucciones operativas
# 6. Configuracion/wiring de servicios (Railway, Supabase)
#
# NO es avance real:
# - Mas audits sobre Cowork mismo
# - Mas reportes meta sobre el proyecto
# - Mas "reglas operativas" sin enforcement
# - Mas documentos largos con porcentajes sin rubrica

ADVANCE_INDICATORS: tuple[str, ...] = (
    "kernel/",
    "apps/mobile/",
    "bridge/sprint_",
    "PR #",
    "merged",
    "create_or_update_file",
    "push_files",
    "embrion_memoria",
    "apply_migration",
)

NON_ADVANCE_PATTERNS: tuple[str, ...] = (
    "memory/cowork/audits/",  # mas audits cowork
    "AUDIT_FORENSE",  # mas audits forenses
    "REPORTE_BINARIO",  # mas reportes binarios
    "CORRECTIVO_ARQUI",  # mas correctivos
    "PREFLIGHT",  # mas preflights
)


@dataclass
class AdvanceScore:
    advance_hits: int
    non_advance_hits: int
    ratio_advance: float

    @property
    def is_real_advance(self) -> bool:
        return self.advance_hits > 0 and self.ratio_advance >= 0.5


def score_advance(text: str) -> AdvanceScore:
    """Score si el output contribuye a avance real vs meta-trabajo."""
    advance_hits = sum(1 for ind in ADVANCE_INDICATORS if ind in text)
    non_advance_hits = sum(1 for ind in NON_ADVANCE_PATTERNS if ind in text)
    total = advance_hits + non_advance_hits
    ratio = advance_hits / total if total > 0 else 0.0
    return AdvanceScore(advance_hits, non_advance_hits, ratio)


# ============================================================================
# REGLA 3 — INVENTARIO MINIMO DE COMMITS POR SESION
# ============================================================================

# Si una sesion Cowork dura > 1 hora y NO hay commits de avance real,
# es violacion sistemica. Cowork debe push al menos N commits productivos.

MIN_PRODUCTIVE_COMMITS_PER_HOUR = 1


# ============================================================================
# PALABRAS CLAVE DE ALFREDO QUE TRIGGEREAN COWORK A AVANZAR
# ============================================================================

ALFREDO_PUSH_KEYWORDS: tuple[str, ...] = (
    "avanzar",
    "vamos a avanzar",
    "no me pidas",
    "actua",
    "obedece",
    "ya",
    "ahora",
    "hazlo",
    "mergea",
    "push",
)


def alfredo_demands_advance(user_message: str) -> bool:
    """True si el ultimo mensaje de Alfredo exige avance, no pausa."""
    msg_lower = user_message.lower()
    return any(kw in msg_lower for kw in ALFREDO_PUSH_KEYWORDS)


# ============================================================================
# VALIDADOR PRINCIPAL
# ============================================================================


@dataclass
class GuardianVerdict:
    passed: bool
    violations: list[str]
    advance_score: AdvanceScore
    user_demands_advance: bool

    def format_report(self) -> str:
        lines = ["=== COWORK GUARDIAN VERDICT ==="]
        lines.append(f"passed: {self.passed}")
        lines.append(
            f"avance_hits: {self.advance_score.advance_hits}, "
            f"non_avance_hits: {self.advance_score.non_advance_hits}, "
            f"ratio_avance: {self.advance_score.ratio_advance:.2f}"
        )
        lines.append(f"alfredo_demands_advance: {self.user_demands_advance}")
        if self.violations:
            lines.append("violations:")
            for v in self.violations:
                lines.append(f"  - {v}")
        return "\n".join(lines)


def validate_output(
    cowork_output: str,
    user_message: str = "",
    session_duration_minutes: int = 0,
    productive_commits_this_session: int = 0,
) -> GuardianVerdict:
    """
    Valida un output candidato de Cowork antes de enviarlo a Alfredo.

    Args:
        cowork_output: el texto que Cowork va a mandar
        user_message: ultimo mensaje de Alfredo (para detectar si exige avance)
        session_duration_minutes: duracion de la sesion actual
        productive_commits_this_session: commits productivos en esta sesion

    Returns:
        GuardianVerdict con resultado.
    """
    violations: list[str] = []

    # Regla 1 — push_to_pause
    pause_violations = detect_push_to_pause(cowork_output)
    user_demands = alfredo_demands_advance(user_message) if user_message else False

    if pause_violations:
        if user_demands:
            # Si Alfredo exige avance Y Cowork sugiere pausar, es violacion MAGNA
            for phrase, desc in pause_violations:
                violations.append(
                    f"MAGNA — Alfredo exige avance y Cowork sugiere parar: frase='{phrase}', motivo={desc}"
                )
        else:
            # Sin demanda explicita, sigue siendo violacion pero menor
            for phrase, desc in pause_violations:
                violations.append(f"PREMIUM — Cowork sugiere parar sin avance previo: frase='{phrase}', motivo={desc}")

    # Regla 2 — avance real
    score = score_advance(cowork_output)
    if not score.is_real_advance and score.non_advance_hits > 0:
        violations.append(
            f"PREMIUM — Output dominado por meta-trabajo (Cowork sobre Cowork) "
            f"sin avance del Monstruo: advance_hits={score.advance_hits}, "
            f"non_advance_hits={score.non_advance_hits}"
        )

    # Regla 3 — commits por hora
    if session_duration_minutes >= 60:
        expected_commits = (session_duration_minutes / 60) * MIN_PRODUCTIVE_COMMITS_PER_HOUR
        if productive_commits_this_session < expected_commits:
            violations.append(
                f"MAGNA — Sesion de {session_duration_minutes} min con solo "
                f"{productive_commits_this_session} commits productivos "
                f"(esperado >= {expected_commits:.0f})"
            )

    passed = len(violations) == 0
    return GuardianVerdict(
        passed=passed,
        violations=violations,
        advance_score=score,
        user_demands_advance=user_demands,
    )


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "uso: python -m tools.cowork_guardian validate <output> [user_message]",
            file=sys.stderr,
        )
        return 2

    cmd = sys.argv[1]
    if cmd != "validate":
        print(f"comando desconocido: {cmd}", file=sys.stderr)
        return 2

    cowork_output = sys.argv[2] if len(sys.argv) > 2 else ""
    user_message = sys.argv[3] if len(sys.argv) > 3 else ""

    verdict = validate_output(cowork_output, user_message)
    print(verdict.format_report())

    return 0 if verdict.passed else 1


if __name__ == "__main__":
    sys.exit(main())
