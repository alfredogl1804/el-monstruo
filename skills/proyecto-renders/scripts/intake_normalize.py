#!/usr/bin/env python3.11
"""
Módulo 1: Intake & Normalización
Captura la información del terreno/ubicación desde múltiples fuentes
y genera un project_brief.yaml normalizado.

Fuentes soportadas:
- Coordenadas GPS
- Dirección textual
- Carpeta en Google Drive con renders/SketchUp
- Descripción libre del proyecto
- Archivos locales (imágenes, PDFs, planos)

Salida: project_brief.yaml con toda la información estructurada
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Agregar conector de sabios al path
sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio


async def extract_brief_from_description(description: str, context: dict = None) -> dict:
    """Usa GPT-5.4 para extraer un brief estructurado de una descripción libre."""

    context_str = ""
    if context:
        context_str = (
            f"\n\nContexto adicional proporcionado:\n{yaml.dump(context, default_flow_style=False, allow_unicode=True)}"
        )

    prompt = f"""Eres un analista inmobiliario experto. Extrae toda la información relevante de la siguiente descripción de proyecto y devuélvela como JSON estructurado.

DESCRIPCIÓN DEL PROYECTO:
{description}
{context_str}

Devuelve SOLO un JSON válido con esta estructura exacta (usa null para campos sin información):
{{
    "nombre_proyecto": "string",
    "ubicacion": {{
        "direccion": "string o null",
        "ciudad": "string o null",
        "estado": "string o null",
        "pais": "string o null",
        "coordenadas": {{
            "lat": "float o null",
            "lng": "float o null"
        }}
    }},
    "terreno": {{
        "area_m2_estimada": "float o null",
        "frente_ml": "float o null",
        "fondo_ml": "float o null",
        "forma": "string: regular/irregular/L/otro o null",
        "topografia": "string: plano/pendiente/mixto o null",
        "uso_actual": "string o null",
        "construcciones_existentes": "string o null"
    }},
    "contexto": {{
        "tipo_zona": "string: urbana/suburbana/periurbana/rural o null",
        "vialidades_principales": ["lista de strings"],
        "landmarks_cercanos": ["lista de strings"],
        "competencia_directa": ["lista de strings"],
        "infraestructura_relevante": ["lista de strings"]
    }},
    "proyecto": {{
        "objetivo": "string: descripción del objetivo del propietario",
        "restricciones": ["lista de restricciones conocidas"],
        "preferencias": ["lista de preferencias del cliente"],
        "presupuesto_estimado": "string o null",
        "timeline": "string o null",
        "publico_objetivo": "string o null"
    }},
    "activos_existentes": {{
        "tiene_renders": false,
        "tiene_planos": false,
        "tiene_sketchup": false,
        "tiene_estudio_mercado": false,
        "archivos_drive": "string: ruta o null",
        "archivos_locales": ["lista de paths"]
    }},
    "nivel_confianza": {{
        "ubicacion": "alto/medio/bajo",
        "terreno": "alto/medio/bajo",
        "contexto": "alto/medio/bajo",
        "proyecto": "alto/medio/bajo"
    }}
}}"""

    resultado = await consultar_sabio("gpt54", prompt)

    if resultado.get("status") == "ok":
        text = resultado["text"]
        # Extraer JSON del texto
        try:
            # Intentar encontrar JSON en la respuesta
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return {"error": "No se pudo extraer brief", "raw": resultado.get("text", "")}


async def scan_drive_folder(drive_path: str) -> dict:
    """Escanea una carpeta de Google Drive para encontrar activos del proyecto."""
    import subprocess

    assets = {"renders": [], "planos": [], "sketchup": [], "documentos": [], "imagenes": [], "otros": []}

    ext_map = {
        "renders": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
        "planos": [".dwg", ".dxf", ".pdf"],
        "sketchup": [".skp", ".skb"],
        "documentos": [".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".md"],
        "imagenes": [".webp", ".svg", ".gif"],
    }

    try:
        result = subprocess.run(["gws", "drive", "ls", drive_path], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                fname = line.strip().split()[-1] if line.strip() else ""
                ext = Path(fname).suffix.lower()
                categorized = False
                for cat, exts in ext_map.items():
                    if ext in exts:
                        assets[cat].append(fname)
                        categorized = True
                        break
                if not categorized and fname:
                    assets["otros"].append(fname)
    except Exception as e:
        assets["error"] = str(e)

    return assets


def geocode_address(address: str) -> dict:
    """Intenta geocodificar una dirección usando Nominatim (OpenStreetMap)."""
    import requests

    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": "ProyectoRenders/1.0"},
            timeout=10,
        )
        if resp.status_code == 200 and resp.json():
            data = resp.json()[0]
            return {
                "lat": float(data["lat"]),
                "lng": float(data["lon"]),
                "display_name": data.get("display_name", ""),
                "source": "nominatim",
                "confianza": "medio",
            }
    except Exception:
        pass

    return {"lat": None, "lng": None, "source": "no_disponible", "confianza": "bajo"}


async def run_intake(
    description: str,
    address: str = None,
    lat: float = None,
    lng: float = None,
    drive_folder: str = None,
    local_files: list = None,
    output_path: str = None,
) -> dict:
    """Ejecuta el pipeline completo de intake y genera project_brief.yaml."""

    print("=" * 60)
    print("📋 MÓDULO 1: INTAKE & NORMALIZACIÓN")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    # 1. Contexto adicional
    context = {}

    # 2. Geocodificación
    if lat and lng:
        context["coordenadas"] = {"lat": lat, "lng": lng, "source": "usuario", "confianza": "alto"}
        print(f"  📍 Coordenadas proporcionadas: {lat}, {lng}")
    elif address:
        print(f"  🔍 Geocodificando: {address}")
        geo = geocode_address(address)
        context["coordenadas"] = geo
        print(f"  📍 Resultado: {geo.get('lat')}, {geo.get('lng')} ({geo.get('confianza')})")

    # 3. Escanear Drive
    if drive_folder:
        print(f"  📂 Escaneando Google Drive: {drive_folder}")
        drive_assets = await scan_drive_folder(drive_folder)
        context["drive_assets"] = drive_assets
        total = sum(len(v) for v in drive_assets.values() if isinstance(v, list))
        print(f"  📁 {total} archivos encontrados en Drive")

    # 4. Archivos locales
    if local_files:
        context["local_files"] = local_files
        print(f"  📎 {len(local_files)} archivos locales proporcionados")

    # 5. Extraer brief con GPT-5.4
    print("  🤖 Extrayendo brief estructurado con GPT-5.4...")
    brief = await extract_brief_from_description(description, context)

    if "error" in brief:
        print(f"  ⚠️ Error en extracción: {brief['error']}")
        return brief

    # 6. Enriquecer con datos de geocodificación si no los tenía
    if context.get("coordenadas") and not brief.get("ubicacion", {}).get("coordenadas", {}).get("lat"):
        if brief.get("ubicacion"):
            brief["ubicacion"]["coordenadas"] = {
                "lat": context["coordenadas"].get("lat"),
                "lng": context["coordenadas"].get("lng"),
            }

    # 7. Agregar metadata
    brief["_metadata"] = {
        "fecha_intake": datetime.now().isoformat(),
        "version": "1.0",
        "fuentes": [],
        "skill": "proyecto-renders",
    }

    if description:
        brief["_metadata"]["fuentes"].append("descripcion_usuario")
    if address or (lat and lng):
        brief["_metadata"]["fuentes"].append("geocodificacion")
    if drive_folder:
        brief["_metadata"]["fuentes"].append("google_drive")
        brief["activos_existentes"] = brief.get("activos_existentes", {})
        brief["activos_existentes"]["archivos_drive"] = drive_folder
        brief["activos_existentes"]["drive_scan"] = context.get("drive_assets", {})
    if local_files:
        brief["_metadata"]["fuentes"].append("archivos_locales")

    # 8. Guardar
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(brief, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n✅ Project brief generado: {output_path}")
        print(f"📊 Campos completados: {count_filled(brief)}")

    return brief


def count_filled(d, prefix=""):
    """Cuenta campos llenos vs totales en un dict anidado."""
    total = 0
    filled = 0
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict):
            sub = count_filled(v, f"{prefix}{k}.")
            total += sub.split("/")[1] if "/" in sub else 0
            filled += sub.split("/")[0] if "/" in sub else 0
        elif isinstance(v, list):
            total += 1
            if v:
                filled += 1
        else:
            total += 1
            if v is not None:
                filled += 1
    return f"{filled}/{total}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo 1: Intake & Normalización")
    parser.add_argument("--description", required=True, help="Descripción del proyecto")
    parser.add_argument("--address", help="Dirección del terreno")
    parser.add_argument("--lat", type=float, help="Latitud")
    parser.add_argument("--lng", type=float, help="Longitud")
    parser.add_argument("--drive-folder", help="Ruta de carpeta en Google Drive")
    parser.add_argument("--local-files", nargs="+", help="Archivos locales")
    parser.add_argument("--output", required=True, help="Ruta de salida para project_brief.yaml")

    args = parser.parse_args()

    result = asyncio.run(
        run_intake(
            description=args.description,
            address=args.address,
            lat=args.lat,
            lng=args.lng,
            drive_folder=args.drive_folder,
            local_files=args.local_files,
            output_path=args.output,
        )
    )
