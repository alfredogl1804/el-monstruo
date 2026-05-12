#!/usr/bin/env python
"""
Smoke test Sprint CATASTRO-C-SLICE-001.

Valida 4 cosas binariamente:
  1. radar_classifier en modo heuristic extrae repos GitHub + HF de un Markdown sample.
  2. radar_classifier en modo LLM (si OPENAI_API_KEY) devuelve schema válido.
  3. Migracion 0018 aplica en Supabase prod (catastro_repos table existe).
  4. Upsert end-to-end: insertar 2 repos sample y leerlos de vuelta.

Exit codes:
  0 = OK (todos los gates verde)
  1 = FAIL (algun gate rojo, evidencia en stderr)
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GATES = {"heuristic": False, "llm": None, "table": False, "upsert": False}


# ============================================================================
# Gate 1: heuristic mode
# ============================================================================
def _load_rc():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "radar_classifier",
        os.path.join(os.path.dirname(__file__), "..", "kernel", "catastro", "radar_classifier.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.RadarClassifier


def gate_heuristic() -> bool:
    RadarClassifier = _load_rc()
    sample_md = """
# AI Trending — 2026-05-11

## Top repos this week
- [OpenAI/gpt-engineer](https://github.com/OpenAI/gpt-engineer) — 50K stars
- [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) — 175K stars
- Try the new model at https://huggingface.co/meta-llama/Llama-3.3-70B
- Bug: https://github.com/foo/bar.

## Stories
- HN: https://huggingface.co/spaces/cool-demo (skip)
"""
    classifier = RadarClassifier(use_llm=False)
    result = classifier.parse(sample_md, fuente_hint="github_trending")

    print(f"[heuristic] extraidos={result.total_extraidos} repos")
    for r in result.repos:
        print(f"  - {r.id} ({r.fuente})")

    expected_ids = {
        "github:OpenAI/gpt-engineer",
        "github:Significant-Gravitas/AutoGPT",
        "github:foo/bar",
        "hf:meta-llama/Llama-3.3-70B",
    }
    got_ids = {r.id for r in result.repos}
    missing = expected_ids - got_ids
    if missing:
        print(f"[heuristic] FAIL: faltan ids {missing}", file=sys.stderr)
        return False
    if len(result.repos) < 4:
        print(f"[heuristic] FAIL: solo {len(result.repos)} extraidos, esperaba >= 4", file=sys.stderr)
        return False
    print("[heuristic] OK")
    return True


# ============================================================================
# Gate 2: LLM mode (opcional, solo si OPENAI_API_KEY)
# ============================================================================
def gate_llm() -> bool:
    if not os.environ.get("OPENAI_API_KEY"):
        print("[llm] SKIP (no OPENAI_API_KEY)")
        return True
    RadarClassifier = _load_rc()
    sample_md = """
# AI Daily Digest

Today's top AI tools:
1. **AutoGPT** by Significant-Gravitas — autonomous agent framework. https://github.com/Significant-Gravitas/AutoGPT (175k stars)
2. **vLLM** — high-throughput inference. https://github.com/vllm-project/vllm
3. New release: Llama 3.3 70B at https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
"""
    classifier = RadarClassifier(use_llm=True)
    result = classifier.parse(sample_md, fuente_hint="github_trending")
    print(f"[llm] extraidos={result.total_extraidos} repos, conf={result.confidence:.2f}")
    for r in result.repos:
        print(f"  - {r.id} | {r.fuente} | topics={r.topics[:3]}")
    if result.total_extraidos < 2:
        print(f"[llm] FAIL: solo {result.total_extraidos} extraidos", file=sys.stderr)
        return False
    print("[llm] OK")
    return True


# ============================================================================
# Gate 3: tabla existe en Supabase
# ============================================================================
def gate_table() -> bool:
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not sb_url or not sb_key:
        print("[table] SKIP (no SUPABASE creds)", file=sys.stderr)
        return False
    import urllib.request
    req = urllib.request.Request(
        f"{sb_url}/rest/v1/catastro_repos?select=count",
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Prefer": "count=exact",
            "Range": "0-0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            cr = resp.headers.get("Content-Range", "")
            print(f"[table] OK: HTTP {resp.status}, content-range={cr}")
            return True
    except Exception as e:
        print(f"[table] FAIL: {e}", file=sys.stderr)
        return False


# ============================================================================
# Gate 4: upsert end-to-end
# ============================================================================
def gate_upsert() -> bool:
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not sb_url or not sb_key:
        print("[upsert] SKIP (no SUPABASE creds)", file=sys.stderr)
        return False
    import urllib.request
    rows = [
        {
            "id": "github:smoke-test/catastro-c-slice-001-A",
            "nombre": "smoke-A",
            "proveedor": "smoke-test",
            "url": "https://github.com/smoke-test/A",
            "fuente": "github_trending",
            "stars_count": 1,
            "topics": ["smoke", "test"],
            "classification": {"confidence": 0.4, "notes": "smoke"},
        },
        {
            "id": "github:smoke-test/catastro-c-slice-001-B",
            "nombre": "smoke-B",
            "proveedor": "smoke-test",
            "url": "https://github.com/smoke-test/B",
            "fuente": "github_trending",
            "stars_count": 2,
            "topics": ["smoke"],
            "classification": {"confidence": 0.4, "notes": "smoke"},
        },
    ]
    req = urllib.request.Request(
        f"{sb_url}/rest/v1/catastro_repos?on_conflict=id",
        data=json.dumps(rows).encode(),
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            print(f"[upsert] OK: insertados {len(data)} rows")
            for r in data:
                print(f"  - {r.get('id')}")
            return len(data) == 2
    except Exception as e:
        print(f"[upsert] FAIL: {e}", file=sys.stderr)
        try:
            print(f"  detail: {e.read().decode()}", file=sys.stderr)
        except Exception:
            pass
        return False


# ============================================================================
# main
# ============================================================================
if __name__ == "__main__":
    GATES["heuristic"] = gate_heuristic()
    GATES["llm"] = gate_llm()
    GATES["table"] = gate_table()
    GATES["upsert"] = gate_upsert()

    print("\n=== RESUMEN GATES ===")
    for k, v in GATES.items():
        sym = "OK" if v else ("SKIP" if v is None else "FAIL")
        print(f"  {k}: {sym}")

    failed = [k for k, v in GATES.items() if v is False]
    sys.exit(1 if failed else 0)
