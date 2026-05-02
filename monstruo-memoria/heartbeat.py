#!/usr/bin/env python3
"""
HEARTBEAT — Latido del Monstruo dentro de Manus.

Problema que resuelve: Cuando el sandbox de Manus se compacta, el agente
pierde todo lo que sabía. No sabe qué perdió. Empieza a dar vueltas.

Solución: Este script se ejecuta PERIÓDICAMENTE dentro de cualquier hilo
de Manus. Cada N minutos:
1. Lee el estado actual del sandbox (archivos, notas, decisiones)
2. Lo comprime en un "snapshot" de contexto
3. Lo sube al kernel del Monstruo via POST /v1/knowledge/ingest (chunked + retry)
4. Guarda una copia local en un archivo RECOVERY.md

Cuando el sandbox se compacta, el agente puede:
- Leer RECOVERY.md (si sobrevivió a la compactación)
- O hacer curl al kernel para recuperar el snapshot

Uso: python3 heartbeat.py
Ejecutar al inicio del hilo y cada 10 minutos.
"""

import glob
import hashlib
import json
import os
import time
from datetime import datetime

import requests

# --- Config ---
KERNEL_URL = os.environ.get("MONSTRUO_KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app")
KERNEL_KEY = os.environ.get("MONSTRUO_API_KEY", "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259")
SANDBOX_HOME = os.environ.get("HOME", "/home/ubuntu")
RECOVERY_FILE = os.path.join(SANDBOX_HOME, "RECOVERY.md")
SNAPSHOT_DIR = os.path.join(SANDBOX_HOME, ".monstruo_snapshots")

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def scan_sandbox():
    """Escanea el sandbox y extrae información clave."""
    findings = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "md_files": [],
        "key_decisions": [],
        "active_threads": [],
        "open_problems": [],
        "verified_facts": [],
    }

    # Buscar todos los .md en home
    md_files = sorted(glob.glob(os.path.join(SANDBOX_HOME, "*.md")))
    for f in md_files:
        name = os.path.basename(f)
        try:
            size = os.path.getsize(f)
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
            # Leer primeras 5 líneas como resumen
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                lines = [l.strip() for l in fh.readlines()[:5] if l.strip()]
            findings["md_files"].append(
                {"name": name, "size": size, "modified": mtime, "preview": " | ".join(lines[:3])}
            )
        except Exception:
            pass

    # Buscar archivos de decisiones y estado
    decision_keywords = ["DECISION", "VERIFICADO", "CONFIRMADO", "DESCARTADO", "CORRECCIÓN"]
    for f in md_files:
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read(5000)
            for kw in decision_keywords:
                if kw in content.upper():
                    # Extraer líneas con la keyword
                    for line in content.split("\n"):
                        if kw.lower() in line.lower() and len(line) > 20:
                            findings["key_decisions"].append(line.strip()[:200])
                    break
        except Exception:
            pass

    # Buscar archivos de hilos/orquestación
    thread_files = [
        f
        for f in md_files
        if any(kw in os.path.basename(f).upper() for kw in ["HILO", "THREAD", "ORQUEST", "COMUNICACION", "MAPA"])
    ]
    for f in thread_files:
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read(3000)
            findings["active_threads"].append({"file": os.path.basename(f), "summary": content[:500]})
        except Exception:
            pass

    return findings


