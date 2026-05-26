#!/usr/bin/env python3
"""
Sprint 91.16 — Migración one-shot a Sprint Registry único.

Lee 4 fuentes:
  1. bridge/sprints_propuestos/sprint_*.md (archivos)
  2. bridge/sprints_completados/sprint_*.md (archivos)
  3. interfaces_context_fabric/maps/SPRINT_REGISTRY.yaml (rama interfaces-context-fabric-001)
  4. tablero-campana/scripts/build_board_data.py _FALLBACK_BACKLOG_SPRINTS

Normaliza, deduplica por similitud, y produce sprints/registry.yaml + migration_conflicts.md.

Uso:
    python3 migrate_to_sprint_registry.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# ---------- Rutas ----------
# Autodetect: si corremos desde el Mac (~/el-monstruo) usar local; si desde sandbox usar mount
_LOCAL_REPO = Path.home() / "el-monstruo"
_MOUNT_REPO = Path("/mnt/desktop/el-monstruo")
if _LOCAL_REPO.exists() and (_LOCAL_REPO / ".git").exists():
    REPO = _LOCAL_REPO
elif _MOUNT_REPO.exists():
    REPO = _MOUNT_REPO
else:
    REPO = _LOCAL_REPO  # default
PROPUESTOS_DIR = REPO / "bridge" / "sprints_propuestos"
COMPLETADOS_DIR = REPO / "bridge" / "sprints_completados"
REGISTRY_OUT = REPO / "sprints" / "registry.yaml"
CONFLICTS_OUT = REPO / "sprints" / "migration_conflicts.md"

# ---------- Helpers de normalización ----------
ID_NORMALIZE_RE = re.compile(r"[^A-Z0-9_]")

def normalize_id(raw: str) -> str:
    """SCREAMING_SNAKE_CASE canónico."""
    s = raw.strip().upper().replace("-", "_").replace(" ", "_")
    # Eliminar prefijos comunes
    for pref in ("SPRINT_", "SPEC_"):
        if s.startswith(pref):
            s = s[len(pref):]
    # Eliminar sufijos de fase (mismo sprint, archivo distinto)
    for suf in ("_KICKOFF", "_CIERRE", "_FIRMADO", "_DRAFT", "_V1", "_V2", "_V3", "_V3_1"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    s = ID_NORMALIZE_RE.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

# ---------- Dataclass ----------
@dataclass
class SprintEntry:
    id: str
    title: str = ""
    status: str = "PROPOSED"
    paradigm: str = "transversal"
    objetivos_maestros: list[int] = field(default_factory=list)
    capas_transversales: list[str] = field(default_factory=list)
    priority: str = "BACKLOG"
    eta_days: int | None = None
    owner: str = ""
    path: str | None = None
    pr_merged: int | None = None
    completed_at: str | None = None
    bloquea_a: list[str] = field(default_factory=list)
    bloqueado_por: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    notes: str = ""
    sources: list[str] = field(default_factory=list)  # debug: de qué fuente vino

# ---------- Parsers ----------
def parse_md_file(md: Path, status_default: str) -> SprintEntry | None:
    try:
        text = md.read_text(encoding="utf-8")
    except Exception:
        return None

    # Patterns variados de header
    title_patterns = [
        r"^#\s+(?:Sprint|SPEC)\s+([A-Z0-9_\-\.]+)\s*—\s*(.+)$",
        r"^#[^A-Za-z\n]*?(?:Sprint|SPEC)\s+([A-Z0-9_\-\.]+)\s*—\s*(.+)$",
        r"^#\s+(?:Sprint|SPEC)\s+([A-Z0-9_\-\.]+)\s*$",
        r"\*\*Sprint:\*\*\s*`?([A-Z0-9_\-\.]+)`?",
    ]
    raw_id = ""
    title = ""
    for pat in title_patterns:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            raw_id = m.group(1).strip()
            title = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else raw_id
            break

    # Fallback: del filename
    if not raw_id:
        stem = md.stem
        if stem.startswith("sprint_"):
            stem = stem[len("sprint_"):]
        for cut in ("_FIRMADO", "_cierre", "_KICKOFF"):
            if cut in stem:
                stem = stem.split(cut)[0]
                break
        raw_id = stem
        title = stem.replace("_", " ").title()

    sprint_id = normalize_id(raw_id)
    if not sprint_id:
        return None

    # Estado
    estado_match = re.search(r"\*\*Estado:\*\*\s*(.+?)(?:\n|$)", text)
    estado_raw = estado_match.group(1).strip() if estado_match else ""
    estado_lower = estado_raw.lower()

    if status_default == "COMPLETED":
        status = "COMPLETED"
    elif "completado" in estado_lower or "declarado" in estado_lower or "verde" in estado_lower:
        status = "COMPLETED"
    elif "en curso" in estado_lower or "ejecuc" in estado_lower or "in progress" in estado_lower:
        status = "IN_PROGRESS"
    elif "bloqueado" in estado_lower or "blocked" in estado_lower:
        status = "BLOCKED"
    elif "firmado" in estado_lower or "signed" in estado_lower or "aspiracional" in estado_lower:
        status = "SIGNED"
    else:
        status = "PROPOSED"

    # OM
    om_match = re.search(r"\*\*Objetivo Maestro:\*\*\s*(.+?)(?:\n|$)", text)
    objetivos: list[int] = []
    if om_match:
        for n in re.findall(r"#?(\d{1,2})", om_match.group(1)):
            try:
                ni = int(n)
                if 1 <= ni <= 15:
                    objetivos.append(ni)
            except ValueError:
                pass

    # Capa
    capas: list[str] = []
    capa_match = re.search(r"\*\*Capa Transversal:\*\*\s*(.+?)(?:\n|$)", text)
    if capa_match:
        for c in re.findall(r"C\d", capa_match.group(1)):
            capas.append(c)

    # Paradigm heurístico
    paradigm = "transversal"
    if sprint_id.startswith("CAPA_"):
        paradigm = "capa_transversal_comercial"
    elif sprint_id.startswith("STACK_") or "vanguardia_perpetua" in text.lower():
        paradigm = "vanguardia_perpetua"
    elif "calm tech" in text.lower() or "ambient" in text.lower() or sprint_id.startswith("LISTENING_") or sprint_id.startswith("WHATSAPP_") or sprint_id.startswith("VOICE_") or sprint_id.startswith("MODO_CONFIDENTE") or sprint_id.startswith("CAPABILITY_"):
        paradigm = "acto_2_calm_tech"
    elif sprint_id.startswith("DAILY_") or sprint_id.startswith("COCKPIT_") or sprint_id.startswith("TOGGLE_") or sprint_id.startswith("PORTFOLIO_"):
        paradigm = "acto_1_pantallas"
    elif sprint_id.startswith("MOBILE_") and "COCKPIT" in sprint_id:
        paradigm = "obsoleto_pendiente_decision"

    # PR mergeado (si está en el texto)
    pr_match = re.search(r"PR\s*#?(\d+)", text)
    pr_merged = int(pr_match.group(1)) if pr_match else None

    # Path relativo al repo
    rel_path = str(md.relative_to(REPO))

    return SprintEntry(
        id=sprint_id,
        title=title[:180],
        status=status,
        paradigm=paradigm,
        objetivos_maestros=sorted(set(objetivos)),
        capas_transversales=sorted(set(capas)),
        path=rel_path,
        pr_merged=pr_merged,
        aliases=[raw_id] if raw_id != sprint_id else [],
        sources=[f"md:{rel_path}"],
    )

def fetch_fabric_registry() -> list[SprintEntry]:
    """Lee SPRINT_REGISTRY.yaml de la rama interfaces-context-fabric-001."""
    try:
        result = subprocess.run(
            ["git", "show", "origin/interfaces-context-fabric-001:interfaces_context_fabric/maps/SPRINT_REGISTRY.yaml"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            print(f"[fabric] git show failed: {result.stderr[:200]}", file=sys.stderr)
            return []
        try:
            import yaml
        except ImportError:
            print("[fabric] PyYAML no instalado; saltando fabric registry", file=sys.stderr)
            return []
        data = yaml.safe_load(result.stdout)
    except Exception as e:
        print(f"[fabric] error: {e}", file=sys.stderr)
        return []

    entries: list[SprintEntry] = []
    if not isinstance(data, dict):
        return entries

    # Estructura esperada: data['sprints'] o data['por_canonizar'] o similar
    candidates_keys = ["sprints", "por_canonizar", "pendientes", "registry"]
    sprint_list = []
    for k in candidates_keys:
        if k in data and isinstance(data[k], list):
            sprint_list = data[k]
            break

    if not sprint_list and isinstance(data, dict):
        # Tal vez cada key es un sprint
        for k, v in data.items():
            if isinstance(v, dict) and ("title" in v or "id" in v or "status" in v):
                v["id"] = v.get("id", k)
                sprint_list.append(v)

    for item in sprint_list:
        if not isinstance(item, dict):
            continue
        raw_id = str(item.get("id") or item.get("ID") or item.get("name") or "")
        if not raw_id:
            continue
        sid = normalize_id(raw_id)
        title = str(item.get("title") or item.get("nombre") or item.get("description", ""))[:180]
        status_raw = str(item.get("status") or item.get("estado") or "PROPOSED").upper()
        status_map = {
            "POR_CANONIZAR": "PROPOSED",
            "POR CANONIZAR": "PROPOSED",
            "CANONIZADO": "SIGNED",
            "FIRMADO": "SIGNED",
            "SIGNED": "SIGNED",
            "PROPOSED": "PROPOSED",
            "PROPUESTO": "PROPOSED",
            "IN_PROGRESS": "IN_PROGRESS",
            "EN CURSO": "IN_PROGRESS",
            "BLOCKED": "BLOCKED",
            "BLOQUEADO": "BLOCKED",
            "COMPLETED": "COMPLETED",
            "COMPLETADO": "COMPLETED",
            "DONE": "COMPLETED",
            "CANCELLED": "CANCELLED",
            "CANCELADO": "CANCELLED",
        }
        status = status_map.get(status_raw, "PROPOSED")

        paradigm = str(item.get("paradigm") or item.get("paradigma") or "transversal")

        oms_raw = item.get("objetivos_maestros") or item.get("OM") or []
        if isinstance(oms_raw, (list, tuple)):
            oms = [int(x) for x in oms_raw if str(x).isdigit() and 1 <= int(x) <= 15]
        else:
            oms = [int(n) for n in re.findall(r"\d+", str(oms_raw)) if 1 <= int(n) <= 15]

        capas_raw = item.get("capas_transversales") or item.get("capas") or []
        if isinstance(capas_raw, (list, tuple)):
            capas = [str(c).upper() for c in capas_raw if re.match(r"^C\d$", str(c).upper())]
        else:
            capas = [c.upper() for c in re.findall(r"C\d", str(capas_raw))]

        entries.append(SprintEntry(
            id=sid,
            title=title or sid,
            status=status,
            paradigm=paradigm,
            objetivos_maestros=sorted(set(oms)),
            capas_transversales=sorted(set(capas)),
            aliases=[raw_id] if raw_id != sid else [],
            sources=["fabric_registry"],
        ))
    return entries

def fetch_pr_data() -> dict[str, int]:
    """Mapea sprint_id (normalizado) -> PR number a través de búsqueda en commits/PRs."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--state", "merged", "--limit", "200",
             "--json", "number,title,headRefName,mergedAt"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            env={"NO_COLOR": "1", "GH_NO_COLOR": "1", "PATH": "/usr/local/bin:/usr/bin:/bin"},
        )
        # Limpiar ANSI por si acaso
        clean = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
        import json
        prs = json.loads(clean)
    except Exception as e:
        print(f"[gh] no se pudo obtener PRs: {e}", file=sys.stderr)
        return {}

    pr_by_id: dict[str, int] = {}
    for pr in prs:
        title = (pr.get("title") or "").upper()
        head = (pr.get("headRefName") or "").upper()
        # Buscar IDs en title y branch
        candidates = re.findall(r"[A-Z][A-Z0-9]+(?:[_\-][A-Z0-9]+){1,5}", title + " " + head)
        for cand in candidates:
            sid = normalize_id(cand)
            if len(sid) >= 4 and sid not in pr_by_id:
                pr_by_id[sid] = pr["number"]
    return pr_by_id

