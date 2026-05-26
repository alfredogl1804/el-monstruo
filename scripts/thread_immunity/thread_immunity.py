#!/usr/bin/env python3
"""
THREAD-IMMUNITY-GATE-v1
Una sola intervención atómica:
A) Arranque verificado
B) Cierre canonizado
C) Verificador externo

No guarda secrets. Usa SUPABASE_URL + SUPABASE_SERVICE_KEY desde env.
No reemplaza Guardian. Lo envuelve con checks binarios.

Diseño autoría: GPT-5.5 Pro (oráculo externo verificado contra GitHub).
Verificación binaria: Hilo B (Manus, ejecutor técnico).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = REPO_ROOT / "bridge" / "thread_immunity"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
GUARDIAN_LOCAL = Path.home() / ".monstruo" / "guardian.py"
GUARDIAN_REPO = REPO_ROOT / "monstruo-memoria" / ".monstruo" / "guardian.py"

REQUIRED_AXIOMS = {
    "THREAD_IMMUNITY_GATE_V1": (
        "Un hilo Manus no puede declarar anclaje, readiness ni capacidad de proceder "
        "hasta que exista STARTUP_PASS verificado por thread_immunity.py y watchdog externo."
    ),
    "ALFREDO_NOT_DON_ALFREDO": (
        "El usuario es Alfredo. No llamarlo don Alfredo. Don Hugo es su papá. "
        "Si un hilo usa don Alfredo para Alfredo, está desanclado."
    ),
    "NO_SELF_ANCHOR_DECLARATION": (
        "La frase hilo anclado no tiene valor si la produce el propio hilo sin receipt "
        "STARTUP_PASS registrado externamente."
    ),
}

SESSION_TTL_HOURS = int(os.environ.get("THREAD_IMMUNITY_TTL_HOURS", "6"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fail(msg: str, code: int = 2) -> None:
    print(f"THREAD_IMMUNITY_FAIL: {msg}")
    sys.exit(code)


def ok(msg: str) -> None:
    print(f"THREAD_IMMUNITY_OK: {msg}")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def get_env() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        fail("SUPABASE_URL y SUPABASE_SERVICE_KEY son obligatorios")
    return url, key


def supabase_request(method: str, path: str, body: dict | list | None = None) -> object:
    url, key = get_env()
    full_url = f"{url}/rest/v1/{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if method == "POST":
        headers["Prefer"] = "return=representation"
    req = Request(full_url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        fail(f"Supabase HTTP {e.code} {path}: {detail}")
    except URLError as e:
        fail(f"Supabase connection error {path}: {e}")
    except Exception as e:
        fail(f"Supabase unexpected error {path}: {e}")


def insert_event(
    session_id: str,
    thread_id: str,
    event_type: str,
    topic: str | None = None,
    summary: str | None = None,
    canon_statement: str | None = None,
    evidence: dict | None = None,
    local_receipt_sha256: str | None = None,
) -> dict:
    row = {
        "session_id": session_id,
        "thread_id": thread_id,
        "event_type": event_type,
        "topic": topic,
        "summary": summary,
        "canon_statement": canon_statement,
        "evidence": evidence or {},
        "local_receipt_sha256": local_receipt_sha256,
    }
    result = supabase_request("POST", "thread_immunity_events", row)
    if isinstance(result, list) and result:
        return result[0]
    return row


def fetch_axioms() -> list[dict]:
    path = (
        "sovereign_axioms?is_active=eq.true"
        "&select=id,statement,source_agent,confidence,validation_count,implications"
        "&limit=200"
    )
    result = supabase_request("GET", path)
    return result if isinstance(result, list) else []


def axiom_exists(fingerprint: str, axioms: list[dict]) -> bool:
    return any(fingerprint in (a.get("statement") or "") for a in axioms)


def insert_axiom(fingerprint: str, statement: str) -> None:
    axiom = {
        "statement": f"{fingerprint}: {statement}",
        "source_agent": "thread_immunity_gate_v1",
        "confidence": 1.0,
        "validation_count": 1,
        "is_active": True,
        "implications": json.dumps(
            [
                "Bloquea auto-declaraciones de anclaje sin evidencia externa.",
                "Obliga cierre con canonización o watchdog reporta drift.",
            ]
        ),
    }
    supabase_request("POST", "sovereign_axioms", axiom)


def run_guardian() -> str:
    guardian = GUARDIAN_LOCAL if GUARDIAN_LOCAL.exists() else GUARDIAN_REPO
    if not guardian.exists():
        fail(f"guardian.py no existe en {GUARDIAN_LOCAL} ni {GUARDIAN_REPO}")
    proc = subprocess.run(
        [sys.executable, str(guardian)],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=90,
    )
    output = proc.stdout or ""
    if proc.returncode != 0:
        fail(f"guardian.py exit code {proc.returncode}\n{output[-2000:]}")
    if "IDENTIDAD RESTAURADA" not in output:
        fail("guardian.py no imprimió IDENTIDAD RESTAURADA")
    return output


def check_repo_contracts() -> dict:
    evidence: dict = {}
    if not AGENTS_MD.exists():
        fail("AGENTS.md no existe")
    agents = AGENTS_MD.read_text(encoding="utf-8")
    evidence["agents_has_guardian"] = "guardian.py" in agents
    evidence["agents_has_thread_immunity"] = "thread_immunity.py start" in agents
    guardian_text = GUARDIAN_REPO.read_text(encoding="utf-8") if GUARDIAN_REPO.exists() else ""
    evidence["guardian_has_sms_hook"] = "inject_sovereign_context" in guardian_text
    evidence["guardian_uses_supabase_service_key"] = "SUPABASE_SERVICE_KEY" in guardian_text
    if not evidence["agents_has_guardian"]:
        fail("AGENTS.md no exige guardian.py")
    if not evidence["agents_has_thread_immunity"]:
        fail("AGENTS.md no exige thread_immunity.py start")
    if not evidence["guardian_has_sms_hook"]:
        fail("guardian.py no contiene sms_guardian_hook")
    return evidence


def write_local_receipt(session_id: str, payload: dict) -> tuple[Path, str]:
    session_dir = BRIDGE_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    path = session_dir / "startup_receipt.json"
    serialized = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    path.write_text(serialized, encoding="utf-8")
    return path, sha256_text(serialized)


def cmd_seed(_: argparse.Namespace) -> None:
    session_id = str(uuid.uuid4())
    axioms = fetch_axioms()
    for fingerprint, statement in REQUIRED_AXIOMS.items():
        if not axiom_exists(fingerprint, axioms):
            insert_axiom(fingerprint, statement)
    insert_event(
        session_id=session_id,
        thread_id="seed",
        event_type="SEED_APPLIED",
        topic="THREAD_IMMUNITY_GATE_V1",
        summary="Seed axioms applied or already present",
        evidence={"required_axioms": list(REQUIRED_AXIOMS.keys())},
    )
    print("THREAD_IMMUNITY_SEED_PASS")


def cmd_start(args: argparse.Namespace) -> None:
    session_id = str(uuid.uuid4())
    thread_id = args.thread_id
    topic = args.topic or "unknown"
    guardian_output = run_guardian()
    axioms = fetch_axioms()
    if not axioms:
        insert_event(
            session_id=session_id,
            thread_id=thread_id,
            event_type="STARTUP_FAIL",
            topic=topic,
            summary="No active sovereign axioms fetched",
            evidence={"guardian_sha256": sha256_text(guardian_output)},
        )
        fail("SMS sovereign_axioms vacío o inaccesible")
    missing = [fp for fp in REQUIRED_AXIOMS if not axiom_exists(fp, axioms)]
    repo_evidence = check_repo_contracts()
    receipt = {
        "session_id": session_id,
        "thread_id": thread_id,
        "topic": topic,
        "created_at": now_iso(),
        "guardian_output_sha256": sha256_text(guardian_output),
        "required_axioms_present": sorted(set(REQUIRED_AXIOMS) - set(missing)),
        "required_axioms_missing": missing,
        "repo_evidence": repo_evidence,
        "status": "PASS" if not missing else "FAIL",
    }
    receipt_path, receipt_sha = write_local_receipt(session_id, receipt)
    if missing:
        insert_event(
            session_id=session_id,
            thread_id=thread_id,
            event_type="STARTUP_FAIL",
            topic=topic,
            summary=f"Missing required axioms: {missing}",
            evidence=receipt,
            local_receipt_sha256=receipt_sha,
        )
        fail(f"faltan axiomas requeridos: {missing}")
    insert_event(
        session_id=session_id,
        thread_id=thread_id,
        event_type="STARTUP_PASS",
        topic=topic,
        summary="Startup verified by THREAD-IMMUNITY-GATE-v1",
        evidence=receipt,
        local_receipt_sha256=receipt_sha,
    )
    print(f"THREAD_IMMUNITY_SESSION_ID={session_id}")
    print(f"THREAD_IMMUNITY_RECEIPT={receipt_path}")
    print(f"THREAD_IMMUNITY_RECEIPT_SHA256={receipt_sha}")
    print("THREAD_IMMUNITY_STARTUP_PASS")


def cmd_close(args: argparse.Namespace) -> None:
    session_id = args.session_id
    thread_id = args.thread_id
    summary = args.summary
    canon = args.canon
    if not summary or len(summary.strip()) < 10:
        fail("--summary mínimo 10 caracteres")
    startup_events = supabase_request(
        "GET",
        f"thread_immunity_events?session_id=eq.{quote(session_id)}&event_type=eq.STARTUP_PASS&select=*&limit=1",
    )
    if not startup_events:
        insert_event(
            session_id=session_id,
            thread_id=thread_id,
            event_type="CLOSE_FAIL",
            summary="No STARTUP_PASS found for session",
            evidence={"session_id": session_id},
        )
        fail("no existe STARTUP_PASS para session_id")
    canon_written = False
    if canon:
        fingerprint = "THREAD_LESSON_" + sha256_text(canon)[:12].upper()
        insert_axiom(fingerprint, canon)
        canon_written = True
    evidence = {
        "startup_event_id": startup_events[0].get("id") if isinstance(startup_events, list) else None,
        "canon_written": canon_written,
        "closed_at": now_iso(),
    }
    insert_event(
        session_id=session_id,
        thread_id=thread_id,
        event_type="CLOSE_CANONIZED",
        summary=summary,
        canon_statement=canon,
        evidence=evidence,
    )
    print("THREAD_IMMUNITY_CLOSE_CANONIZED")


def cmd_verify(_: argparse.Namespace) -> None:
    failures: list[str] = []
    axioms = fetch_axioms()
    for fp in REQUIRED_AXIOMS:
        if not axiom_exists(fp, axioms):
            failures.append(f"missing_axiom:{fp}")
    try:
        check_repo_contracts()
    except SystemExit:
        failures.append("repo_contract_missing")
    starts = supabase_request(
        "GET",
        "thread_immunity_events?event_type=eq.STARTUP_PASS&select=session_id,thread_id,topic,created_at&order=created_at.desc&limit=100",
    )
    closes = supabase_request(
        "GET",
        "thread_immunity_events?event_type=eq.CLOSE_CANONIZED&select=session_id,created_at&order=created_at.desc&limit=200",
    )
    close_sessions = {c.get("session_id") for c in closes if isinstance(c, dict) and c.get("session_id")}
    now = datetime.now(timezone.utc)
    ttl = timedelta(hours=SESSION_TTL_HOURS)
    if isinstance(starts, list):
        for s in starts:
            sid = s.get("session_id")
            if not sid or sid in close_sessions:
                continue
            created_raw = s.get("created_at")
            try:
                created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except Exception:
                failures.append(f"bad_created_at:{sid}")
                continue
            if now - created > ttl:
                failures.append(f"session_without_close:{sid}:{s.get('thread_id')}:{s.get('topic')}")
    session_id = str(uuid.uuid4())
    if failures:
        insert_event(
            session_id=session_id,
            thread_id="github_actions_watchdog",
            event_type="WATCHDOG_FAIL",
            topic="THREAD_IMMUNITY_GATE_V1",
            summary="; ".join(failures),
            evidence={"failures": failures},
        )
        print("THREAD_IMMUNITY_WATCHDOG_FAIL")
        for f in failures:
            print(f"- {f}")
        sys.exit(2)
    insert_event(
        session_id=session_id,
        thread_id="github_actions_watchdog",
        event_type="WATCHDOG_PASS",
        topic="THREAD_IMMUNITY_GATE_V1",
        summary="All checks passed",
        evidence={"checked_at": now_iso()},
    )
    print("THREAD_IMMUNITY_WATCHDOG_PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="THREAD-IMMUNITY-GATE-v1")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_seed = sub.add_parser("seed")
    p_seed.set_defaults(func=cmd_seed)
    p_start = sub.add_parser("start")
    p_start.add_argument("--thread-id", required=True)
    p_start.add_argument("--topic", default="unknown")
    p_start.set_defaults(func=cmd_start)
    p_close = sub.add_parser("close")
    p_close.add_argument("--session-id", required=True)
    p_close.add_argument("--thread-id", default="manus_b")
    p_close.add_argument("--summary", required=True)
    p_close.add_argument("--canon", default=None)
    p_close.set_defaults(func=cmd_close)
    p_verify = sub.add_parser("verify")
    p_verify.set_defaults(func=cmd_verify)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
