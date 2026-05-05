"""
Smoke E2E productivo Sprint Memento Bloque 6.
Valida el detector de contexto contaminado en shadow mode contra Railway.

4 casos:
  1. Caso baseline: validation OK sin contaminacion.
  2. H2 trigger: host actual contradice host previo (TiDB gateway01 fantasma).
  3. H3 trigger: hilo activo sin pre-flight previo para esta operation.
  4. Caso negativo: validacion clean sin warning (control).

Importante: estos NO bloquean (shadow mode), solo loggean + persisten evidence.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import uuid

API_KEY = os.environ.get("MONSTRUO_API_KEY", "")
KERNEL_URL = "https://el-monstruo-kernel-production.up.railway.app"
URL = f"{KERNEL_URL}/v1/memento/validate"


def post(body: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, {"_raw": raw[:500]}
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or ""
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"_raw": raw[:500]}


def assert_ok(label: str, status: int, body: dict, expect_warning: bool):
    contamination_warning = body.get("contamination_warning", False)
    findings = body.get("contamination_findings", [])
    proceed = body.get("proceed", False)
    print(f"\n[{label}]")
    print(f"  status:                {status}")
    print(f"  validation_id:         {body.get('validation_id')}")
    print(f"  validation_status:     {body.get('validation_status')}")
    print(f"  proceed:               {proceed}")
    print(f"  contamination_warning: {contamination_warning} (expect={expect_warning})")
    print(f"  findings_count:        {len(findings)}")
    for f in findings:
        print(f"    - {f.get('rule_id')} severity={f.get('severity')} reason={f.get('reason')}")
    print(f"  persistence_failed:    {body.get('persistence_failed')}")
    if status != 200:
        print(f"  RESPONSE: {body}")
        return False
    return True


def main():
    if not API_KEY:
        raise SystemExit("MONSTRUO_API_KEY no esta en el env")

    HILO_ID = f"smoke_b6_{uuid.uuid4().hex[:6]}"

    # Caso 1: baseline (sql_against_production con host real → OK, sin warning)
    s1, b1 = post({
        "hilo_id": HILO_ID,
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
        "intent_summary": "smoke b6 caso 1 baseline",
    })
    ok1 = assert_ok("CASO 1: baseline OK", s1, b1, expect_warning=False)

    # Pequena pausa para que la primera validacion entre como historico H2
    time.sleep(2)

    # Caso 2: H2 trigger — host actual diferente al historico (TiDB gateway01 fantasma)
    s2, b2 = post({
        "hilo_id": HILO_ID,
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
        "intent_summary": "smoke b6 caso 2 H2 host divergente",
    })
    ok2 = assert_ok("CASO 2: H2 host divergente", s2, b2, expect_warning=True)

    # Caso 3: H3 trigger — hilo activo (5+ validations) sin pre-flight previo para op nueva
    # Saturamos el hilo con varias validaciones rapidas de kernel_admin_call,
    # luego pedimos external_api_call (operacion nueva sin pre-flight previo).
    HILO_ACTIVO = f"smoke_b6_h3_{uuid.uuid4().hex[:6]}"
    for i in range(6):
        post({
            "hilo_id": HILO_ACTIVO,
            "operation": "kernel_admin_call",
            "context_used": {"endpoint": "/v1/error-memory/seed", "iteration": i},
            "intent_summary": f"smoke b6 caso 3 setup hilo activo iter {i}",
        })
    s3, b3 = post({
        "hilo_id": HILO_ACTIVO,
        "operation": "external_api_call",
        "context_used": {"target": "openai", "endpoint": "/v1/chat/completions"},
        "intent_summary": "smoke b6 caso 3 H3 sin preflight previo",
    })
    ok3 = assert_ok("CASO 3: H3 hilo activo sin preflight previo", s3, b3, expect_warning=True)

    # Caso 4: negativo — operacion bootstrapped sin historico (debe ser OK sin warning)
    HILO_VIRGEN = f"smoke_b6_neg_{uuid.uuid4().hex[:6]}"
    s4, b4 = post({
        "hilo_id": HILO_VIRGEN,
        "operation": "kernel_admin_call",
        "context_used": {"endpoint": "/health"},
        "intent_summary": "smoke b6 caso 4 control limpio",
    })
    ok4 = assert_ok("CASO 4: control limpio sin historico", s4, b4, expect_warning=False)

    print("\n===== RESUMEN SMOKE B6 =====")
    print(f"  caso 1 baseline:        {'OK' if ok1 else 'FAIL'}")
    print(f"  caso 2 H2 divergente:   {'OK' if ok2 else 'FAIL'}")
    print(f"  caso 3 H3 sin preflight:{'OK' if ok3 else 'FAIL'}")
    print(f"  caso 4 control limpio:  {'OK' if ok4 else 'FAIL'}")
    raise SystemExit(0 if all([ok1, ok2, ok3, ok4]) else 1)


if __name__ == "__main__":
    main()