# ---------- Deduplicación ----------
def deduplicate(entries: list[SprintEntry]) -> tuple[list[SprintEntry], list[dict[str, Any]]]:
    """Agrupa por ID exacto + reporta similares para revisión humana."""
    by_id: dict[str, SprintEntry] = {}
    conflicts: list[dict[str, Any]] = []

    # Pasada 1: merge por id exacto
    for entry in entries:
        if entry.id in by_id:
            existing = by_id[entry.id]
            # Política: completed > in_progress > signed > blocked > proposed
            priority_order = {"COMPLETED": 5, "IN_PROGRESS": 4, "SIGNED": 3, "BLOCKED": 2, "PROPOSED": 1, "CANCELLED": 0}
            if priority_order.get(entry.status, 0) > priority_order.get(existing.status, 0):
                # Nuevo gana, pero conserva metadata del existente
                merged = entry
                merged.aliases = sorted(set(existing.aliases + entry.aliases))
                merged.sources = sorted(set(existing.sources + entry.sources))
                if existing.path and not merged.path:
                    merged.path = existing.path
                if existing.pr_merged and not merged.pr_merged:
                    merged.pr_merged = existing.pr_merged
                by_id[entry.id] = merged
            else:
                # Existente gana, agrega aliases/sources
                existing.aliases = sorted(set(existing.aliases + entry.aliases))
                existing.sources = sorted(set(existing.sources + entry.sources))
                if entry.path and not existing.path:
                    existing.path = entry.path
                if entry.pr_merged and not existing.pr_merged:
                    existing.pr_merged = entry.pr_merged
                if entry.objetivos_maestros and not existing.objetivos_maestros:
                    existing.objetivos_maestros = entry.objetivos_maestros
        else:
            by_id[entry.id] = entry

    # Pasada 2: detectar similitudes >= 0.85 entre IDs distintos (potenciales duplicados)
    ids = sorted(by_id.keys())
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            sim = similarity(a, b)
            if sim >= 0.85:
                conflicts.append({
                    "type": "potential_duplicate",
                    "sim": round(sim, 3),
                    "id_a": a,
                    "id_b": b,
                    "title_a": by_id[a].title[:60],
                    "title_b": by_id[b].title[:60],
                    "sources_a": by_id[a].sources,
                    "sources_b": by_id[b].sources,
                })

    return list(by_id.values()), conflicts

