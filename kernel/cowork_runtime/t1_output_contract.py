"""
kernel/cowork_runtime/t1_output_contract.py — Contrato de salida tipado.

Antes de que una respuesta de Cowork llegue a Alfredo, cada afirmacion
sustantiva debe llevar una de las 9 etiquetas epistemicas canonicas
(convergencia 7 Sabios 2026-05-12, ver kernel/cowork_runtime/epistemic_labels.py):

  [VERIFIED_CURRENT_TURN]        tool_call ejecutado en este turno
  [VERIFIED_RECENT_LT_60M]       validado <60min, no repetir tool_call
  [SESSION_MEMORY_ONLY]          solo memoria de sesion, NO afirmar como hecho
  [INFERRED]                     inferencia razonable, no verificacion
  [USER_PROVIDED]                dato que aporto Alfredo T1 en sesion
  [NEEDS_SQL]                    claim factual que requiere SQL fresco
  [NEEDS_READ]                   claim factual que requiere Read del repo
  [CONTRADICTED_BY_EXTERNAL]     contradice output reciente Sabio externo
  [UNVERIFIED_DO_NOT_ASSERT]     sin licencia para afirmar, debe omitirse

Compatibilidad hacia atras: las 4 etiquetas legacy
([VERIFICADO ...], [INFERIDO], [NO VERIFICADO], [REQUIERE READ/SQL])
siguen siendo aceptadas y se normalizan al equivalente moderno via
epistemic_labels.normalize_label().

Implementacion: heuristica conservadora basada en patrones de oracion
afirmativa. NO pretende ser un parser de lenguaje natural — el objetivo
es alimentar el audit log con claims candidatos, donde la auditoria
manual decidira true_block / false_positive / false_negative.

Severidad asignada cuando un claim sustantivo no tiene etiqueta:
  P0  Claim factual sobre estado de produccion (kernel, PRs, RLS,
      migraciones, embrion). Bloqueante en ENFORCE.
  P1  Claim factual sobre estado del repo o memoria (DSCs canonizados,
      archivos existentes, contenido de specs). Bloqueante en ENFORCE.
  P2  Texto sin claim factual operacional (opiniones, recomendaciones,
      preguntas, meta-trabajo). NUNCA bloqueante, ni siquiera en ENFORCE.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Optional

from kernel.cowork_runtime.epistemic_labels import (
    LABEL_REGEX,
    VALID_LABELS_9,
    extract_label,
    is_licensed,
    requires_tool_call,
)


# Compat: lista historica de etiquetas legacy.
VALID_TAGS: tuple[str, ...] = (
    "VERIFICADO",
    "INFERIDO",
    "NO VERIFICADO",
    "REQUIERE READ/SQL",
)

# Compat: alias del nuevo regex. Codigo legacy que importe TAG_REGEX
# obtiene el detector unificado de 9 etiquetas + 4 legacy.
TAG_REGEX = LABEL_REGEX

# Patrones P0 — claims sobre estado operativo del sistema. Si un claim
# matcha esto sin tag y NO es pregunta/condicional, es P0.
P0_PATTERNS: tuple[re.Pattern, ...] = tuple(
    re.compile(p, re.IGNORECASE) for p in (
        r"\b(?:kernel|embri[óo]n|gateway|railway|supabase|RLS)\b.*\b(?:vivo|activo|funcionando|caido|down|up|deployed|merge[ad]o)\b",
        r"\bPR\s*#\s*\d+\b.*\b(?:merge[ad]o|mergeado|cerrado|abierto|ready)\b",
        r"\b(?:migraci[óo]n|migration)\b.*\b(?:aplicad[ao]|ejecutad[ao]|corrid[ao])\b",
        r"\bapply_migration\b",
        r"\b(?:produccion|production|prod)\b.*\b(?:status|estado|caido|down|vivo)\b",
    )
)

# Patrones P1 — claims sobre repo/memoria persistente.
P1_PATTERNS: tuple[re.Pattern, ...] = tuple(
    re.compile(p, re.IGNORECASE) for p in (
        r"\bDSC[-_][A-Z]+[-_]?\d+\b",
        r"\b\d+\s+DSCs?\b",
        r"\b\d+/\d+\s+tablas\b",
        r"\b(?:archivo|spec|doc|memory/cowork)\b.*\b(?:existe|esta|contiene|firmado|canonizado)\b",
        r"\b(?:linea|line|loc|tests?)\s+\d+",
    )
)

# Conectivos / hedges que indican que la oracion no es un claim factual
HEDGE_PATTERNS = re.compile(
    r"\b(?:propongo|sugiero|deberia|deber[íi]a|quiz[áa]s?|tal vez|"
    r"podr[íi]a|podria|recomiendo|opino|creo que|me parece|"
    r"podemos|quieres|querer|si quieres|"
    r"\?)\b",
    re.IGNORECASE,
)


@dataclass
class Claim:
    text: str
    severity: str  # "P0" | "P1" | "P2"
    has_tag: bool
    tag_value: str = ""  # contenido literal del tag si has_tag (con corchetes)
    normalized_label: Optional[str] = None  # uno de VALID_LABELS_9 si has_tag

    def is_untagged_material(self) -> bool:
        return (not self.has_tag) and self.severity in ("P0", "P1")

    def has_license_to_assert(self) -> bool:
        """
        True si la etiqueta concede licencia para afirmar (VERIFIED_*,
        USER_PROVIDED). False si esta sin etiqueta o etiqueta degradante.
        """
        return is_licensed(self.normalized_label)

    def needs_tool_call(self) -> bool:
        """True si la etiqueta es NEEDS_SQL o NEEDS_READ."""
        return requires_tool_call(self.normalized_label)


@dataclass
class ContractReport:
    claims: list[Claim] = field(default_factory=list)

    @property
    def untagged_p0(self) -> list[Claim]:
        return [c for c in self.claims if c.severity == "P0" and not c.has_tag]

    @property
    def untagged_p1(self) -> list[Claim]:
        return [c for c in self.claims if c.severity == "P1" and not c.has_tag]

    @property
    def untagged_p2(self) -> list[Claim]:
        return [c for c in self.claims if c.severity == "P2" and not c.has_tag]

    @property
    def has_untagged_blocking(self) -> bool:
        """True si hay al menos un claim P0 o P1 sin tag."""
        return bool(self.untagged_p0 or self.untagged_p1)

    def summary(self) -> dict:
        return {
            "total_claims": len(self.claims),
            "tagged": sum(1 for c in self.claims if c.has_tag),
            "untagged_p0": len(self.untagged_p0),
            "untagged_p1": len(self.untagged_p1),
            "untagged_p2": len(self.untagged_p2),
            "has_untagged_blocking": self.has_untagged_blocking,
        }


def _strip_code_blocks(text: str) -> str:
    return re.sub(r"```[\s\S]*?```", "", text)


def _classify_severity(sentence: str) -> str:
    # Hedge primero -> P2
    if HEDGE_PATTERNS.search(sentence):
        return "P2"
    for pat in P0_PATTERNS:
        if pat.search(sentence):
            return "P0"
    for pat in P1_PATTERNS:
        if pat.search(sentence):
            return "P1"
    return "P2"


def _sentence_has_tag(sentence: str) -> tuple[bool, str, Optional[str]]:
    """
    Devuelve (has_tag, raw_match_con_corchetes, normalized_label_o_None).

    Detecta tanto las 9 etiquetas modernas como las 4 legacy. La
    normalizacion mapea legacy -> moderno (ver epistemic_labels.py).
    """
    has, raw, normalized = extract_label(sentence)
    return has, raw, normalized


def extract_claims(text: str) -> list[Claim]:
    """
    Particiona el texto en claims y clasifica cada uno por severidad.

    Heuristica: split por '.', '!', '?', salto de linea con bullet '-'.
    Stripea bloques de codigo. Lineas vacias o <3 palabras se ignoran.
    """
    stripped = _strip_code_blocks(text)
    # Normaliza bullets
    stripped = re.sub(r"^[ \t]*[-*]\s+", "", stripped, flags=re.MULTILINE)
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", stripped)

    claims: list[Claim] = []
    for s in raw_sentences:
        s = s.strip()
        if len(s.split()) < 3:
            continue
        has_tag, tag_value, normalized_label = _sentence_has_tag(s)
        severity = _classify_severity(s)
        claims.append(Claim(
            text=s,
            severity=severity,
            has_tag=has_tag,
            tag_value=tag_value,
            normalized_label=normalized_label,
        ))
    return claims


def analyze(text: str) -> ContractReport:
    """Punto de entrada principal: devuelve un ContractReport del output."""
    return ContractReport(claims=extract_claims(text))


def format_violation_feedback(report: ContractReport) -> str:
    """Mensaje que se devuelve a Cowork cuando se bloquea en ENFORCE."""
    lines = [
        "[T1_OUTPUT_CONTRACT_VIOLATION]",
        "",
        "Tu output candidato contiene claims factuales operativos sin etiqueta.",
        "Cada claim sustantivo debe llevar UNA de las 9 etiquetas canonicas:",
        "  [VERIFIED_CURRENT_TURN fuente=... ts=...]",
        "  [VERIFIED_RECENT_LT_60M fuente=... ts=...]",
        "  [SESSION_MEMORY_ONLY]",
        "  [INFERRED]",
        "  [USER_PROVIDED]",
        "  [NEEDS_SQL] + propuesta de query exacta",
        "  [NEEDS_READ] + path del archivo",
        "  [CONTRADICTED_BY_EXTERNAL fuente=...]",
        "  [UNVERIFIED_DO_NOT_ASSERT]",
        "",
        "Legacy (aceptado por compat, normalizado): [VERIFICADO ...] / [INFERIDO] /",
        "[NO VERIFICADO] / [REQUIERE READ/SQL]",
        "",
        f"Resumen: {report.summary()}",
        "",
        "## Claims P0 sin tag (bloqueantes)",
    ]
    for c in report.untagged_p0:
        lines.append(f"  - {c.text[:200]}")
    lines.append("")
    lines.append("## Claims P1 sin tag (bloqueantes)")
    for c in report.untagged_p1:
        lines.append(f"  - {c.text[:200]}")
    lines.append("")
    lines.append("## Claims P2 sin tag (NO bloqueantes — solo registrados)")
    for c in report.untagged_p2[:5]:
        lines.append(f"  - {c.text[:200]}")
    return "\n".join(lines)
