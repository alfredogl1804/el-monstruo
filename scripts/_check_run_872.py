#!/usr/bin/env python3
"""Verifica el estado final del run de smoke Sprint 87.2."""
import json
import os
import sys
import urllib.request

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "e2e_1778013013_888e5d"
API = "https://el-monstruo-kernel-production.up.railway.app"
KEY = os.environ.get("MONSTRUO_API_KEY", "")

req = urllib.request.Request(
    f"{API}/v1/e2e/runs/{RUN_ID}",
    headers={"X-API-Key": KEY},
)
with urllib.request.urlopen(req, timeout=30) as r:
    d = json.loads(r.read())

run = d.get("run", {})
print(f"estado            = {run.get('estado')}")
print(f"pipeline_step     = {run.get('pipeline_step')}")
print(f"deploy_url        = {run.get('deploy_url')}")
print(f"critic_visual_score = {run.get('critic_visual_score')}")
print(f"veredicto_alfredo = {run.get('veredicto_alfredo')}")
print()

for s in d.get("steps", []):
    sn = s.get("step_name", "")
    if sn in ("DEPLOY", "CRITIC", "TRAFFIC", "VEREDICTO"):
        op = s.get("output_payload") or {}
        print(f"=== {sn} status={s.get('status')} duration_ms={s.get('duration_ms')} ===")
        for k in [
            "source", "provider", "real_deploy", "deploy_url",
            "score", "veredicto", "modelo_consultado",
            "vigia_status", "tracking_endpoint", "tracking_script",
            "fallback_reason", "error_message",
        ]:
            if k in op and op[k] is not None:
                v = op[k]
                if isinstance(v, str) and len(v) > 100:
                    v = v[:97] + "..."
                print(f"  {k}: {v}")
        sub = op.get("sub_scores")
        if sub:
            print(f"  sub_scores: {sub}")
        screenshot = op.get("screenshot")
        if screenshot:
            print(f"  screenshot.source: {screenshot.get('source')}")
            print(f"  screenshot.path:   {screenshot.get('screenshot_path')}")
            if screenshot.get("fallback_reason"):
                print(f"  screenshot.fallback_reason: {screenshot.get('fallback_reason')}")
        if s.get("error_message"):
            print(f"  STEP ERROR: {s.get('error_message')[:200]}")
        print()