# ---------- Output ----------
def to_yaml_dict(entry: SprintEntry) -> dict[str, Any]:
    d = asdict(entry)
    # Eliminar campos sources (debug only) y campos vacíos opcionales
    d.pop("sources", None)
    if not d["aliases"]:
        d.pop("aliases")
    if not d["bloquea_a"]:
        d.pop("bloquea_a")
    if not d["bloqueado_por"]:
        d.pop("bloqueado_por")
    if not d["objetivos_maestros"]:
        d.pop("objetivos_maestros")
    if not d["capas_transversales"]:
        d.pop("capas_transversales")
    if d["eta_days"] is None:
        d.pop("eta_days")
    if d["pr_merged"] is None:
        d.pop("pr_merged")
    if d["completed_at"] is None:
        d.pop("completed_at")
    if not d["owner"]:
        d.pop("owner")
    if not d["notes"]:
        d.pop("notes")
    if d["path"] is None:
        d.pop("path")
    return d

def write_registry(entries: list[SprintEntry], dry_run: bool) -> None:
    try:
        import yaml
    except ImportError:
        print("PyYAML requerido. Instalar con: sudo pip3 install pyyaml", file=sys.stderr)
        sys.exit(2)

    entries_sorted = sorted(entries, key=lambda e: (e.status != "PROPOSED", e.status != "SIGNED", e.id))
    data = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_doc": "sprints/REGISTRY_SCHEMA.md",
        "sprints": [to_yaml_dict(e) for e in entries_sorted],
    }

    yaml_text = "# Sprint Registry — Fuente única de verdad\n"
    yaml_text += "# Generado por scripts/migrate_to_sprint_registry.py (Sprint 91.16)\n"
    yaml_text += "# Schema: ver sprints/REGISTRY_SCHEMA.md\n\n"
    yaml_text += yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False, width=200)

    if dry_run:
        print(yaml_text[:3000])
        print(f"\n[dry-run] {len(entries)} sprints serían escritos a {REGISTRY_OUT}")
        return

    REGISTRY_OUT.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_OUT.write_text(yaml_text, encoding="utf-8")
    print(f"[ok] Registry escrito en {REGISTRY_OUT} ({len(entries)} sprints)")

