#!/usr/bin/env python3.11
"""
sync_notion.py — Sincroniza el inventario de APIs desde Notion DB.

Consulta la base de datos "API Keys y Credenciales" en Notion
y genera un snapshot actualizado en data/snapshots/.

Uso:
    python3.11 sync_notion.py [--output-dir data/snapshots/]

NOTA: Este script NO almacena API keys en archivos.
Solo almacena metadata (servicio, categoría, estado, tipo, notas).
"""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

NOTION_DB_DATASOURCE = "collection://d94369d5-5dc3-437e-b483-fa86a5e98b74"
NOTION_DB_ID = "54b9d97704bc408d8453c1524fbfec9b"

# Campos seguros para almacenar (NUNCA API Key, Password, Usuario)
SAFE_FIELDS = ["Servicio", "Categoria", "Estado", "Tipo", "Notas", "userDefined:URL"]
REDACTED_FIELDS = ["API Key", "Password", "Usuario"]


def run_mcp_command(tool_name: str, server: str, input_json: dict) -> dict:
    """Ejecuta un comando MCP y retorna el resultado parseado."""
    cmd = ["manus-mcp-cli", "tool", "call", tool_name, "--server", server, "--input", json.dumps(input_json)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            # Intentar parsear JSON del output
            output = result.stdout.strip()
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"raw": output}
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"}
    except Exception as e:
        return {"error": str(e)}


def search_all_entries() -> list:
    """Busca todas las entradas en la DB de API Keys."""
    result = run_mcp_command(
        "notion-search",
        "notion",
        {"query": "", "data_source_url": NOTION_DB_DATASOURCE, "page_size": 100, "filters": {}},
    )

    entries = []
    if "results" in result:
        for item in result["results"]:
            entries.append({"id": item.get("id", ""), "title": item.get("title", ""), "url": item.get("url", "")})

    return entries


def fetch_entry_metadata(entry_id: str) -> dict:
    """Obtiene metadata segura de una entrada (sin credenciales)."""
    result = run_mcp_command("notion-fetch", "notion", {"id": entry_id})

    metadata = {"id": entry_id}

    text = result.get("text", "")
    if text:
        # Extraer propiedades del texto
        try:
            # Buscar el JSON de propiedades
            import re

            props_match = re.search(r'"properties">\s*({[^}]+})', text)
            if props_match:
                props = json.loads(props_match.group(1))

                # Solo copiar campos seguros
                for field in SAFE_FIELDS:
                    if field in props:
                        metadata[field] = props[field]

                # Marcar campos redactados
                for field in REDACTED_FIELDS:
                    if field in props and props[field]:
                        metadata[f"{field}_present"] = True
                    else:
                        metadata[f"{field}_present"] = False
        except (json.JSONDecodeError, AttributeError):
            pass

    metadata["title"] = result.get("title", "")
    metadata["url"] = result.get("url", "")

    return metadata


def generate_snapshot(entries: list, output_dir: Path):
    """Genera un snapshot del inventario."""
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "source": "Notion DB: API Keys y Credenciales",
        "db_id": NOTION_DB_ID,
        "total_entries": len(entries),
        "entries": entries,
        "categories": {},
        "status_summary": {"Activo": 0, "Inactivo": 0, "Desconocido": 0},
    }

    for entry in entries:
        cat = entry.get("Categoria", "Sin categoría")
        if cat not in snapshot["categories"]:
            snapshot["categories"][cat] = []
        snapshot["categories"][cat].append(entry.get("title", entry.get("Servicio", "?")))

        status = entry.get("Estado", "Desconocido")
        if status in snapshot["status_summary"]:
            snapshot["status_summary"][status] += 1
        else:
            snapshot["status_summary"]["Desconocido"] += 1

    output_dir.mkdir(parents=True, exist_ok=True)

    # Guardar snapshot JSON
    snapshot_file = output_dir / f"notion-snapshot-{datetime.now().strftime('%Y%m%d')}.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    # Guardar latest
    latest_file = output_dir / "notion-snapshot-latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    return snapshot_file


def main():
    parser = argparse.ArgumentParser(description="Sincroniza inventario desde Notion")
    parser.add_argument("--output-dir", default="data/snapshots/", help="Directorio de salida")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / args.output_dir

    print("🔄 Sincronizando desde Notion DB...")
    print(f"   DB: {NOTION_DB_ID}")

    # Buscar todas las entradas
    print("   Buscando entradas...")
    entries = search_all_entries()
    print(f"   Encontradas: {len(entries)}")

    # Obtener metadata de cada entrada
    enriched = []
    for i, entry in enumerate(entries):
        print(f"   [{i + 1}/{len(entries)}] {entry.get('title', '?')}...")
        metadata = fetch_entry_metadata(entry["id"])
        metadata.update(entry)
        enriched.append(metadata)

    # Generar snapshot
    snapshot_file = generate_snapshot(enriched, output_dir)

    print(f"\n✅ Snapshot generado: {snapshot_file}")
    print(f"   Total entradas: {len(enriched)}")


if __name__ == "__main__":
    main()
