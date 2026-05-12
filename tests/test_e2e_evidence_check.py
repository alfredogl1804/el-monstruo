"""Tests para tools/_check_e2e_evidence.py (DSC-G-010)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import importlib.util

_SPEC = importlib.util.spec_from_file_location(
    "_check_e2e_evidence",
    ROOT / "tools" / "_check_e2e_evidence.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)  # type: ignore[arg-type]
_SPEC.loader.exec_module(_MOD)  # type: ignore[union-attr]

check_pr_body = _MOD.check_pr_body
extract_evidence_section = _MOD.extract_evidence_section
check_binary_evidence = _MOD.check_binary_evidence


# ---------------------- OBLIGATORIOS (3) ----------------------

def test_pr_body_con_url_pasa():
    body = """## Resumen
Sprint cerrado.

## E2E Evidence
Logs Railway: https://railway.app/project/abc/deployments/xyz
"""
    code, msg = check_pr_body(body)
    assert code == 0, msg
    assert "url:" in msg


def test_pr_body_sin_seccion_falla():
    body = "## Resumen\nCambios menores.\n\n## Tests\nPasaron todos."
    code, msg = check_pr_body(body)
    assert code == 2
    assert "ausente" in msg.lower()


def test_pr_body_seccion_vacia_falla():
    body = "## Resumen\nCambios.\n\n## E2E Evidence\nTODO: agregar despues.\n\n## Otros\n"
    code, msg = check_pr_body(body)
    assert code == 1
    assert "sin evidencia binaria" in msg.lower()


# ---------------------- EDGE (12) ----------------------

def test_seccion_case_insensitive():
    body = "## e2e evidence\nhttps://example.com/log"
    code, _ = check_pr_body(body)
    assert code == 0


def test_path_repo_pasa():
    body = "## E2E Evidence\nVer reports/sprint_001.md"
    code, msg = check_pr_body(body)
    assert code == 0
    assert "path:" in msg


def test_sha_commit_pasa():
    body = "## E2E Evidence\nCommit cb07e45 contiene la fix."
    code, msg = check_pr_body(body)
    assert code == 0
    assert "sha:" in msg


def test_test_results_pasa():
    body = "## E2E Evidence\n```\n7 passed in 0.02s\n```"
    code, msg = check_pr_body(body)
    assert code == 0
    assert "test:" in msg


def test_smoke_count_pasa():
    body = "## E2E Evidence\nsmoke 3/3 verde"
    code, _ = check_pr_body(body)
    assert code == 0


def test_body_vacio_falla():
    code, msg = check_pr_body("")
    assert code == 2
    assert "vacio" in msg.lower()


def test_body_solo_whitespace_falla():
    code, _ = check_pr_body("   \n\n  ")
    assert code == 2


def test_seccion_termina_en_siguiente_h2():
    body = """## E2E Evidence

## Otra Seccion
https://no-deberia-contar.com
"""
    code, _ = check_pr_body(body)
    assert code == 1


def test_multiple_evidencias_se_listan():
    body = "## E2E Evidence\n- URL: https://railway.app/log\n- Path: reports/sprint.md\n- Commit: cb07e45"
    code, msg = check_pr_body(body)
    assert code == 0
    assert "url:" in msg
    assert "path:" in msg
    assert "sha:" in msg


def test_url_dentro_de_codigo_pasa():
    body = "## E2E Evidence\n```\ncurl https://api.example.com/health\n```"
    code, _ = check_pr_body(body)
    assert code == 0


def test_no_falla_con_solo_texto_descriptivo():
    body = "## E2E Evidence\nEsta seccion sin evidencia binaria solo dice palabras."
    code, _ = check_pr_body(body)
    assert code == 1


def test_extract_section_devuelve_none_si_falta():
    assert extract_evidence_section("## Otra cosa\ntexto") is None


def test_check_binary_evidence_solo_texto_falla():
    valid, found = check_binary_evidence("solo descripcion narrativa sin nada binario")
    assert valid is False
    assert found == []