def write_conflicts(conflicts: list[dict[str, Any]], dry_run: bool) -> None:
    if not conflicts:
        return
    md = ["# Sprint Migration — Conflictos potenciales", "",
          f"Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}", "",
          f"Total: {len(conflicts)} pares con similitud >= 0.85", "",
          "Revisar manualmente y, si son el mismo sprint, fusionarlos en `sprints/registry.yaml` agregando uno como alias del otro.", "",
          "| Sim | ID A | ID B | Título A | Título B | Fuentes A | Fuentes B |",
          "|---|---|---|---|---|---|---|"]
    for c in sorted(conflicts, key=lambda x: -x["sim"]):
        md.append(f"| {c['sim']} | `{c['id_a']}` | `{c['id_b']}` | {c['title_a']} | {c['title_b']} | {', '.join(c['sources_a'])} | {', '.join(c['sources_b'])} |")
    text = "\n".join(md)
    if dry_run:
        print("\n" + text[:2000])
        return
    CONFLICTS_OUT.write_text(text, encoding="utf-8")
    print(f"[ok] Conflictos escritos en {CONFLICTS_OUT} ({len(conflicts)} pares)")

# ---------- Main ----------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="No escribir archivos, solo imprimir")
    args = ap.parse_args()

    print(f"[migrate] Iniciando Sprint 91.16 — registry consolidation")
    print(f"[migrate] Repo: {REPO}")
    if not REPO.exists():
        print(f"[fatal] Repo no encontrado", file=sys.stderr)
        return 1

    all_entries: list[SprintEntry] = []

    # 1. Archivos en sprints_propuestos
    if PROPUESTOS_DIR.exists():
        for md in sorted(PROPUESTOS_DIR.glob("sprint_*.md")):
            entry = parse_md_file(md, status_default="PROPOSED")
            if entry:
                all_entries.append(entry)
        print(f"[propuestos] {len([e for e in all_entries if 'sprints_propuestos' in str(e.path)])} sprints")

    # 2. Archivos en sprints_completados
    completados_count = 0
    if COMPLETADOS_DIR.exists():
        for md in sorted(COMPLETADOS_DIR.glob("sprint_*.md")):
            entry = parse_md_file(md, status_default="COMPLETED")
            if entry:
                all_entries.append(entry)
                completados_count += 1
    print(f"[completados] {completados_count} sprints")

    # 3. Fabric registry
    fabric_entries = fetch_fabric_registry()
    print(f"[fabric] {len(fabric_entries)} sprints")
    all_entries.extend(fabric_entries)

    # 4. PRs mergeados (mapeo id -> PR para enriquecer estado COMPLETED)
    pr_by_id = fetch_pr_data()
    print(f"[gh-prs] {len(pr_by_id)} sprint IDs detectados en PRs mergeados")
    for entry in all_entries:
        if entry.id in pr_by_id and not entry.pr_merged:
            entry.pr_merged = pr_by_id[entry.id]
            if entry.status == "PROPOSED":
                entry.status = "COMPLETED"
                entry.sources.append("gh_pr")

    # Deduplicar
    final, conflicts = deduplicate(all_entries)
    print(f"[dedup] {len(all_entries)} entries -> {len(final)} sprints únicos")
    print(f"[dedup] {len(conflicts)} pares con similitud >= 0.85 (revisión manual)")

    # Estadísticas finales
    by_status: dict[str, int] = defaultdict(int)
    by_paradigm: dict[str, int] = defaultdict(int)
    for e in final:
        by_status[e.status] += 1
        by_paradigm[e.paradigm] += 1
    print(f"\n[stats] Por estado:")
    for k, v in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"[stats] Por paradigma:")
    for k, v in sorted(by_paradigm.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    write_registry(final, args.dry_run)
    write_conflicts(conflicts, args.dry_run)

    return 0

if __name__ == "__main__":
    sys.exit(main())
