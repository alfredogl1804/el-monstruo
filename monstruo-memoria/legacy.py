#!/usr/bin/env python3
"""
LEGACY — Legado del Hilo Moribundo.

Problema que resuelve: Cuando un hilo de Manus termina o está por morir,
todo lo que descubrió muere con él. El siguiente hilo empieza de cero.

Solución: Este script extrae todo el conocimiento nuevo del hilo actual
y lo deposita en el kernel del Monstruo. El siguiente hilo puede
recuperarlo via inject.py.

Uso: python3 legacy.py "Resumen de lo que hice en este hilo"
Ejecutar ANTES de cerrar el hilo.
"""

import os
import sys
import glob
import json
import requests
import time as time_mod
from datetime import datetime

# --- Config ---
KERNEL_URL = os.environ.get(
    "MONSTRUO_KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app"
)
KERNEL_KEY = os.environ.get(
    "MONSTRUO_API_KEY",
    "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259"
)
SANDBOX_HOME = os.environ.get("HOME", "/home/ubuntu")


def collect_new_knowledge():
    """Recolecta archivos nuevos/modificados en las últimas 4 horas."""
    cutoff = time_mod.time() - (4 * 3600)  # 4 horas

    new_files = []
    for f in glob.glob(os.path.join(SANDBOX_HOME, "*.md")):
        if os.path.getmtime(f) > cutoff:
            name = os.path.basename(f)
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read(3000)
                new_files.append({"name": name, "content": content})
            except Exception:
                pass

    return new_files


def deposit_to_kernel(content, source, doc_type="legacy"):
    """Deposita un documento en el kernel via wrapper con retry."""
    for attempt in range(3):
        try:
            from kernel_client import knowledge_ingest
            result = knowledge_ingest(
                content=content[:3000],
                source=source,
                doc_type=doc_type
            )
            if result.get("ingested"):
                return True
            print(f"[legacy] No ingested en intento {attempt + 1}")
        except Exception as e:
            if "timeout" in str(e).lower() or "Timeout" in str(e):
                wait = 2 ** attempt
                print(f"[legacy] Timeout, retry en {wait}s...")
                time_mod.sleep(wait)
            else:
                print(f"[legacy] Error: {e}")
                return False
    return False


def main():
    # Resumen manual del hilo (argumento opcional)
    manual_summary = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

    timestamp = datetime.utcnow().isoformat()
    print(f"[legacy] Recolectando conocimiento del hilo... {timestamp}")

    # Recolectar archivos nuevos
    new_files = collect_new_knowledge()
    print(f"[legacy] {len(new_files)} archivos nuevos/modificados encontrados")

    deposited = 0
    failed = 0

    # Depositar resumen manual si existe
    if manual_summary:
        ok = deposit_to_kernel(
            f"LEGADO DE HILO ({timestamp}): {manual_summary}",
            f"legacy_manual_{timestamp}",
            "legacy_summary"
        )
        if ok:
            deposited += 1
            print(f"[legacy] Resumen manual depositado")
        else:
            failed += 1

    # Depositar cada archivo nuevo
    for f in new_files:
        header = f"LEGADO DE HILO ({timestamp}) — Archivo: {f['name']}\n\n"
        ok = deposit_to_kernel(
            header + f["content"],
            f"legacy_{f['name']}_{timestamp}",
            "legacy_file"
        )
        if ok:
            deposited += 1
            print(f"[legacy] Depositado: {f['name']}")
        else:
            failed += 1
            print(f"[legacy] FALLÓ: {f['name']}")

    total = len(new_files) + (1 if manual_summary else 0)
    print(f"[legacy] Total depositados: {deposited}/{total} ({failed} fallidos)")
    print(f"[legacy] El conocimiento de este hilo sobrevivirá.")


if __name__ == "__main__":
    main()
