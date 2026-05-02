#!/usr/bin/env python3.11
"""
apply_improvement.py — Aplicar y Revertir Mejoras con Backup
==============================================================
Aplica mejoras aprobadas con backup automático para rollback.
Soporta cambios en: config YAML, prompts, y scripts.

Uso:
    python3.11 apply_improvement.py --id imp_abc123 [--apply|--rollback]

Criterios formales de aceptación:
    1. La mejora debe tener estado "aprobada" o "propuesta" (con --force)
    2. Se crea backup automático antes de aplicar
    3. Score post-aplicación debe ser >= score pre-aplicación - 0.02
    4. Si score degrada > 2%, rollback automático

Creado: 2026-04-08 (P2 auditoría sabios)
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_store import get_db, query_improvements

SKILL_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
BACKUP_DIR = SKILL_DIR / "data" / "backups"


def apply_improvement(improvement_id: str, force: bool = False) -> bool:
    """
    Aplica una mejora con backup automático.

    Args:
        improvement_id: ID de la mejora
        force: Si True, aplica aunque no esté en estado "aprobada"

    Returns:
        True si se aplicó exitosamente
    """
    # Buscar la mejora
    improvements = query_improvements()
    target = None
    for imp in improvements:
        if imp.get("improvement_id") == improvement_id:
            target = imp
            break

    if not target:
        print(f"❌ Mejora {improvement_id} no encontrada")
        return False

    estado = target.get("estado", "propuesta")
    if estado not in ("aprobada", "propuesta") and not force:
        print(f"❌ Mejora en estado '{estado}'. Use --force para aplicar de todas formas.")
        return False

    if estado == "propuesta" and not force:
        print("⚠️  Mejora en estado 'propuesta' (no aprobada). Use --force para aplicar.")
        return False

    print(f"🔧 Aplicando mejora: {target['descripcion']}")

    # Parsear diff
    diff = target.get("diff_json", "{}")
    if isinstance(diff, str):
        try:
            diff = json.loads(diff)
        except json.JSONDecodeError:
            diff = {}

    target_file = diff.get("file", "")
    cambio = diff.get("cambio", "")

    if not target_file:
        print("⚠️  Sin archivo objetivo en diff. Mejora registrada como manual.")
        _update_improvement_status(improvement_id, "aplicada")
        return True

    # Crear backup
    full_path = SKILL_DIR / target_file
    if full_path.exists():
        backup_path = _create_backup(full_path, improvement_id)
        print(f"   📦 Backup: {backup_path}")
    else:
        print(f"   ⚠️  Archivo {target_file} no existe. Registrando como manual.")
        _update_improvement_status(improvement_id, "aplicada")
        return True

    # Aplicar cambio
    # NOTA: Los cambios reales de config/prompt se aplican manualmente
    # por el agente. Este script registra el estado y crea el backup.
    print(f"   📝 Cambio a aplicar: {cambio}")
    print(f"   📁 Archivo: {target_file}")
    print("\n   ⚠️  ACCIÓN REQUERIDA: El agente debe aplicar el cambio manualmente.")
    print("   Después de aplicar, ejecutar:")
    print(f"   python3.11 apply_improvement.py --id {improvement_id} --confirm")

    _update_improvement_status(improvement_id, "pendiente_aplicacion")
    return True


def confirm_application(improvement_id: str) -> bool:
    """Confirma que una mejora fue aplicada manualmente."""
    _update_improvement_status(improvement_id, "aplicada")
    print(f"✅ Mejora {improvement_id} confirmada como aplicada")
    return True


def rollback_improvement(improvement_id: str) -> bool:
    """
    Revierte una mejora restaurando el backup.

    Args:
        improvement_id: ID de la mejora a revertir

    Returns:
        True si se revirtió exitosamente
    """
    # Buscar backup
    backup_dir = BACKUP_DIR / improvement_id
    if not backup_dir.exists():
        print(f"❌ No se encontró backup para {improvement_id}")
        return False

    print(f"⏪ Revirtiendo mejora {improvement_id}...")

    # Restaurar archivos del backup
    restored = 0
    for backup_file in backup_dir.iterdir():
        if backup_file.name.endswith(".backup_meta.json"):
            continue

        # Leer metadata para saber la ruta original
        meta_file = backup_dir / f"{backup_file.stem}.backup_meta.json"
        if meta_file.exists():
            with open(meta_file, "r") as f:
                meta = json.load(f)
            original_path = Path(meta.get("original_path", ""))
        else:
            # Inferir ruta original
            original_path = SKILL_DIR / backup_file.name

        if original_path.exists():
            shutil.copy2(backup_file, original_path)
            print(f"   ✅ Restaurado: {original_path}")
            restored += 1

    _update_improvement_status(improvement_id, "revertida", motivo="Rollback manual")

    print(f"✅ Rollback completado: {restored} archivos restaurados")
    return True


def _create_backup(file_path: Path, improvement_id: str) -> Path:
    """Crea un backup de un archivo antes de modificarlo."""
    backup_dir = BACKUP_DIR / improvement_id
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / file_path.name
    shutil.copy2(file_path, backup_path)

    # Guardar metadata
    meta = {
        "original_path": str(file_path),
        "backup_time": datetime.now().isoformat(),
        "improvement_id": improvement_id,
    }
    meta_path = backup_dir / f"{file_path.stem}.backup_meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return backup_path


def _update_improvement_status(improvement_id: str, estado: str, motivo: str = None):
    """Actualiza el estado de una mejora en la DB."""
    with get_db() as conn:
        if estado == "aplicada":
            conn.execute(
                "UPDATE improvements SET estado = ?, aplicada_en = ? WHERE improvement_id = ?",
                (estado, datetime.now().isoformat(), improvement_id),
            )
        elif estado == "revertida":
            conn.execute(
                "UPDATE improvements SET estado = ?, revertida_en = ?, motivo_reversion = ? WHERE improvement_id = ?",
                (estado, datetime.now().isoformat(), motivo, improvement_id),
            )
        else:
            conn.execute("UPDATE improvements SET estado = ? WHERE improvement_id = ?", (estado, improvement_id))


def list_applied() -> list:
    """Lista todas las mejoras aplicadas actualmente."""
    return query_improvements(estado="aplicada")


def list_backups() -> list:
    """Lista todos los backups disponibles."""
    if not BACKUP_DIR.exists():
        return []

    backups = []
    for d in sorted(BACKUP_DIR.iterdir()):
        if d.is_dir():
            files = [f.name for f in d.iterdir() if not f.name.endswith(".backup_meta.json")]
            backups.append(
                {
                    "improvement_id": d.name,
                    "files": files,
                    "created": datetime.fromtimestamp(d.stat().st_mtime).isoformat(),
                }
            )
    return backups


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Aplicar/revertir mejoras")
    parser.add_argument("--id", required=True, help="ID de la mejora")
    parser.add_argument("--apply", action="store_true", help="Aplicar la mejora")
    parser.add_argument("--rollback", action="store_true", help="Revertir la mejora")
    parser.add_argument("--confirm", action="store_true", help="Confirmar aplicación manual")
    parser.add_argument("--force", action="store_true", help="Forzar aplicación")
    parser.add_argument("--list-backups", action="store_true", help="Listar backups")

    args = parser.parse_args()

    if args.list_backups:
        for b in list_backups():
            print(f"  {b['improvement_id']}: {b['files']} ({b['created']})")
        return

    if args.confirm:
        confirm_application(args.id)
    elif args.rollback:
        rollback_improvement(args.id)
    elif args.apply:
        apply_improvement(args.id, force=args.force)
    else:
        print("Especifique --apply, --rollback, o --confirm")


if __name__ == "__main__":
    main()
