#!/usr/bin/env python3
"""
generate_visual_data.py — Generador automatizado de JSON visuales del Quantum Realm

Lee fuentes canónicas:
  - MONSTRUO_GENOME.yaml (estado arquitectónico)
  - kernel/catastro/data/*.json (candidatas)
  - kernel/, embriones/, scripts/, tools/, apps/ (código real para AST)

Emite:
  - client/public/genome_visual_data.json (o monstruo-quantum-realm/client/public/)
  - client/public/catastro_visual_data.json

Diseño:
  - Posiciones 3D distribuidas por distrito ontológico (mapeo Z→Distrito)
  - visual_scale, geometria.faces, irregularity calculados desde AST real
  - Edge bundling jerárquico vía agrupación por distrito
  - Escala logarítmica de área base para evitar efecto espagueti

Uso:
  python3 scripts/generate_visual_data.py [--output-dir PATH]

Autor: Hilo principal Manus (2026-05-23)
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
GENOME_YAML = REPO_ROOT / "MONSTRUO_GENOME.yaml"
CATASTRO_DIR = REPO_ROOT / "kernel" / "catastro" / "data"

# ─── Mapeo ontológico Z→Distrito ─────────────────────────────────────
# El sitio actual tiene 8 zonas. El otro hilo Manus pide 5 distritos
# ontológicos. Aquí definimos el mapeo canónico que el hilo Manus debe
# usar. Si Alfredo lo modifica, debe ser aquí, no en el código del sitio.
ZONE_TO_DISTRICT = {
    "Z1": ("D1", "COGNICIÓN"),  # CEREBRO → Cognición
    "Z2": ("D1", "COGNICIÓN"),  # MEMORIA → Cognición
    "Z3": ("D4", "CAPACIDADES"),  # AUTONOMÍA → Capacidades
    "Z4": ("D1", "COGNICIÓN"),  # INTELIGENCIA → Cognición
    "Z5": ("D2", "INTERFACES"),  # INTERFACES → Interfaces
    "Z6": ("D3", "INFRAESTRUCTURA"),  # SEGURIDAD → Infraestructura
    "Z7": ("D1", "COGNICIÓN"),  # CONOCIMIENTO → Cognición
    "Z8": ("D5", "FUTURO"),  # SATÉLITES → Futuro
}

DISTRICTS = [
    ("D1", "COGNICIÓN", {"x": 0, "y": 0, "z": 0}, 0xFFFFFF),
    ("D2", "INTERFACES", {"x": 12, "y": 0, "z": 0}, 0xCCCCCC),
    ("D3", "INFRAESTRUCTURA", {"x": -8, "y": 0, "z": 10}, 0xA3A3A3),
    ("D4", "CAPACIDADES", {"x": 8, "y": 0, "z": 10}, 0xB8B8B8),
    ("D5", "FUTURO", {"x": 0, "y": 0, "z": -14}, 0x888888),
]

# Carpetas que se escanean para nodos del genoma visual.
SCAN_DIRS = [
    "kernel",
    "scripts",
    "tools",
    "apps/la-forja/api/src",
    "apps/la-forja/web/app",
    "apps/mobile/lib",
    "tests",
    "migrations",
    "docs",
    "discovery_forense/CAPILLA_DECISIONES",
    "discovery_forense/SABIOS",
    "references",
]

# ─── AST helpers ─────────────────────────────────────────────────────


@dataclass
class FileMetrics:
    lines: int
    branches: int
    loops: int
    functions: int
    classes: int
    imports: int

    @property
    def complexity(self) -> int:
        return 1 + self.branches + self.loops + self.functions // 2


@dataclass
class Node:
    id: str
    zona: str
    distrito: str
    estado: str
    peso: int
    lineas: int
    archivos: int
    geometria: dict
    ast: dict
    visual_scale: float
    position: dict


def measure_python(path: Path) -> Optional[FileMetrics]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    branches = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.If, ast.IfExp, ast.Try)))
    loops = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While, ast.AsyncFor)))
    functions = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    imports = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)))
    lines = len(src.splitlines())
    return FileMetrics(
        lines=lines, branches=branches, loops=loops, functions=functions, classes=classes, imports=imports
    )


def measure_generic(path: Path) -> FileMetrics:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return FileMetrics(0, 0, 0, 0, 0, 0)
    lines = len(src.splitlines())
    # heurística simple para .ts/.js/.dart
    branches = len(re.findall(r"\bif\s*\(", src))
    loops = len(re.findall(r"\b(for|while)\s*\(", src))
    functions = len(re.findall(r"\bfunction\b|=>|\bdef\s+\w+", src))
    classes = len(re.findall(r"\bclass\s+\w+", src))
    imports = len(re.findall(r"^\s*(import|from)\s+", src, re.MULTILINE))
    return FileMetrics(
        lines=lines, branches=branches, loops=loops, functions=functions, classes=classes, imports=imports
    )


def measure_file(path: Path) -> FileMetrics:
    if path.suffix == ".py":
        m = measure_python(path)
        if m is not None:
            return m
    return measure_generic(path)


# ─── Mapeo de carpeta a zona ─────────────────────────────────────────


def folder_to_zone(rel_path: str) -> str:
    """Asigna zona ontológica al archivo basándose en su path.

    Orden de evaluación importante: las reglas más específicas van primero.
    Si modificás este mapeo, el sitio visual reorganiza los nodos automáticamente.
    """
    p = rel_path.lower()
    # Z6 SEGURIDAD (más específico que Z1 kernel)
    if "security" in p or "guardian" in p or "cosign" in p or "_check_" in p or "audit" in p or "pen_test" in p:
        return "Z6"
    # Z3 AUTONOMÍA — embriones, agentes, loops orquestadores
    if p.startswith("kernel/embriones") or "embrion" in p or "agent" in p or "orchestrator" in p or "loop" in p:
        return "Z3"
    # Z2 MEMORIA — SMS, sovereign, anchor, supabase
    if (
        p.startswith("kernel/memoria")
        or "memoria" in p
        or "/sms" in p
        or "sovereign" in p
        or "anchor" in p
        or "supabase" in p
    ):
        return "Z2"
    # Z4 INTELIGENCIA — modelos LLM, catastros, prompting, IA
    if (
        "llm" in p
        or "catastro" in p
        or "prompt" in p
        or "sabio" in p
        or "models" in p
        or "openrouter" in p
        or "anthropic" in p
        or "gemini" in p
    ):
        return "Z4"
    # Z5 INTERFACES — apps, mobile, web, bot, transports
    if (
        p.startswith("apps/")
        or p.startswith("web/")
        or p.startswith("client/")
        or "transport" in p
        or "telegram" in p
        or "whatsapp" in p
        or "discord" in p
        or "bridge" in p
    ):
        return "Z5"
    # Z7 CONOCIMIENTO — docs, skills, referencias, doctrina
    if (
        p.startswith("docs/")
        or "skills/" in p
        or p.startswith("references/")
        or p.startswith("discovery_forense/")
        or "doctrine" in p
        or "canon" in p
        or "semilla" in p
    ):
        return "Z7"
    # Z8 SATÉLITES — proyectos externos integrados
    if "satellite" in p or "ticketlike" in p or "like-kukulkan" in p or "el-mundo-de-tata" in p:
        return "Z8"
    # Z3 AUTONOMÍA — migraciones, scripts, tools (acciones autónomas)
    if p.startswith("migrations/") or p.startswith("tools/") or p.startswith("scripts/"):
        return "Z3"
    # Z1 CEREBRO — kernel core (default)
    if p.startswith("kernel/"):
        return "Z1"
    return "Z1"


def detect_state(rel_path: str, lines: int) -> str:
    if lines == 0:
        return "ASPIRANTE"
    return "ACTIVO"


# ─── Posicionamiento 3D ──────────────────────────────────────────────


def fibonacci_sphere_offset(idx: int, n: int, radius: float) -> dict:
    """Distribución casi-uniforme alrededor de un centro."""
    phi = math.pi * (3.0 - math.sqrt(5.0))
    y = 1 - (idx / max(n - 1, 1)) * 2
    r = math.sqrt(max(1 - y * y, 0))
    theta = phi * idx
    x = math.cos(theta) * r
    z = math.sin(theta) * r
    return {"x": x * radius, "y": y * radius * 0.5, "z": z * radius}


def calc_visual_scale(lines: int) -> float:
    """Escala logarítmica para evitar nodos gigantes."""
    if lines <= 1:
        return 0.2
    scaled = math.log10(max(lines, 1) + 1) / 3.0  # log10(10000) = 4 → /3 ≈ 1.33
    return round(0.2 + min(scaled, 1.5), 3)


def calc_faces(complexity: int) -> int:
    """Más complejidad → más caras geométricas."""
    return 60 + min(complexity * 4, 240)


def calc_irregularity(metrics: FileMetrics) -> float:
    """Irregularidad refleja branching + loops."""
    raw = (metrics.branches + metrics.loops * 2) / max(metrics.lines, 1)
    return round(min(raw, 1.0), 3)


# ─── Scan principal ──────────────────────────────────────────────────


def scan_directory(root: Path, rel_dir: str) -> dict[str, FileMetrics]:
    """Devuelve {id_modulo: FileMetrics agregadas}."""
    aggregated: dict[str, FileMetrics] = {}
    full = root / rel_dir
    if not full.exists():
        return aggregated
    for path in full.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".sql"}:
            continue
        if "node_modules" in str(path) or ".git" in str(path):
            continue
        # ID = path relativo sin extension
        path.relative_to(root)
        module_id = path.stem  # nombre del archivo sin extension
        if module_id == "__init__":
            module_id = path.parent.name + "_init"
        # acumulamos
        m = measure_file(path)
        if module_id in aggregated:
            existing = aggregated[module_id]
            aggregated[module_id] = FileMetrics(
                lines=existing.lines + m.lines,
                branches=existing.branches + m.branches,
                loops=existing.loops + m.loops,
                functions=existing.functions + m.functions,
                classes=existing.classes + m.classes,
                imports=existing.imports + m.imports,
            )
        else:
            aggregated[module_id] = m
    return aggregated


# ─── Genoma visual ───────────────────────────────────────────────────


def build_genome_visual(root: Path, target_nodes: int = 120) -> dict:
    all_nodes: list[Node] = []
    file_records: list[tuple[str, str, FileMetrics]] = []  # (module_id, rel_path, metrics)

    # Patrones a excluir: dumps de memoria, exports JSON, fixtures masivos
    SKIP_PATTERNS = [
        "_export_",
        "_dump_",
        "_snapshot_",
        "_fixture_",
        "_seed_data",
        ".min.",
        "package-lock",
        "yarn.lock",
    ]

    for d in SCAN_DIRS:
        full = root / d
        if not full.exists():
            continue
        for path in full.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".ts", ".tsx", ".dart", ".sql", ".md"}:
                continue
            if "node_modules" in str(path) or ".git" in str(path):
                continue
            rel = str(path.relative_to(root))
            if any(skip in rel for skip in SKIP_PATTERNS):
                continue
            # Cap duro: archivos > 10k líneas son dumps generados, no código
            m = measure_file(path)
            if m.lines < 5 or m.lines > 10000:
                continue
            module_id = path.stem
            if module_id in ("__init__", "index", "README"):
                module_id = path.parent.name + "_" + module_id
            file_records.append((module_id, rel, m))

    # ordenamos por líneas desc y tomamos los top (target_nodes - satellites)
    file_records.sort(key=lambda r: r[2].lines, reverse=True)

    # Inyectar satélites del genoma como nodos Z8 sintéticos (siempre incluidos)
    satellite_records: list[tuple[str, str, FileMetrics]] = []
    try:
        genome = yaml.safe_load((root / "MONSTRUO_GENOME.yaml").read_text())
        for sat in genome.get("satellites", []):
            sat_id = sat.get("id", "unknown")
            satellite_records.append(
                (
                    sat_id,
                    f"satellites/{sat_id}",
                    FileMetrics(lines=200, branches=10, loops=2, functions=10, classes=5, imports=5),
                )
            )
    except Exception as e:
        print(f"[gen] warn: no se pudo leer satellites del genome: {e}")

    # Reservamos slots para satellites + completamos con archivos
    remaining_slots = target_nodes - len(satellite_records)
    file_records = file_records[:remaining_slots] + satellite_records

    # agrupamos por distrito para distribuir 3D
    by_district: dict[str, list[tuple[str, str, FileMetrics]]] = {d[0]: [] for d in DISTRICTS}
    for module_id, rel_path, metrics in file_records:
        zona = folder_to_zone(rel_path)
        distrito_id, _ = ZONE_TO_DISTRICT.get(zona, ("D1", "COGNICIÓN"))
        by_district[distrito_id].append((module_id, rel_path, metrics))

    # construimos nodos con posición 3D por distrito
    district_centers = {d[0]: d[2] for d in DISTRICTS}
    for distrito_id, items in by_district.items():
        center = district_centers[distrito_id]
        for idx, (module_id, rel_path, metrics) in enumerate(items):
            zona = folder_to_zone(rel_path)
            distrito_id_final, distrito_name = ZONE_TO_DISTRICT.get(zona, ("D1", "COGNICIÓN"))
            offset = fibonacci_sphere_offset(idx, len(items), radius=4.0)
            position = {
                "x": round(center["x"] + offset["x"], 3),
                "y": round(center["y"] + offset["y"], 3),
                "z": round(center["z"] + offset["z"], 3),
            }
            node = Node(
                id=module_id,
                zona=zona,
                distrito=distrito_id_final,
                estado=detect_state(rel_path, metrics.lines),
                peso=metrics.lines,
                lineas=metrics.lines,
                archivos=1,
                geometria={
                    "faces": calc_faces(metrics.complexity),
                    "irregularity": calc_irregularity(metrics),
                    "is_cluster": False,
                    "cluster_count": 1,
                    "elongation": round(1.0 + min(metrics.classes * 0.1, 0.5), 2),
                },
                ast={
                    "branches": metrics.branches,
                    "loops": metrics.loops,
                    "functions": metrics.functions,
                    "imports": metrics.imports,
                    "classes": metrics.classes,
                    "complexity": metrics.complexity,
                },
                visual_scale=calc_visual_scale(metrics.lines),
                position=position,
            )
            all_nodes.append(node)

    # zonas del genoma (mantenemos compat con sitio actual + agregamos distritos)
    zones_legacy = [
        {"id": "Z1", "name": "CEREBRO", "radius": 0, "distrito": "D1"},
        {"id": "Z2", "name": "MEMORIA", "radius": 3, "distrito": "D1"},
        {"id": "Z3", "name": "AUTONOMÍA", "radius": 5, "distrito": "D4"},
        {"id": "Z4", "name": "INTELIGENCIA", "radius": 7, "distrito": "D1"},
        {"id": "Z5", "name": "INTERFACES", "radius": 9, "distrito": "D2"},
        {"id": "Z6", "name": "SEGURIDAD", "radius": 11, "distrito": "D3"},
        {"id": "Z7", "name": "CONOCIMIENTO", "radius": 13, "distrito": "D1"},
        {"id": "Z8", "name": "SATÉLITES", "radius": 17, "distrito": "D5"},
    ]

    districts_out = [{"id": d[0], "name": d[1], "center": d[2], "color_hex": f"0x{d[3]:06x}"} for d in DISTRICTS]

    heaviest = max(all_nodes, key=lambda n: n.lineas).id if all_nodes else "none"

    return {
        "meta": {
            "generated_at_utc": _now_iso(),
            "version": "3.0",
            "generator": "scripts/generate_visual_data.py",
            "total_nodes": len(all_nodes),
            "total_zones": len(zones_legacy),
            "total_districts": len(districts_out),
            "heaviest": heaviest,
            "source": "MONSTRUO_GENOME.yaml + filesystem AST",
        },
        "districts": districts_out,
        "zones": zones_legacy,
        "nodes": [asdict(n) for n in all_nodes],
    }


# ─── Catastro visual ─────────────────────────────────────────────────


def build_catastro_visual(root: Path) -> dict:
    """Genera catastro_visual_data.json desde kernel/catastro/data/*.json.

    Si los catastros del repo son insuficientes (hoy 2 entries cada uno),
    preservamos el catastro actual del sitio para no perder Nano Banana Pro
    ni las 120 candidatas. Devolvemos None si NO podemos generar uno mejor.
    """
    catastro_files = list((root / "kernel" / "catastro" / "data").glob("*.json"))
    candidatas_raw = []
    for f in catastro_files:
        try:
            data = json.loads(f.read_text())
            if isinstance(data, list):
                candidatas_raw.extend(data)
            elif isinstance(data, dict) and "candidatas" in data:
                candidatas_raw.extend(data["candidatas"])
        except Exception:
            continue

    if len(candidatas_raw) < 50:
        # Insuficiente — devolvemos None para que el caller preserve el manual
        return None

    # TODO Fase 4: cuando los catastros del repo crezcan a 120+, mapeamos
    # aquí con posición orbital, familia, tier, operable, etc.
    raise NotImplementedError("Catastro generator pendiente — requiere catastros canónicos completos.")


# ─── IO helpers ──────────────────────────────────────────────────────


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/home/ubuntu/monstruo-quantum-realm/client/public"),
        help="Directorio destino para los JSON visuales",
    )
    parser.add_argument(
        "--target-nodes",
        type=int,
        default=120,
        help="Cantidad objetivo de nodos en el genoma visual",
    )
    parser.add_argument(
        "--preserve-catastro",
        action="store_true",
        default=True,
        help="Preservar catastro manual si los catastros del repo son insuficientes",
    )
    args = parser.parse_args()

    print(f"[gen] root={REPO_ROOT}")
    print(f"[gen] output={args.output_dir}")
    print(f"[gen] target_nodes={args.target_nodes}")

    # Genoma visual
    genome_visual = build_genome_visual(REPO_ROOT, target_nodes=args.target_nodes)
    write_json(args.output_dir / "genome_visual_data.json", genome_visual)
    print(
        f"[gen] genome_visual_data.json escrito · {genome_visual['meta']['total_nodes']} nodos · {genome_visual['meta']['total_districts']} distritos"
    )

    # Catastro visual
    try:
        catastro_visual = build_catastro_visual(REPO_ROOT)
    except NotImplementedError as e:
        catastro_visual = None
        print(f"[gen] catastro: {e}")
    if catastro_visual is None:
        if args.preserve_catastro:
            print(f"[gen] catastro: PRESERVANDO manual ({args.output_dir / 'catastro_visual_data.json'})")
        else:
            print("[gen] catastro: omitido")
    else:
        write_json(args.output_dir / "catastro_visual_data.json", catastro_visual)
        print("[gen] catastro_visual_data.json escrito")

    print("[gen] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
