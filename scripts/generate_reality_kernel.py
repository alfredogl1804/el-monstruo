#!/usr/bin/env python3
"""
Generador automático del Reality Kernel (ATLAS-3 v0.2).
Este script valida la existencia de los archivos base y asegura que el Kernel
esté sincronizado con la realidad del repositorio.
"""

import os
import sys
import yaml
import json
from datetime import datetime, timezone

KERNEL_DIR = "monstruo_reality_atlas"
FILES = {
    "veto": f"{KERNEL_DIR}/00_DOCTRINE_VETO.md",
    "matrix": f"{KERNEL_DIR}/01_ENTITY_MATRIX.md",
    "pulse": f"{KERNEL_DIR}/02_REALITY_PULSE.yaml"
}

def check_files_exist():
    """Verifica que los archivos del Reality Kernel existan."""
    missing = []
    for name, path in FILES.items():
        if not os.path.exists(path):
            missing.append(path)
    
    if missing:
        print(f"❌ Faltan archivos del Reality Kernel: {missing}")
        sys.exit(1)
    print("✅ Todos los archivos del Reality Kernel están presentes.")

def validate_pulse():
    """Valida la estructura del REALITY_PULSE."""
    try:
        with open(FILES["pulse"], "r") as f:
            pulse = yaml.safe_load(f)
            
        required_keys = ["schema_version", "global_health", "vitals", "active_gaps"]
        for key in required_keys:
            if key not in pulse:
                print(f"❌ REALITY_PULSE no tiene la clave requerida: {key}")
                sys.exit(1)
                
        print("✅ REALITY_PULSE es válido.")
    except Exception as e:
        print(f"❌ Error validando REALITY_PULSE: {e}")
        sys.exit(1)

def main():
    print("=== Monstruo Reality Kernel Generator & Validator ===")
    
    if not os.path.exists(KERNEL_DIR):
        os.makedirs(KERNEL_DIR)
        print(f"Creado directorio {KERNEL_DIR}")
        
    check_files_exist()
    validate_pulse()
    
    print("\n✅ Reality Kernel validado correctamente.")
    print("Nota: Este script es un scaffold inicial. En el futuro, se conectará")
    # print("al AST del kernel y a Supabase para auto-generar la matriz.")

if __name__ == "__main__":
    main()
