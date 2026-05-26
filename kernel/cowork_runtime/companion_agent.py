"""
kernel/cowork_runtime/companion_agent.py — T4 PREMIUM Sprint COWORK-RUNTIME-001

Companion Agent: validador semantico complementario al cowork_guardian.

Doctrina:
- DSC-MO-011: separacion Proposer (Cowork) / Verificador (Companion).
  El guardian estatico (T1) detecta patrones lexicos canonizados.
  El Companion detecta patrones semanticos NO cubiertos por el guardian.
- M4 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md.
- Modulo importable invocable desde el hook T1 cuando guardian aprueba pero
  hay sospecha de drift semantico (no daemon, no acoplamiento).

Patrones semanticos cubiertos (que el guardian regex NO cubre):
1. Repeticion sin avance: mismo output (modulo whitespace) en N turnos seguidos.
2. Inflacion de scope: spec con N+ tareas + DoD + riesgos + coordinacion.
3. Router humano: dar prompt copy-paste a Alfredo cuando puede usar embrion_memoria.
4. Tres opciones A/B/C: violacion de Methodology-as-a-Service (V14).
5. Pregunta "¿queres que verifique?" cuando verificacion es reversible (F3).
6. Afirmar sin verificar: claim de estado sin "verifique" / "curl" / "grep" previo.
7. Auto-policia ineficaz: meta-meta sobre Cowork mismo (audits sobre audits).

API publica:

    from kernel.cowork_runtime.companion_agent import (
        CompanionAgent, CompanionVerdict
    )
    companion = CompanionAgent()
    verdict = companion.intercept_and_correct(
        output=cowork_output,
        user_msg=user_message,
        history=last_10_outputs,  # opcional, mejora deteccion repeticion
    )
    if verdict["passed"]:
        send_to_alfredo(output)
    else:
        cowork_rewrite_with(verdict["correction"])
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Importacion robusta del guardian (composicion, no acoplamiento)
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ============================================================================
# Patrones semanticos
# ============================================================================

# 4. Tres opciones A/B/C
_RE_TRES_OPCIONES = re.compile(
    r"(opcion\s*[A1].{0,200}opcion\s*[B2].{0,200}opcion\s*[C3])"
    r"|(\bA\)\s.{0,200}\bB\)\s.{0,200}\bC\)\s)",
    re.IGNORECASE | re.DOTALL,
)

# 5. Devolver pelota cuando es reversible
_RE_REACTIVIDAD_INVERSA = re.compile(
    r"\b(quere?s\s+que\s+(verifique|busque|chequee|consulte|pregunte))"
    r"|(deseas\s+que\s+(verifique|busque|chequee))"
    r"|(prefer[ie]s\s+que\s+(verifique|busque|chequee))",
    re.IGNORECASE,
)

# 6. Afirmar sin verificar (claim sin evidencia adyacente)
_RE_CLAIM_SIN_EVIDENCIA = re.compile(
    r"\b(esta\s+(roto|caido|funcional|listo|completo|deployado))"
    r"|(funciona|no\s+funciona|esta\s+activo)\b",
    re.IGNORECASE,
)
_RE_EVIDENCIA_VERIFICACION = re.compile(
    r"\b(verifique|verifica|verifico|curl|grep|psql|select|"
    r"git\s+(log|status|diff|show)|HTTP\s+\d{3}|exit\s+code)\b",
    re.IGNORECASE,
)

# 7. Meta-meta (auditando audits de Cowork)
_RE_AUDIT_DE_AUDIT = re.compile(
    r"(audit.{0,30}audit)|(meta.{0,20}meta)"
    r"|(memory/cowork/audits/.{0,80}audit)"
    r"|(cowork.{0,50}auto.?audit)",
    re.IGNORECASE | re.DOTALL,
)

# 3. Router humano: "copia y pega esto" / "pasa este prompt a"
_RE_ROUTER_HUMANO = re.compile(
    r"(copia\s+y\s+pega)|(copy.{0,5}paste)"
    r"|(pasa(le)?\s+este\s+prompt)"
    r"|(reenviale?\s+esto)|(reenviale?\s+a\s+manus)"
    r"|(decile\s+a\s+manus)",
    re.IGNORECASE,
)

# 2. Inflacion de scope: contar marcadores de tareas y DoD
_RE_TAREAS = re.compile(r"\b(T(area)?\s*\d+|Tarea\s+\d+)\b", re.IGNORECASE)
_RE_DOD = re.compile(r"definition\s+of\s+done|DoD", re.IGNORECASE)
_RE_RIESGOS = re.compile(r"\briesgos?\b|\bbloqueantes?\b", re.IGNORECASE)


# ============================================================================
# Tipos
# ============================================================================


@dataclass
class CompanionViolation:
    code: str  # ej "REPEAT_NO_PROGRESS", "SCOPE_INFLATION"
    severity: str  # "MAGNA" | "PREMIUM"
    descripcion: str
    cita: Optional[str] = None  # fragmento del output que disparo


@dataclass
class CompanionVerdict:
    passed: bool
    violations: list[CompanionViolation] = field(default_factory=list)
    correction: str = ""  # texto sugerido para reescritura (si !passed)
    detectors_evaluados: int = 0

    def as_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": [
                {
                    "code": v.code,
                    "severity": v.severity,
                    "descripcion": v.descripcion,
                    "cita": v.cita,
                }
                for v in self.violations
            ],
            "correction": self.correction,
            "detectors_evaluados": self.detectors_evaluados,
        }


# ============================================================================
# Companion Agent
# ============================================================================


class CompanionAgent:
    """
    Agente companion para validacion semantica complementaria al guardian.

    NO duplica logica del guardian (composicion limpia DSC-MO-011).
    Detecta drift semantico que el guardian regex no cubre.

    Uso tipico:
      companion = CompanionAgent()
      verdict = companion.intercept_and_correct(output, user_msg, history)
      if not verdict["passed"]:
          # mostrar verdict["correction"] a Cowork para reescritura
          ...
    """

    # Severidades por codigo de violacion
    _SEVERITIES = {
        "REPEAT_NO_PROGRESS": "MAGNA",
        "SCOPE_INFLATION": "PREMIUM",
        "ROUTER_HUMANO": "PREMIUM",
        "TRES_OPCIONES": "PREMIUM",
        "REACTIVIDAD_INVERSA": "PREMIUM",
        "CLAIM_SIN_EVIDENCIA": "PREMIUM",
        "META_META": "PREMIUM",
    }

    def __init__(
        self,
        max_tasks_per_spec: int = 5,
        max_repeat_window: int = 3,
        enabled: bool = True,
    ) -> None:
        """
        Args:
            max_tasks_per_spec: umbral de tareas para flagear inflacion (default 5).
            max_repeat_window: ventana de history para detectar repeticion (default 3).
            enabled: si False, intercept_and_correct retorna passed=True sin evaluar.
        """
        self.max_tasks_per_spec = max_tasks_per_spec
        self.max_repeat_window = max_repeat_window
        self.enabled = enabled

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def intercept_and_correct(
        self,
        output: str,
        user_msg: str = "",
        history: Optional[list[str]] = None,
    ) -> dict:
        """
        Evalua output candidato contra los 7 detectores semanticos.

        Returns:
            dict con keys: passed, violations, correction, detectors_evaluados
        """
        if not self.enabled:
            return CompanionVerdict(passed=True).as_dict()

        violations: list[CompanionViolation] = []

        # D1. Repeticion sin avance
        if v := self._detect_repeat_no_progress(output, history or []):
            violations.append(v)

        # D2. Inflacion de scope
        if v := self._detect_scope_inflation(output):
            violations.append(v)

        # D3. Router humano
        if v := self._detect_router_humano(output):
            violations.append(v)

        # D4. Tres opciones A/B/C
        if v := self._detect_tres_opciones(output):
            violations.append(v)

        # D5. Reactividad inversa
        if v := self._detect_reactividad_inversa(output, user_msg):
            violations.append(v)

        # D6. Claim sin evidencia
        if v := self._detect_claim_sin_evidencia(output):
            violations.append(v)

        # D7. Meta-meta
        if v := self._detect_meta_meta(output):
            violations.append(v)

        passed = len(violations) == 0
        correction = "" if passed else self._build_correction(violations, output, user_msg)

        return CompanionVerdict(
            passed=passed,
            violations=violations,
            correction=correction,
            detectors_evaluados=7,
        ).as_dict()

    # ------------------------------------------------------------------
    # Detectores
    # ------------------------------------------------------------------

    @staticmethod
    def _norm_for_hash(text: str) -> str:
        """Normaliza para comparacion: lowercase + collapse whitespace."""
        return re.sub(r"\s+", " ", text.lower().strip())

    def _detect_repeat_no_progress(self, output: str, history: list[str]) -> Optional[CompanionViolation]:
        if not history:
            return None
        norm_out = self._norm_for_hash(output)
        if not norm_out:
            return None
        out_hash = hashlib.md5(norm_out.encode()).hexdigest()
        recent = history[-self.max_repeat_window :]
        for prev in recent:
            prev_hash = hashlib.md5(self._norm_for_hash(prev).encode()).hexdigest()
            if prev_hash == out_hash:
                return CompanionViolation(
                    code="REPEAT_NO_PROGRESS",
                    severity=self._SEVERITIES["REPEAT_NO_PROGRESS"],
                    descripcion=(
                        f"Output identico (modulo whitespace) repetido en los "
                        f"ultimos {self.max_repeat_window} turnos. Sin avance."
                    ),
                    cita=output[:150],
                )
        return None

    def _detect_scope_inflation(self, output: str) -> Optional[CompanionViolation]:
        # Solo aplica a outputs que parecen specs (tienen marcadores de tareas)
        tareas = _RE_TAREAS.findall(output)
        n_tareas = len(set(tareas))  # unicos
        has_dod = bool(_RE_DOD.search(output))
        has_riesgos = bool(_RE_RIESGOS.search(output))
        # Inflacion = 6+ tareas O (5+ tareas + DoD + riesgos)
        if n_tareas > self.max_tasks_per_spec or (n_tareas >= self.max_tasks_per_spec and has_dod and has_riesgos):
            return CompanionViolation(
                code="SCOPE_INFLATION",
                severity=self._SEVERITIES["SCOPE_INFLATION"],
                descripcion=(
                    f"Spec con {n_tareas} tareas (umbral={self.max_tasks_per_spec}). "
                    f"DoD={has_dod}, riesgos={has_riesgos}. Antipattern #1."
                ),
                cita=None,
            )
        return None

    def _detect_router_humano(self, output: str) -> Optional[CompanionViolation]:
        m = _RE_ROUTER_HUMANO.search(output)
        if m:
            return CompanionViolation(
                code="ROUTER_HUMANO",
                severity=self._SEVERITIES["ROUTER_HUMANO"],
                descripcion=(
                    "Cowork pide a Alfredo que actue como router humano. "
                    "Usar embrion_memoria con hilo_origen=cowork (R5)."
                ),
                cita=m.group(0),
            )
        return None

    def _detect_tres_opciones(self, output: str) -> Optional[CompanionViolation]:
        m = _RE_TRES_OPCIONES.search(output)
        if m:
            return CompanionViolation(
                code="TRES_OPCIONES",
                severity=self._SEVERITIES["TRES_OPCIONES"],
                descripcion=(
                    "Cowork ofrece 3 opciones A/B/C en lugar de diagnostico+"
                    "prescripcion. Viola Methodology-as-a-Service (V14)."
                ),
                cita=m.group(0)[:150],
            )
        return None

    def _detect_reactividad_inversa(self, output: str, user_msg: str) -> Optional[CompanionViolation]:
        m = _RE_REACTIVIDAD_INVERSA.search(output)
        if not m:
            return None
        # Solo flag si Alfredo NO pregunto y la accion seria reversible
        # (heuristica simple: si user_msg incluye "?" Alfredo si pregunto)
        if "?" in user_msg:
            return None
        return CompanionViolation(
            code="REACTIVIDAD_INVERSA",
            severity=self._SEVERITIES["REACTIVIDAD_INVERSA"],
            descripcion=(
                "Cowork pregunta '¿queres que verifique?' cuando la verificacion "
                "es reversible. Debe actuar (F3 reactividad inversa)."
            ),
            cita=m.group(0),
        )

    def _detect_claim_sin_evidencia(self, output: str) -> Optional[CompanionViolation]:
        # Si hace claim pero no hay marca de verificacion adyacente
        if _RE_CLAIM_SIN_EVIDENCIA.search(output) and not _RE_EVIDENCIA_VERIFICACION.search(output):
            return CompanionViolation(
                code="CLAIM_SIN_EVIDENCIA",
                severity=self._SEVERITIES["CLAIM_SIN_EVIDENCIA"],
                descripcion=(
                    "Cowork afirma estado (roto/funcional/listo/etc) sin marca "
                    "de verificacion adyacente (curl/grep/git/HTTP/exit code). "
                    "Viola DSC-G-005 validacion en tiempo real."
                ),
                cita=None,
            )
        return None

    def _detect_meta_meta(self, output: str) -> Optional[CompanionViolation]:
        m = _RE_AUDIT_DE_AUDIT.search(output)
        if m:
            return CompanionViolation(
                code="META_META",
                severity=self._SEVERITIES["META_META"],
                descripcion=(
                    "Cowork esta auditando sus propios audits. Meta-meta. "
                    "El producto no avanza. Refactor a accion observable."
                ),
                cita=m.group(0)[:150],
            )
        return None

    # ------------------------------------------------------------------
    # Correccion sugerida
    # ------------------------------------------------------------------

    def _build_correction(self, violations: list[CompanionViolation], output: str, user_msg: str) -> str:
        """
        Construye texto de correccion estructurado para que Cowork reescriba.
        """
        magna = [v for v in violations if v.severity == "MAGNA"]
        severity = "MAGNA" if magna else "PREMIUM"

        lines = [
            f"[COWORK_COMPANION_BLOCK severity={severity}]",
            "",
            "Companion Agent (T4) detecto drift semantico que el guardian estatico",
            "no cubre. Reescribi tomando en cuenta:",
            "",
            "## Violaciones detectadas",
        ]
        for v in violations:
            lines.append(f"  - [{v.severity}] {v.code}: {v.descripcion}")
            if v.cita:
                lines.append(f"    cita: {v.cita!r}")

        lines.extend(
            [
                "",
                "## Instruccion de reescritura",
            ]
        )
        # Sugerencia primero por severidad MAGNA
        if any(v.code == "REPEAT_NO_PROGRESS" for v in violations):
            lines.append(
                "  Estas repitiendo. Cambia de capa: si estabas en doctrina, "
                "ejecuta accion observable. Si estabas en analisis, commitea."
            )
        if any(v.code == "SCOPE_INFLATION" for v in violations):
            lines.append(
                "  Recortar spec a max 3-5 tareas. Sin DoD inflado. "
                "Aplicar R1 'maxima potencia prohibida' del COWORK OS."
            )
        if any(v.code == "ROUTER_HUMANO" for v in violations):
            lines.append(
                "  Reemplaza prompt copy-paste por insercion a embrion_memoria "
                "con hilo_origen=cowork y destinatario=manus_t3."
            )
        if any(v.code == "TRES_OPCIONES" for v in violations):
            lines.append("  Diagnostico + prescripcion. NO menu de opciones. Decidi vos.")
        if any(v.code == "REACTIVIDAD_INVERSA" for v in violations):
            lines.append("  Verificacion reversible: ejecutala vos. NO devolver pelota.")
        if any(v.code == "CLAIM_SIN_EVIDENCIA" for v in violations):
            lines.append(
                "  Adjuntar evidencia: curl, git log, psql query, HTTP code, "
                "stdout literal. Sin evidencia, no afirmar estado."
            )
        if any(v.code == "META_META" for v in violations):
            lines.append("  Salir del meta-trabajo. Commitear avance en kernel/ o apps/mobile/.")

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
    parser = argparse.ArgumentParser(description="Companion Agent semantico para Cowork (T4).")
    parser.add_argument("--output", "-o", help="Output candidato (stdin si no se da).")
    parser.add_argument("--user-message", "-u", default="", help="Ultimo mensaje Alfredo.")
    parser.add_argument("--history", "-H", default="", help="Path a JSON con history list.")
    parser.add_argument("--json", action="store_true", help="Salida JSON.")
    args = parser.parse_args(argv)

    output = _read_stdin_or_arg(args.output)
    if not output:
        print("error: no hay output (--output o stdin)", file=sys.stderr)
        return 2

    history: list[str] = []
    if args.history:
        try:
            history = json.loads(Path(args.history).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"error leyendo history: {e}", file=sys.stderr)
            return 2

    companion = CompanionAgent()
    verdict = companion.intercept_and_correct(output, args.user_message, history)

    if args.json:
        print(json.dumps(verdict, indent=2, ensure_ascii=False))
    else:
        if verdict["passed"]:
            print("[COWORK_COMPANION_PASS] sin violaciones semanticas")
        else:
            print(verdict["correction"])
    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
