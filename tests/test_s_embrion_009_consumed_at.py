"""
S-EMBRION-009 T4 — Tests for consumed_at filter + NO_RESPONDER pre-flight.

Spec: bridge/sprints_propuestos/sprint_S-EMBRION-009_consumed_at_pre_llm_silence.md
Audit Cowork: comment 4472878191 (PR #139) — VERDE_CON_OBSERVACIONES.

Cierra hallazgo H1 (2026-05-17): bucle infinito por re-detección de
mensaje_alfredo cuando self_verifier abortaba el thought.

Doctrina (Cowork Opción 2):
  - Marcar consumed_at ANTES de invocar LLM (idempotente)
  - Pre-flight NO_RESPONDER strict matching (Cowork P2 Q2.b):
    case-sensitive, word-boundary, sin invocar LLM

6 tests:
  1. _NO_RESPONDER_RE matches exact literal (positive)
  2. _NO_RESPONDER_RE rejects "NO_RESPONDERIA" (word-boundary, no false positive)
  3. _NO_RESPONDER_RE rejects "no_responder" lowercase (case-sensitive)
  4. _mark_consumed returns False when DB not connected
  5. _mark_consumed returns False with empty msg_id
  6. AST: _detect_trigger uses {"consumed_at": None} filter
"""
from __future__ import annotations

import ast
import asyncio
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
EMBRION_LOOP_PATH = REPO_ROOT / "kernel" / "embrion_loop.py"

# Asegurar que el repo root está en sys.path para 'from kernel.embrion_loop'.
# Pytest del proyecto asume rootdir = repo root (configuración CI).
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ─────────────────────────────────────────────────────────────────────
# Tests 1-3: Regex strict matching (Cowork P2 Q2.b)
# ─────────────────────────────────────────────────────────────────────


def test_no_responder_regex_matches_exact_literal():
    """_NO_RESPONDER_RE must match the literal flag in real usage contexts."""
    from kernel.embrion_loop import _NO_RESPONDER_RE

    cases = [
        "POST_MERGE_PROOF anti-dory test 2026-05-13 NO_RESPONDER",
        "Mensaje de prueba. NO_RESPONDER al final.",
        "directiva: NO_RESPONDER (ack inmediato)",
        "[NO_RESPONDER]",
        "msg NO_RESPONDER msg",
    ]
    for content in cases:
        assert _NO_RESPONDER_RE.search(content), (
            f"Expected match in: {content!r}"
        )


def test_no_responder_regex_rejects_no_responderia_word_boundary():
    """_NO_RESPONDER_RE must NOT match substrings (word-boundary anchored).

    Sin word-boundary, NO_RESPONDER también matchearía dentro de
    NO_RESPONDERIA, NO_RESPONDERLE, etc., generando false positives.
    """
    from kernel.embrion_loop import _NO_RESPONDER_RE

    cases = [
        "Yo NO_RESPONDERIA a este mensaje",
        "El bot NO_RESPONDERLE conviene",
        "NO_RESPONDERSE es la doctrina",
        "_NO_RESPONDERX_",  # con sufijo no-word-boundary
    ]
    for content in cases:
        assert not _NO_RESPONDER_RE.search(content), (
            f"Unexpected match in: {content!r} (word-boundary should reject)"
        )


def test_no_responder_regex_rejects_lowercase_case_sensitive():
    """_NO_RESPONDER_RE must be case-sensitive (Cowork strict matching).

    El flag canónico es UPPERCASE. Aceptar lowercase ampliaría la superficie
    de obediencia a casos no autorizados.
    """
    from kernel.embrion_loop import _NO_RESPONDER_RE

    cases = [
        "no_responder en lowercase",
        "No_Responder en titlecase",
        "nO_rESPONDER mixed case",
    ]
    for content in cases:
        assert not _NO_RESPONDER_RE.search(content), (
            f"Unexpected match in: {content!r} (must be case-sensitive)"
        )


# ─────────────────────────────────────────────────────────────────────
# Tests 4-5: _mark_consumed (idempotencia + safety guards)
# ─────────────────────────────────────────────────────────────────────


class _MockDBDisconnected:
    """DB no conectada — _mark_consumed debe retornar False sin tocar DB."""

    connected = False

    async def update(self, *args, **kwargs):  # pragma: no cover
        raise AssertionError("update() no debería llamarse con DB desconectada")


class _MockDBConnected:
    """DB conectada — captura calls para validar UPDATE."""

    connected = True

    def __init__(self):
        self.update_calls: list[dict] = []

    async def update(self, table, data, filters):
        self.update_calls.append({"table": table, "data": data, "filters": filters})
        return {"id": filters.get("id"), "consumed_at": data.get("consumed_at")}


def _make_loop(db):
    """Crea instancia minimal de EmbrionLoop solo con _db (helper para tests)."""
    from kernel.embrion_loop import EmbrionLoop

    # Bypass __init__ — solo necesitamos self._db para _mark_consumed
    loop = EmbrionLoop.__new__(EmbrionLoop)
    loop._db = db
    return loop


def test_mark_consumed_returns_false_when_db_disconnected():
    """_mark_consumed debe retornar False sin tocar DB cuando no conectada."""
    loop = _make_loop(_MockDBDisconnected())
    result = asyncio.run(loop._mark_consumed("any-uuid"))
    assert result is False


def test_mark_consumed_returns_false_with_empty_msg_id():
    """_mark_consumed debe rechazar msg_id vacío sin tocar DB."""
    db = _MockDBConnected()
    loop = _make_loop(db)
    result = asyncio.run(loop._mark_consumed(""))
    assert result is False
    assert db.update_calls == [], (
        "msg_id vacío no debe ejecutar UPDATE (safety guard)"
    )


# ─────────────────────────────────────────────────────────────────────
# Test 6: AST — _detect_trigger usa filter consumed_at IS NULL
# ─────────────────────────────────────────────────────────────────────


def test_detect_trigger_filters_consumed_at_is_null():
    """_detect_trigger must include consumed_at: None in the select filter.

    Esto es el corazón del fix arquitectónico de S-EMBRION-009: solo se
    consideran mensajes pendientes (consumed_at IS NULL).
    """
    src = EMBRION_LOOP_PATH.read_text()
    tree = ast.parse(src)

    # Ubicar la función _detect_trigger
    detect_trigger_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_detect_trigger":
            detect_trigger_func = node
            break

    assert detect_trigger_func is not None, "_detect_trigger no encontrado"

    # Buscar literal {"tipo": "mensaje_alfredo", "consumed_at": None}
    found_consumed_at_filter = False
    for node in ast.walk(detect_trigger_func):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if "tipo" in keys and "consumed_at" in keys:
            # Encontrar el value asociado a consumed_at
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "consumed_at":
                    if isinstance(v, ast.Constant) and v.value is None:
                        found_consumed_at_filter = True
                        break

    assert found_consumed_at_filter, (
        "_detect_trigger debe incluir filter {'consumed_at': None} para "
        "seleccionar solo mensajes pendientes (S-EMBRION-009 T2)"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
