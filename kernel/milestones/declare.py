# kernel/milestones/declare.py
"""
Declaracion de hitos del Monstruo (DSC-G-017 + DSC-G-014).

NO se puede declarar PRODUCTO_COMERCIALIZABLE en chat, en bridge.md, ni en commit
message. Solo aqui, y solo si los gates definidos en gates.yaml pasan con
evidencia reproducible adjunta.

CLI:
    python -m kernel.milestones.declare pipeline_tecnico_funcional
    python -m kernel.milestones.declare producto_comercializable

Exit code:
    0  = hito declarado (todos los gates verde)
    1  = declaracion rechazada (>=1 gate fallido)
    2  = error de configuracion (hito no canonizado, yaml invalido, etc.)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


GATES_FILE = Path(__file__).parent / "gates.yaml"


class GateFailure(Exception):
    """Un gate especifico fallo. Bloqueante."""


class MilestoneDeclarationRejected(Exception):
    """Declaracion rechazada por uno o mas gates fallidos."""


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    evidence_path: str | None
    detail: str


def _load_gates() -> dict[str, Any]:
    if not GATES_FILE.exists():
        raise FileNotFoundError(f"Gates file no encontrado: {GATES_FILE}")
    return yaml.safe_load(GATES_FILE.read_text())


def _check_command(gate: dict[str, Any]) -> GateResult:
    cmd = gate["command"]
    expected = gate.get("expected_exit", 0)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=600)
        passed = result.returncode == expected
        return GateResult(
            gate_id=gate["id"],
            passed=passed,
            evidence_path=gate.get("evidence_artifact"),
            detail=f"exit={result.returncode}, expected={expected}",
        )
    except subprocess.TimeoutExpired:
        return GateResult(gate["id"], False, None, "timeout >600s")
    except Exception as e:
        return GateResult(gate["id"], False, None, f"error: {e}")


def _check_visual_audit(gate: dict[str, Any]) -> GateResult:
    script = gate["script"]
    urls_artifact = gate["urls_artifact"]
    min_score = gate["min_differentiation_score"]

    if not Path(urls_artifact).exists():
        return GateResult(
            gate["id"],
            False,
            None,
            f"urls_artifact ausente: {urls_artifact}. Sin evidencia, no hay declaracion (DSC-V-002).",
        )

    cmd = ["python", script, "--urls", urls_artifact, "--min-score", str(min_score)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        return GateResult(
            gate["id"],
            result.returncode == 0,
            gate.get("evidence_artifact"),
            (result.stdout or result.stderr)[:500],
        )
    except FileNotFoundError:
        return GateResult(gate["id"], False, None, f"script ausente: {script}")
    except Exception as e:
        return GateResult(gate["id"], False, None, f"error: {e}")


def _check_human_signature(gate: dict[str, Any]) -> GateResult:
    sig_path = Path(gate["signature_artifact"])
    if not sig_path.exists():
        return GateResult(
            gate["id"],
            False,
            None,
            f"firma humana ausente: {sig_path}. Validacion humana mandatoria (DSC-S-006).",
        )
    content = sig_path.read_text()
    required = gate["required_signer"].lower()
    passed = required in content.lower()
    return GateResult(
        gate["id"],
        passed,
        str(sig_path),
        f"firma '{required}' encontrada: {passed}",
    )


def _check_python_assertion(gate: dict[str, Any]) -> GateResult:
    module = gate["module"]
    assertion = gate["assertion"]
    gate_id = gate["id"]
    snippet = f"from {module} import *; assert {assertion}, 'gate {gate_id} fallo'"
    cmd = [sys.executable, "-c", snippet]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return GateResult(
            gate["id"],
            result.returncode == 0,
            gate.get("evidence_artifact"),
            (result.stderr or result.stdout)[:500],
        )
    except Exception as e:
        return GateResult(gate["id"], False, None, f"error: {e}")


def _check_http_endpoint(gate: dict[str, Any]) -> GateResult:
    import urllib.error
    import urllib.request
    try:
        req = urllib.request.Request(gate["url"])
        with urllib.request.urlopen(req, timeout=30) as resp:
            ok = resp.status == gate["expected_status"]
            return GateResult(
                gate["id"],
                ok,
                gate.get("evidence_artifact"),
                f"status={resp.status}, expected={gate['expected_status']}",
            )
    except urllib.error.HTTPError as e:
        return GateResult(gate["id"], False, None, f"http_error: {e.code}")
    except Exception as e:
        return GateResult(gate["id"], False, None, f"error: {e}")


def _check_coverage(gate: dict[str, Any]) -> GateResult:
    artifact = Path(gate["evidence_artifact"])
    if not artifact.exists():
        return GateResult(
            gate["id"],
            False,
            None,
            f"coverage artifact ausente: {artifact}. Corra pytest --cov primero.",
        )
    text = artifact.read_text()
    m = re.search(r'line-rate="([0-9.]+)"', text)
    if not m:
        return GateResult(gate["id"], False, str(artifact), "coverage.xml no parseable")
    pct = float(m.group(1)) * 100
    threshold = gate["threshold"]
    return GateResult(
        gate["id"],
        pct >= threshold,
        str(artifact),
        f"coverage={pct:.1f}%, threshold={threshold}%",
    )


CHECKERS = {
    "command": _check_command,
    "visual_audit": _check_visual_audit,
    "human_signature": _check_human_signature,
    "python_assertion": _check_python_assertion,
    "http_endpoint": _check_http_endpoint,
    "coverage": _check_coverage,
}


def evaluate_milestone(name: str) -> tuple[bool, list[GateResult]]:
    cfg = _load_gates()
    if name not in cfg["milestones"]:
        raise KeyError(
            f"Hito no canonizado: '{name}'. Editar kernel/milestones/gates.yaml."
        )

    milestone = cfg["milestones"][name]
    results: list[GateResult] = []

    if "requires_milestone" in milestone:
        prev_ok, _ = evaluate_milestone(milestone["requires_milestone"])
        if not prev_ok:
            results.append(
                GateResult(
                    f"prereq:{milestone['requires_milestone']}",
                    False,
                    None,
                    "prerequisito no declarado verde",
                )
            )
            return False, results

    for gate in milestone["gates"]:
        kind = gate["check_kind"]
        if kind not in CHECKERS:
            results.append(
                GateResult(
                    gate["id"],
                    False,
                    None,
                    f"check_kind desconocido: {kind}",
                )
            )
            continue
        results.append(CHECKERS[kind](gate))

    all_passed = all(r.passed for r in results)
    return all_passed, results


def declare(name: str, fail_loud: bool = True) -> dict[str, Any]:
    ok, results = evaluate_milestone(name)
    payload = {
        "milestone": name,
        "declared": ok,
        "gates": [asdict(r) for r in results],
    }
    if not ok and fail_loud:
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)
        failed = sum(1 for r in results if not r.passed)
        raise MilestoneDeclarationRejected(
            f"Declaracion rechazada para '{name}'. {failed}/{len(results)} gates fallidos."
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Declarar un hito del Monstruo contra gates.yaml (DSC-G-017)."
    )
    parser.add_argument(
        "milestone",
        help="Nombre del hito (ver kernel/milestones/gates.yaml)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output solo el JSON, sin texto explicativo.",
    )
    args = parser.parse_args()

    try:
        payload = declare(args.milestone, fail_loud=False)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if not payload["declared"]:
        if not args.json_only:
            failed = [g for g in payload["gates"] if not g["passed"]]
            print(
                f"\nDeclaracion RECHAZADA. {len(failed)}/{len(payload['gates'])} gates fallidos:",
                file=sys.stderr,
            )
            for g in failed:
                print(f"  - {g['gate_id']}: {g['detail']}", file=sys.stderr)
        return 1

    if not args.json_only:
        print(
            f"\n[ok] Hito declarado: {payload['milestone']}. "
            f"{len(payload['gates'])} gates verde.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
