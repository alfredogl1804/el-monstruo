#!/usr/bin/env python3
"""Inspecciona el step CRITIC de los 5 runs del eval Sprint 88.1+88.2 post-revert."""
import json
import os
import sys
import urllib.request

KEY = os.environ["MONSTRUO_API_KEY"]
BASE = "https://el-monstruo-kernel-production.up.railway.app"

RIDS = [
    ("pintura_oleo_merida", "e2e_1778131933_3dbfc0"),
    ("cursos_python_latam", "e2e_1778131934_8e1839"),  # 92 PASS
    ("cafe_polanco", "e2e_1778131935_98406b"),
    ("joyeria_oaxaca", "e2e_1778131936_4cecd4"),  # 45 lowest
    ("coaching_ctos", "e2e_1778131937_df9d8e"),
]

for tag, rid in RIDS:
    print(f"\n=== {tag} ({rid}) ===")
    req = urllib.request.Request(f"{BASE}/v1/e2e/runs/{rid}", headers={"X-API-Key": KEY})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read().decode())
    steps = d.get("steps", [])
    # Buscar step de critic visual
    critic_step = None
    for s in steps:
        sname = (s.get("step_name") or "").upper()
        if sname == "CRITIC" or "CRITIC" in sname:
            critic_step = s
            break
    if critic_step is None:
        print("Steps disponibles:")
        for s in steps:
            print(" -", s.get("step_name"))
        continue
    payload = critic_step.get("output_payload") or {}
    print("step_name:", critic_step.get("step_name"), "| step_number:", critic_step.get("step_number"))
    print("source:", payload.get("source"))
    print("score_total:", payload.get("score_total") or payload.get("total_score"))
    print("sub_scores:", payload.get("sub_scores"))
    razones = payload.get("razones_mejora") or payload.get("razones") or payload.get("issues")
    if isinstance(razones, list):
        for r_ in razones[:5]:
            print(" -", r_)
    else:
        print("razones:", razones)
