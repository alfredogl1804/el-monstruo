#!/usr/bin/env python3
"""
verify_embrion_post_fix.py

Verifica el estado real del embrion-loop usando el genome público
/v1/genome/now?full=1 (no requiere API key).

Distingue entre:
  - SANO Y ACTIVO: running=true, cycle_count avanza, errors=[]
  - STANDBY INTENCIONAL: running=true, last_result indica STANDBY
  - CAÍDO POR ERROR: errors[] no vacío, especialmente con kimi-k2-6
  - APAGADO: running=false

Exit codes:
  0 = sano o standby intencional
  1 = caído o con errores
  2 = kernel inalcanzable

Uso:
  python3 scripts/verify_embrion_post_fix.py [--sleep 30]
"""
import argparse
import json
import sys
import time
import urllib.request

KERNEL_DEFAULT = "https://el-monstruo-kernel-production.up.railway.app"


def _find_dict_with_key(obj, target_key: str):
    """Busca recursivamente el primer dict que tenga `target_key`."""
    if isinstance(obj, dict):
        if target_key in obj:
            return obj
        for v in obj.values():
            result = _find_dict_with_key(v, target_key)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_dict_with_key(item, target_key)
            if result is not None:
                return result
    return None


def fetch_embrion(kernel_url: str) -> dict:
    url = f"{kernel_url}/v1/genome/now?full=1"
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    found = _find_dict_with_key(data, "cycle_count")
    return found if found is not None else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", default=KERNEL_DEFAULT)
    parser.add_argument("--sleep", type=int, default=30, help="seconds between snapshots")
    args = parser.parse_args()

    print("==> verify_embrion_post_fix.py")
    print(f"    kernel: {args.kernel}")
    print()

    print("[1/3] Snapshot 1 del embrion...")
    try:
        snap1 = fetch_embrion(args.kernel)
    except Exception as e:
        print(f"ERROR: kernel inalcanzable: {e}", file=sys.stderr)
        return 2

    if not snap1:
        print("ERROR: embrion_loop no encontrado en genome.", file=sys.stderr)
        return 2

    running1 = snap1.get("running")
    cycle1 = snap1.get("cycle_count")
    errors1 = snap1.get("errors", [])
    last_result = snap1.get("last_result", "") or ""
    last_trigger = (snap1.get("last_trigger") or {}).get("type", "")

    print(f"    running       : {running1}")
    print(f"    cycle_count   : {cycle1}")
    print(f"    errors[]      : {errors1!r}"[:200])
    print(f"    last_trigger  : {last_trigger}")
    print()

    print(f"[2/3] Esperando {args.sleep}s para snapshot 2...")
    time.sleep(args.sleep)

    snap2 = fetch_embrion(args.kernel)
    cycle2 = snap2.get("cycle_count")
    errors2 = snap2.get("errors", [])

    print(f"    cycle_count   : {cycle2}")
    print(f"    errors[]      : {errors2!r}"[:200])
    print()

    print("[3/3] Veredicto...")
    print("=" * 60)

    if not running1:
        print("❌ EMBRION APAGADO")
        print(f"    running={running1}")
        return 1

    has_kimi = any(
        "kimi-k2-6" in str(e).lower() or "kimi_k2_6" in str(e).lower()
        for e in (errors2 or [])
    )
    if has_kimi:
        print("❌ EMBRION CAÍDO con kimi-k2-6 ACTIVO")
        print(f"    errors: {errors2}")
        print("    Ver: discovery_forense/INCIDENTES/EMBRION_DOWN_2026_05_26_kimi_k2_6_catalog_key_mismatch.md")
        return 1

    if errors2:
        print("⚠️  EMBRION CON ERRORES (no kimi-k2-6)")
        print(f"    errors: {errors2}")
        print("    Investigar logs Railway servicio embrion-loop.")
        return 1

    if "STANDBY" in last_result.upper():
        print("✅ EMBRION EN STANDBY INTENCIONAL")
        print(f"    running={running1}, errors=[], cycle_count={cycle2}")
        print("    Última instrucción procesada: STANDBY (mensaje_alfredo)")
        print("    Para reanudar: enviar mensaje al embrion con instrucción explícita.")
        return 0

    if cycle1 != cycle2:
        print("✅ EMBRION SANO Y ACTIVO")
        print(f"    cycle_count avanzó: {cycle1} → {cycle2}")
        print("    errors=[]")
        return 0
    else:
        print("⚠️  EMBRION RUNNING PERO CICLO NO AVANZA")
        print(f"    cycle_count estancado en {cycle1} durante {args.sleep}s")
        print("    Posible: cooldown post-thought (think_cooldown_s=300)")
        print(f"    Re-ejecutar con --sleep 350 para confirmar.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
