"""
kernel/cowork_runtime/t1_output_contract.py — Contrato de salida tipado.

Antes de que una respuesta de Cowork llegue a Alfredo, cada afirmacion
sustantiva debe llevar uno de cuatro tags:

  [VERIFICADO fuente + timestamp]   Afirmacion factual operacional con
                                    evidencia fresca de esta sesion (Read,
                                    Grep, Bash, SQL via MCP, etc).
  [INFERIDO]                        Inferencia razonable a partir de
                                    contexto, sin fuente binaria directa.
  [NO VERIFICADO]                   Dato que NO se pudo comprobar en esta
                                    sesion (memoria stale, asumido, etc).
  [REQUIERE READ/SQL]               Claim que necesita lectura fresca y
                                    aun no se ha hecho.

Implementacion: heuristica conservadora basada en patrones de oracion
afirmativa. NO pretende ser un parser de lenguaje natural — el objetivo
es alimentar el audit log con claims candidatos, donde la auditoria
manual a 24h decidira true/false positive / false negative.

Severidad asignada cuando un claim sustantivo no tiene tag:
  P0  Claim factual sobre estado de produccion (kernel, PRs, RLS,
      migraciones, embrion). Bloqueante en ENFORCE.
  P1  Claim factual sobre estado del repo o memoria (DSCs canonizados,
      archivos existentes, contenido de specs). Bloqueante en ENFORCE.
  P2  Texto sin claim factual operacional (opiniones, recomendaciones,
      preguntas, meta-trabajo). Nunca bloqueante.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


VALID_TAGS: tuple[str, ...] = (
    "VERIFICADO",
    "INFERIDO",
    "NO VERIFICADO",
    "REQUIERE READ/SQL",
)

# Detecta cualquiera de los tags al inicio o al final de una linea
TAG_REGEX = re.compile(
    r"\[(?:VERIFICADO[^\]]*|INFERIDO|NO\s+VERIFICADO|REQUIERE\s+READ/SQL)\]",
    re.IGNORECASE,
)

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
    tag_value: str = ""  # contenido del tag si has_tag

    def is_untagged_material(self) -> bool:
        return (not self.has_tag) and self.severity in ("P0", "P1")


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


def _sentence_has_tag(sentence: str) -> tuple[bool, str]:
    m = TAG_REGEX.search(sentence)
    if not m:
        return False, ""
    return True, m.group(0)


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
        has_tag, tag_value = _sentence_has_tag(s)
        severity = _classify_severity(s)
        claims.append(Claim(
            text=s,
            severity=severity,
            has_tag=has_tag,
            tag_value=tag_value,
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
        "Tu output candidato contiene claims factuales operativos sin tag.",
        "Antes de enviar a Alfredo, cada claim sustantivo debe llevar uno de:",
        "  [VERIFICADO fuente + timestamp]",
        "  [INFERIDO]",
        "  [NO VERIFICADO]",
        "  [REQUIERE READ/SQL]",
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
