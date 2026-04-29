#!/usr/bin/env python3.11
"""
DRIVE_SCANNER.py — Herramienta de planificación
Escanea Google Drive REAL usando gws CLI para catalogar y descargar
assets del estadio Kukulcán, mascotas y patrocinadores.
Conexión REAL a Google Drive. Cero simulaciones.
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from colorama import init, Fore, Style

init(autoreset=True)

class DriveScanner:
    def __init__(self):
        self.gws_available = self._check_gws()
        if not self.gws_available:
            print(f"{Fore.RED}❌ BLOQUEADO: gws CLI no está instalado o no responde.{Style.RESET_ALL}")
            print(f"{Fore.RED}   Sin gws no hay acceso a Drive. No se puede planificar sin assets reales.{Style.RESET_ALL}")
            sys.exit(1)

    def _check_gws(self):
        """Verifica que gws CLI está instalado y responde."""
        try:
            result = subprocess.run(
                ["gws", "--help"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _gws_search(self, query, page_size=50):
        """Ejecuta búsqueda real en Google Drive via gws CLI."""
        # La API de Drive requiere el formato: name contains 'termino'
        # Si el query ya tiene formato de Drive API, usarlo tal cual
        if "contains" in query or "=" in query:
            drive_query = query
        else:
            drive_query = f"name contains '{query}'"
        
        params = json.dumps({
            "pageSize": page_size,
            "q": drive_query,
            "fields": "files(id,name,mimeType,size,modifiedTime,parents),nextPageToken"
        })
        
        print(f"{Fore.CYAN}  🔍 gws drive files list --q \"{drive_query}\"{Style.RESET_ALL}")
        
        try:
            result = subprocess.run(
                ["gws", "drive", "files", "list", "--params", params],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=30, text=True
            )
            
            if result.returncode != 0:
                print(f"{Fore.RED}  ❌ Error en búsqueda: {result.stderr.strip()}{Style.RESET_ALL}")
                return []
            
            data = json.loads(result.stdout)
            files = data.get("files", [])
            print(f"{Fore.GREEN}  ✅ Encontrados {len(files)} archivos{Style.RESET_ALL}")
            return files
            
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}  ❌ Timeout en búsqueda de Drive{Style.RESET_ALL}")
            return []
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}  ❌ Error parseando respuesta: {e}{Style.RESET_ALL}")
            return []

    def _gws_download(self, file_id, file_name, output_dir):
        """Descarga un archivo real de Google Drive via gws CLI."""
        # gws requiere que --output sea relativa al directorio actual
        original_dir = os.getcwd()
        os.chdir(output_dir)
        
        try:
            params = json.dumps({
                "fileId": file_id,
                "alt": "media"
            })
            
            result = subprocess.run(
                ["gws", "drive", "files", "get", "--params", params, "--output", file_name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=120, text=True
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                full_path = os.path.join(output_dir, file_name)
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    print(f"{Fore.GREEN}  ⬇️ {file_name} ({size:,} bytes){Style.RESET_ALL}")
                    return full_path
                else:
                    print(f"{Fore.YELLOW}  ⚠️ Comando exitoso pero archivo no encontrado: {file_name}{Style.RESET_ALL}")
                    return None
            else:
                print(f"{Fore.RED}  ❌ Error descargando {file_name}: {result.stderr.strip()}{Style.RESET_ALL}")
                return None
                
        except subprocess.TimeoutExpired:
            os.chdir(original_dir)
            print(f"{Fore.RED}  ❌ Timeout descargando {file_name}{Style.RESET_ALL}")
            return None
        except Exception as e:
            os.chdir(original_dir)
            print(f"{Fore.RED}  ❌ Error inesperado: {e}{Style.RESET_ALL}")
            return None

    def escanear_assets(self, queries, output_dir, descargar_imagenes=True, descargar_videos=False):
        """
        Escanea Google Drive con múltiples queries y cataloga los resultados.
        
        Args:
            queries: Lista de strings de búsqueda
            output_dir: Directorio donde guardar catálogo y descargas
            descargar_imagenes: Si True, descarga automáticamente las imágenes encontradas
            descargar_videos: Si True, descarga también los videos (pueden ser pesados)
        """
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}  ESCÁNER DE GOOGLE DRIVE (CONEXIÓN REAL){Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        os.makedirs(output_dir, exist_ok=True)
        download_dir = os.path.join(output_dir, "descargas")
        os.makedirs(download_dir, exist_ok=True)
        
        # ── FASE 1: Búsqueda múltiple ──
        todos_los_archivos = {}  # Deduplicar por ID
        
        for query in queries:
            print(f"\n{Fore.WHITE}📂 Buscando: \"{query}\"{Style.RESET_ALL}")
            archivos = self._gws_search(query)
            for f in archivos:
                todos_los_archivos[f["id"]] = f
        
        archivos_unicos = list(todos_los_archivos.values())
        
        print(f"\n{Fore.WHITE}{'─'*40}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total archivos únicos encontrados: {len(archivos_unicos)}{Style.RESET_ALL}")
        
        if len(archivos_unicos) == 0:
            print(f"{Fore.RED}❌ BLOQUEADO: No se encontraron assets en Drive.{Style.RESET_ALL}")
            print(f"{Fore.RED}   No se puede planificar sin referencias visuales reales.{Style.RESET_ALL}")
            return None
        
        # ── FASE 2: Clasificar por tipo ──
        clasificacion = {
            "imagenes": [],
            "videos": [],
            "modelos_3d": [],
            "documentos": [],
            "otros": []
        }
        
        for f in archivos_unicos:
            mime = f.get("mimeType", "")
            if "image" in mime:
                clasificacion["imagenes"].append(f)
            elif "video" in mime:
                clasificacion["videos"].append(f)
            elif any(ext in f.get("name", "").lower() for ext in [".skp", ".obj", ".fbx", ".3ds", ".blend"]):
                clasificacion["modelos_3d"].append(f)
            elif any(ext in mime for ext in ["pdf", "document", "spreadsheet", "presentation"]):
                clasificacion["documentos"].append(f)
            else:
                clasificacion["otros"].append(f)
        
        print(f"\n{Fore.CYAN}📊 Clasificación:{Style.RESET_ALL}")
        for cat, items in clasificacion.items():
            if items:
                print(f"   {cat}: {len(items)} archivos")
                for item in items[:5]:  # Mostrar máximo 5 por categoría
                    print(f"     • {item['name']} ({item.get('mimeType', 'unknown')})")
                if len(items) > 5:
                    print(f"     ... y {len(items) - 5} más")
        
        # ── FASE 3: Descargar assets de referencia ──
        archivos_descargados = []
        
        if descargar_imagenes and clasificacion["imagenes"]:
            print(f"\n{Fore.WHITE}⬇️ Descargando {len(clasificacion['imagenes'])} imágenes de referencia...{Style.RESET_ALL}")
            for img in clasificacion["imagenes"]:
                path = self._gws_download(img["id"], img["name"], download_dir)
                if path:
                    archivos_descargados.append({
                        "id": img["id"],
                        "name": img["name"],
                        "local_path": path,
                        "type": "imagen"
                    })
        
        if descargar_videos and clasificacion["videos"]:
            print(f"\n{Fore.WHITE}⬇️ Descargando {len(clasificacion['videos'])} videos de referencia...{Style.RESET_ALL}")
            for vid in clasificacion["videos"]:
                path = self._gws_download(vid["id"], vid["name"], download_dir)
                if path:
                    archivos_descargados.append({
                        "id": vid["id"],
                        "name": vid["name"],
                        "local_path": path,
                        "type": "video"
                    })
        
        # ── FASE 4: Generar catálogo ──
        catalogo = {
            "fecha_escaneo": subprocess.run(
                ["date", "-Iseconds"], stdout=subprocess.PIPE, text=True
            ).stdout.strip(),
            "queries_usadas": queries,
            "total_archivos_encontrados": len(archivos_unicos),
            "clasificacion": {k: len(v) for k, v in clasificacion.items()},
            "archivos": archivos_unicos,
            "archivos_descargados": archivos_descargados,
            "directorio_descargas": download_dir
        }
        
        catalogo_file = os.path.join(output_dir, "catalogo_drive_real.json")
        with open(catalogo_file, 'w', encoding='utf-8') as f:
            json.dump(catalogo, f, indent=2, ensure_ascii=False)
        
        # ── FASE 5: Generar resumen legible ──
        resumen_file = os.path.join(output_dir, "RESUMEN_ASSETS_DRIVE.md")
        with open(resumen_file, 'w', encoding='utf-8') as f:
            f.write("# Inventario de Assets en Google Drive\n\n")
            f.write(f"**Fecha de escaneo:** {catalogo['fecha_escaneo']}\n\n")
            f.write(f"**Queries usadas:** {', '.join(queries)}\n\n")
            f.write(f"**Total de archivos únicos:** {len(archivos_unicos)}\n\n")
            
            f.write("## Clasificación\n\n")
            f.write("| Categoría | Cantidad |\n")
            f.write("|-----------|----------|\n")
            for cat, items in clasificacion.items():
                f.write(f"| {cat.replace('_', ' ').title()} | {len(items)} |\n")
            
            f.write("\n## Archivos Descargados para Referencia\n\n")
            if archivos_descargados:
                for ad in archivos_descargados:
                    f.write(f"- **{ad['name']}** → `{ad['local_path']}`\n")
            else:
                f.write("_Ninguno descargado en esta ejecución._\n")
            
            f.write("\n## Inventario Completo\n\n")
            for cat, items in clasificacion.items():
                if items:
                    f.write(f"\n### {cat.replace('_', ' ').title()}\n\n")
                    for item in items:
                        size_str = f" ({int(item.get('size', 0)):,} bytes)" if item.get('size') else ""
                        f.write(f"- `{item['name']}`{size_str} — ID: `{item['id']}`\n")
        
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Escaneo completado:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Catálogo JSON: {catalogo_file}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Resumen MD:    {resumen_file}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Descargados:   {len(archivos_descargados)} archivos en {download_dir}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        
        return catalogo_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Escanea Google Drive para catalogar assets de planificación"
    )
    parser.add_argument(
        "--queries", nargs="+", required=True,
        help="Una o más queries de búsqueda (ej: 'kukulkan' 'leones mascota' 'zona like')"
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directorio de salida para catálogo y descargas"
    )
    parser.add_argument(
        "--descargar-imagenes", action="store_true", default=True,
        help="Descargar automáticamente las imágenes encontradas"
    )
    parser.add_argument(
        "--descargar-videos", action="store_true", default=False,
        help="Descargar también los videos (pueden ser pesados)"
    )
    args = parser.parse_args()
    
    scanner = DriveScanner()
    scanner.escanear_assets(
        args.queries,
        args.output_dir,
        descargar_imagenes=args.descargar_imagenes,
        descargar_videos=args.descargar_videos
    )
