#!/usr/bin/env python3.11
"""
ping_sabios.py — Pre-vuelo: Valida conexión con los 6 sabios en <15 segundos.
================================================================================
EJECUTAR SIEMPRE antes de una consulta real para garantizar que las APIs están vivas.

Uso:
    python3.11 ping_sabios.py
"""

import asyncio
import os
import sys

# Agregar el directorio del script al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import ping_todos, resumen_resultados


async def main():
    print("=" * 60)
    print("🏓 PRE-VUELO: Validando conexión con los 6 sabios...")
    print("=" * 60)
    print()

    resultados = await ping_todos()
    print(resumen_resultados(resultados))

    exitosos = sum(1 for r in resultados if r.get("exito"))
    total = len(resultados)

    print()
    if exitosos == total:
        print("✅ TODOS LOS SABIOS OPERATIVOS. Listo para consulta real.")
        return 0
    elif exitosos >= 3:
        print(f"⚠️  {exitosos}/{total} sabios operativos. Mínimo cumplido (semilla v7.3 requiere ≥3).")
        fallidos = [r for r in resultados if not r.get("exito")]
        for f in fallidos:
            print(f"   ❌ {f['sabio']}: {f.get('error', 'Error desconocido')[:100]}")
        return 0
    else:
        print(f"🛑 ALTO: Solo {exitosos}/{total} sabios operativos.")
        print("   Protocolo semilla v7.3: NO PROCEDER con menos de 3 sabios.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
