"""
El Monstruo — Skill Read Tool (DAN P0.4)
=========================================
Handler de solo lectura para `skills/<name>/SKILL.md`. NO escribe, NO ejecuta.
Aplica redacción de PII básica antes de devolver el contenido al LLM.

Ubicación de skills (verificada contra repo):
    skills/<skill_name>/SKILL.md

Sprint DAN — P0.4-mínimo — 2026-05-27 — Manus E1
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger("tools.skill_read")

# Repo root: tools/skill_read.py vive en <root>/tools/, asi que parent.parent = root
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SKILLS_DIR = _REPO_ROOT / "skills"

# Patrones PII conservadores. Falsos positivos preferibles a leak.
_PII_PATTERNS = [
    # Tokens / claves API comunes
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "[REDACTED:OPENAI_KEY]"),
    (re.compile(r"sk_live_[A-Za-z0-9_\-]{20,}"), "[REDACTED:STRIPE_KEY]"),
    (re.compile(r"pk_live_[A-Za-z0-9_\-]{20,}"), "[REDACTED:STRIPE_PUB_KEY]"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "[REDACTED:GOOGLE_KEY]"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "[REDACTED:GITHUB_TOKEN]"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{50,}"), "[REDACTED:GITHUB_PAT]"),
    (re.compile(r"xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]{20,}"), "[REDACTED:SLACK_BOT]"),
    # JWTs (tres segmentos base64url separados por punto)
    (
        re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
        "[REDACTED:JWT]",
    ),
    # Postgres URLs con credenciales
    (re.compile(r"postgres(?:ql)?://[^:]+:[^@]+@"), "postgresql://[REDACTED]@"),
    # Emails (PII común; útil redactar antes de pasarle al LLM)
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[REDACTED:EMAIL]"),
]


def _redact_pii(text: str) -> tuple[str, int]:
    """Aplica patrones de redacción y devuelve (texto_limpio, hits_count)."""
    hits = 0
    out = text
    for pattern, replacement in _PII_PATTERNS:
        out, n = pattern.subn(replacement, out)
        hits += n
    return out, hits


def _is_safe_skill_name(name: str) -> bool:
    """
    Valida que skill_name sea un slug seguro: letras, dígitos, guiones, underscores.
    Bloquea path traversal (../), separadores y nombres absolutos.
    """
    if not name or len(name) > 100:
        return False
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_\-]*", name):
        return False
    return True


async def skill_read(skill_name: str, **kwargs: Any) -> dict[str, Any]:
    """
    Lee `skills/<skill_name>/SKILL.md` con redacción PII.

    Args:
        skill_name: nombre del directorio de skill bajo `skills/`. Debe ser un
            slug seguro (letras/dígitos/guion/underscore, sin path traversal).

    Returns:
        dict con keys:
            - skill_name: nombre solicitado (echo).
            - path: path relativo desde repo root (informativo, sin leak absoluto).
            - content: contenido del SKILL.md con PII redactada. None si error.
            - bytes: tamaño del archivo original.
            - redactions: número de redacciones aplicadas.
            - error: str | None.
    """
    if not _is_safe_skill_name(skill_name):
        logger.warning("skill_read_invalid_name", skill_name=skill_name[:50])
        return {
            "skill_name": skill_name,
            "path": None,
            "content": None,
            "bytes": 0,
            "redactions": 0,
            "error": "invalid skill_name (use slug: letters/digits/_/-, max 100 chars)",
        }

    skill_md = _SKILLS_DIR / skill_name / "SKILL.md"

    # Defensa en profundidad: aunque el slug pase, confirmamos que el path
    # resuelto sigue dentro de _SKILLS_DIR (anti symlink/traversal residual).
    try:
        resolved = skill_md.resolve()
        if not str(resolved).startswith(str(_SKILLS_DIR.resolve())):
            return {
                "skill_name": skill_name,
                "path": None,
                "content": None,
                "bytes": 0,
                "redactions": 0,
                "error": "path traversal blocked",
            }
    except Exception as e:  # pragma: no cover — defensive
        return {
            "skill_name": skill_name,
            "path": None,
            "content": None,
            "bytes": 0,
            "redactions": 0,
            "error": f"path resolution failed: {e}",
        }

    if not resolved.exists() or not resolved.is_file():
        return {
            "skill_name": skill_name,
            "path": f"skills/{skill_name}/SKILL.md",
            "content": None,
            "bytes": 0,
            "redactions": 0,
            "error": "SKILL.md not found",
        }

    try:
        raw = resolved.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "skill_name": skill_name,
            "path": f"skills/{skill_name}/SKILL.md",
            "content": None,
            "bytes": 0,
            "redactions": 0,
            "error": f"read failed: {e}",
        }

    redacted, hits = _redact_pii(raw)
    rel_path = f"skills/{skill_name}/SKILL.md"

    logger.info(
        "skill_read_success",
        skill_name=skill_name,
        bytes=len(raw),
        redactions=hits,
    )

    return {
        "skill_name": skill_name,
        "path": rel_path,
        "content": redacted,
        "bytes": len(raw),
        "redactions": hits,
        "error": None,
    }