def build_recovery_doc(findings):
    """Construye el documento RECOVERY.md que sobrevive a compactaciones."""
    lines = [
        "# RECOVERY — Estado del Monstruo",
        f"**Generado:** {findings['timestamp']}",
        "**Propósito:** Si perdiste contexto, lee este archivo PRIMERO.",
        "",
        "## Archivos en el sandbox",
        "",
    ]

    for f in findings["md_files"][:20]:
        lines.append(f"- `{f['name']}` ({f['size']}B, {f['modified']}) — {f['preview'][:100]}")

    lines.extend(["", "## Decisiones clave encontradas", ""])
    for d in findings["key_decisions"][:15]:
        lines.append(f"- {d}")

    lines.extend(["", "## Hilos/Orquestación", ""])
    for t in findings["active_threads"][:5]:
        lines.append(f"### {t['file']}")
        lines.append(t["summary"][:300])
        lines.append("")

    lines.extend(
        [
            "",
            "## Cómo recuperar contexto completo",
            "",
            "```bash",
            "# Opción 1: Query al kernel del Monstruo",
            f'curl -s -X POST -H "X-API-Key: {KERNEL_KEY}" \\',
            '  -H "Content-Type: application/json" \\',
            f"  {KERNEL_URL}/v1/knowledge/query \\",
            '  -d \'{"query": "estado completo del Monstruo decisiones hilos modelos", "mode": "naive", "top_k": 10}\'',
            "```",
            "",
            "```bash",
            "# Opción 2: Leer archivos del sandbox",
            "ls -lt ~/*.md | head -20",
            "```",
            "",
            "## Modelos verificados de los 6 Sabios (27 abril 2026)",
            "",
            "| Sabio | Model ID | Fuente |",
            "|-------|----------|--------|",
            "| GPT | gpt-5.5 | platform.openai.com |",
            "| Claude | claude-opus-4-7 | anthropic.com |",
            "| Gemini | gemini-3.1-pro-preview | ai.google.dev |",
            "| Grok | grok-4.20-0309-reasoning | docs.x.ai |",
            "| DeepSeek | deepseek-v4-pro | api-docs.deepseek.com |",
            "| Perplexity | sonar-reasoning-pro | docs.perplexity.ai |",
            "",
            "## Kernel del Monstruo",
            "",
            f"- URL: {KERNEL_URL}",
            f"- API Key: {KERNEL_KEY}",
            "- Endpoints: /health, /v1/knowledge/query, /v1/knowledge/ingest, /v1/stats",
            "",
            "## REGLA DE ORO",
            "",
            "**NUNCA confíes en tu entrenamiento para versiones, modelos, o datos.**",
            "**SIEMPRE investiga en tiempo real antes de afirmar algo.**",
            "**Si no estás seguro, haz curl al kernel o investiga en la web.**",
            "",
        ]
    )

    return "\n".join(lines)


def upload_to_kernel_chunked(recovery_doc, findings):
    """Sube el snapshot al kernel en chunks de ~2KB con retry."""
    content_hash = hashlib.md5(recovery_doc.encode()).hexdigest()[:8]
    ts = findings["timestamp"]

    # Dividir en chunks de ~2000 chars
    CHUNK_SIZE = 2000
    chunks = []
    for i in range(0, len(recovery_doc), CHUNK_SIZE):
        chunks.append(recovery_doc[i : i + CHUNK_SIZE])

    success_count = 0
    fail_count = 0

    for idx, chunk in enumerate(chunks):
        payload = {
            "content": chunk,
            "source": f"heartbeat_{ts}_{content_hash}_chunk{idx}of{len(chunks)}",
            "doc_type": "heartbeat_snapshot",
        }

        # Retry con backoff via kernel_client
        for attempt in range(3):
            try:
                from kernel_client import knowledge_ingest

                result = knowledge_ingest(content=chunk, source=payload["source"], doc_type="heartbeat_snapshot")
                if result.get("ingested"):
                    success_count += 1
                    break
                else:
                    print(f"[heartbeat] Chunk {idx}: no ingested")
            except requests.exceptions.Timeout:
                wait = 2**attempt
                print(f"[heartbeat] Chunk {idx}: timeout, retry en {wait}s...")
                time.sleep(wait)
            except Exception as e:
                print(f"[heartbeat] Chunk {idx}: error {e}")
                break
        else:
            fail_count += 1

    return success_count, fail_count, len(chunks)


def save_local(recovery_doc, findings):
    """Guarda copia local."""
    # RECOVERY.md siempre se sobreescribe con lo más reciente
    with open(RECOVERY_FILE, "w", encoding="utf-8") as f:
        f.write(recovery_doc)

    # Snapshot con timestamp para historial
    snapshot_file = os.path.join(SNAPSHOT_DIR, f"snapshot_{findings['timestamp'].replace(':', '-')}.json")
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)

    # Limpiar snapshots viejos (mantener últimos 10)
    snapshots = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "snapshot_*.json")))
    for old in snapshots[:-10]:
        os.remove(old)


def main():
    print(f"[heartbeat] Escaneando sandbox... {datetime.utcnow().isoformat()}")
    findings = scan_sandbox()
    print(
        f"[heartbeat] Encontrados: {len(findings['md_files'])} archivos, "
        f"{len(findings['key_decisions'])} decisiones, "
        f"{len(findings['active_threads'])} hilos"
    )

    recovery_doc = build_recovery_doc(findings)

    # Guardar local PRIMERO (siempre funciona)
    save_local(recovery_doc, findings)
    print(f"[heartbeat] RECOVERY.md guardado ({len(recovery_doc)} chars)")

    # Subir al kernel en chunks con retry
    ok, fail, total = upload_to_kernel_chunked(recovery_doc, findings)
    print(f"[heartbeat] Kernel upload: {ok}/{total} chunks OK, {fail} failed")

    return recovery_doc


if __name__ == "__main__":
    main()
