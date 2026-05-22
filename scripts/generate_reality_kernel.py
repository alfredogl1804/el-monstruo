#!/usr/bin/env python3
"""
REALITY KERNEL Generator v1.0
==============================
Consume MONSTRUO_GENOME.yaml y produce automaticamente:
  1. monstruo_reality_atlas/00_DOCTRINE_VETO.md
  2. monstruo_reality_atlas/01_ENTITY_MATRIX.md
  3. monstruo_reality_atlas/02_REALITY_PULSE.yaml

Principio: El Reality Kernel es un DERIVADO del Genoma.
Si el Genoma se actualiza, este script regenera la capa de proteccion.

Ejecutar: python3 scripts/generate_reality_kernel.py
Requiere: MONSTRUO_GENOME.yaml existente (correr genome_generator.py primero)
"""

import sys
import re
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
GENOME_FILE = REPO_ROOT / "MONSTRUO_GENOME.yaml"
OUTPUT_DIR = REPO_ROOT / "monstruo_reality_atlas"

ONTOLOGY_RULES = [
    ("memory", "MEMORY_SYSTEM", "Sistemas de memoria y persistencia cognitiva"),
    ("anti_dory", "MEMORY_SYSTEM", "Sistemas de memoria y persistencia cognitiva"),
    ("memento", "MEMORY_SYSTEM", "Sistemas de memoria y persistencia cognitiva"),
    ("sms", "MEMORY_SYSTEM", "Sistemas de memoria y persistencia cognitiva"),
    ("embrion", "WORKER_ROLE", "Agentes especialistas que ejecutan tareas"),
    ("collective", "WORKER_ROLE", "Agentes especialistas que ejecutan tareas"),
    ("catastro", "INTELLIGENCE_SYSTEM", "Sistemas de inteligencia y registro"),
    ("vanguard", "INTELLIGENCE_SYSTEM", "Sistemas de inteligencia y registro"),
    ("learning", "INTELLIGENCE_SYSTEM", "Sistemas de inteligencia y registro"),
    ("lightrag", "INTELLIGENCE_SYSTEM", "Sistemas de inteligencia y registro"),
    ("brand", "MAGIC_CAPABILITY", "Capacidades magicas de alto nivel"),
    ("design", "MAGIC_CAPABILITY", "Capacidades magicas de alto nivel"),
    ("cost_optimizer", "MAGIC_CAPABILITY", "Capacidades magicas de alto nivel"),
    ("adaptive_model", "MAGIC_CAPABILITY", "Capacidades magicas de alto nivel"),
    ("causal_decomposer", "MAGIC_CAPABILITY", "Capacidades magicas de alto nivel"),
    ("guardian", "GOVERNANCE", "Gobierno, seguridad y validacion"),
    ("security", "GOVERNANCE", "Gobierno, seguridad y validacion"),
    ("sovereignty", "GOVERNANCE", "Gobierno, seguridad y validacion"),
    ("validation", "GOVERNANCE", "Gobierno, seguridad y validacion"),
    ("a2ui", "PROTOCOL_SPEC", "Protocolos e interfaces de comunicacion"),
    ("mcp", "PROTOCOL_SPEC", "Protocolos e interfaces de comunicacion"),
    ("agui", "PROTOCOL_SPEC", "Protocolos e interfaces de comunicacion"),
    ("browser", "PROTOCOL_SPEC", "Protocolos e interfaces de comunicacion"),
    ("plugins", "PROTOCOL_SPEC", "Protocolos e interfaces de comunicacion"),
    ("alerts", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("dashboards", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("milestones", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("motion", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("rotor", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("runner", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("background_store", "INVISIBLE_INFRA", "Infraestructura invisible que sostiene todo"),
    ("forja", "CREATURE", "Criaturas y productos con vida propia"),
    ("like-kukulkan", "CREATURE", "Criaturas y productos con vida propia"),
    ("el-mundo-de-tata", "FUTURE_VISION", "Visiones futuras no implementadas"),
]

SATELLITE_CLASS_MAP = {
    "product": "CREATURE",
    "transport": "PROTOCOL_SPEC",
    "aspirant": "FUTURE_VISION",
    "infrastructure": "INVISIBLE_INFRA",
}


def parse_genome_lightweight(genome_path):
    """Parse MONSTRUO_GENOME.yaml using regex (no PyYAML dependency)."""
    content = genome_path.read_text()
    data = {
        "generated_at": "",
        "version": "",
        "total_kernel_modules": 0,
        "total_embriones": 0,
        "total_supabase_tables": 0,
        "total_satellites": 0,
        "kernel_modules": [],
        "embriones": [],
        "satellites": [],
        "skills": [],
        "gaps": [],
        "connections": [],
    }

    m = re.search(r'generated_at:\s*(.+)', content)
    if m:
        data["generated_at"] = m.group(1).strip()
    m = re.search(r'version:\s*(.+)', content)
    if m:
        data["version"] = m.group(1).strip()
    m = re.search(r'total_kernel_modules:\s*(\d+)', content)
    if m:
        data["total_kernel_modules"] = int(m.group(1))
    m = re.search(r'total_embriones:\s*(\d+)', content)
    if m:
        data["total_embriones"] = int(m.group(1))
    m = re.search(r'total_supabase_tables:\s*(\d+)', content)
    if m:
        data["total_supabase_tables"] = int(m.group(1))
    m = re.search(r'total_satellites:\s*(\d+)', content)
    if m:
        data["total_satellites"] = int(m.group(1))

    # Kernel modules
    for m in re.finditer(r'- id: (\w+)\n\s+path: (.+)\n\s+files: (\d+)', content):
        data["kernel_modules"].append({
            "id": m.group(1),
            "path": m.group(2).strip(),
            "files": int(m.group(3)),
        })

    # Embriones (domain_specialists)
    embrion_section = re.search(r'domain_specialists:\n((?:\s+- id:.*\n(?:\s+\w+:.*\n)*)+)', content)
    if embrion_section:
        for m in re.finditer(r'- id: (\w+)\n\s+path: (.+)', embrion_section.group(1)):
            data["embriones"].append({"id": m.group(1), "path": m.group(2).strip()})

    # Satellites
    sat_section = re.search(r'satellites:\n((?:\s+- id:.*\n(?:\s+\w+:.*\n)*)+)', content)
    if sat_section:
        current_sat = {}
        for line in sat_section.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- id:'):
                if current_sat:
                    data["satellites"].append(current_sat)
                current_sat = {"id": line.split(':', 1)[1].strip()}
            elif ':' in line and current_sat:
                key, val = line.split(':', 1)
                current_sat[key.strip()] = val.strip()
        if current_sat:
            data["satellites"].append(current_sat)

    # Skills
    skills_section = re.search(r'items:\n((?:\s+- .+\n)+)', content)
    if skills_section:
        for m in re.finditer(r'- (.+)', skills_section.group(1)):
            data["skills"].append(m.group(1).strip())

    # Gaps
    for m in re.finditer(r'- id: (\w+)\n\s+description: (.+)', content):
        data["gaps"].append({"id": m.group(1), "description": m.group(2).strip()})

    return data


def classify_entity(entity_id):
    """Classify an entity into an ontological class."""
    entity_lower = entity_id.lower()
    for pattern, cls, _ in ONTOLOGY_RULES:
        if pattern in entity_lower:
            return cls
    return "INVISIBLE_INFRA"


def generate_doctrine_veto(genome_data):
    """Generate 00_DOCTRINE_VETO.md from genome data."""
    all_entities = set()
    for mod in genome_data["kernel_modules"]:
        all_entities.add(mod["id"])
    for emb in genome_data["embriones"]:
        all_entities.add(emb["id"])
    for sat in genome_data["satellites"]:
        all_entities.add(sat["id"])

    classes = {}
    for entity in sorted(all_entities):
        cls = classify_entity(entity)
        if cls not in classes:
            classes[cls] = []
        classes[cls].append(entity)

    lines = []
    lines.append("# 00 - DOCTRINE VETO")
    lines.append("")
    lines.append(f"> Auto-generado desde MONSTRUO_GENOME.yaml ({genome_data['generated_at']})")
    lines.append(f"> Regenerar: `python3 scripts/generate_reality_kernel.py`")
    lines.append("")
    lines.append("## Proposito")
    lines.append("")
    lines.append("Este documento define QUE NO PROPONER. Si algo aparece aqui, ya existe.")
    lines.append("Proponer recrearlo es **RECHAZADO_DUPLICA_CANON**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Reglas Duras")
    lines.append("")
    lines.append("1. **NUNCA** proponer un sistema de memoria soberana - ya existe (SMS v4.0).")
    lines.append("2. **NUNCA** proponer un orquestador de agentes - ya existe (Embrion Loop).")
    lines.append("3. **NUNCA** proponer un sistema anti-olvido - ya existe (Anti-Dory).")
    lines.append("4. **NUNCA** proponer un catastro de modelos - ya existe (kernel/catastro/).")
    lines.append("5. **NUNCA** proponer un bot de Telegram nuevo - ya existe (el-monstruo-bot).")
    lines.append("6. **NUNCA** proponer un sistema de boleteria - ya existe (like-kukulkan-tickets).")
    lines.append("7. **NUNCA** proponer un MCP gateway - ya existe (forja-mcp).")
    lines.append("8. **NUNCA** proponer un sistema de gobernanza - ya existe (Guardian + DSCs).")
    lines.append("9. **NUNCA** proponer un knowledge graph - ya existe (SMS v4.0 knowledge_graph).")
    lines.append("10. **NUNCA** proponer un sistema de brand/identidad - ya existe (kernel/brand/).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Workflow: Probe-Before-Propose (6 pasos)")
    lines.append("")
    lines.append("Antes de proponer CUALQUIER componente nuevo:")
    lines.append("")
    lines.append("```bash")
    lines.append("# Paso 1: Buscar en el Genoma")
    lines.append("grep -i '<nombre_propuesto>' MONSTRUO_GENOME.yaml")
    lines.append("")
    lines.append("# Paso 2: Buscar en el kernel")
    lines.append("find kernel/ -iname '*<nombre>*'")
    lines.append("")
    lines.append("# Paso 3: Buscar en Supabase")
    lines.append("grep -i '<nombre>' MONSTRUO_GENOME.yaml | grep 'table\\|rpc'")
    lines.append("")
    lines.append("# Paso 4: Buscar en satelites")
    lines.append("grep -i '<nombre>' MONSTRUO_GENOME.yaml | grep 'satellite'")
    lines.append("")
    lines.append("# Paso 5: Buscar en skills")
    lines.append("ls /home/ubuntu/skills/ | grep -i '<nombre>'")
    lines.append("")
    lines.append("# Paso 6: Si NADA aparece -> proponer. Si ALGO aparece -> RECHAZADO_DUPLICA_CANON.")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Espacio Negativo por Clase Ontologica")
    lines.append("")

    class_descriptions = {
        "MEMORY_SYSTEM": "NO proponer nuevos stores, caches, o persistencias cognitivas",
        "WORKER_ROLE": "NO proponer nuevos embriones o especialistas sin verificar",
        "INTELLIGENCE_SYSTEM": "NO proponer nuevos registros, catastros, o RAGs",
        "MAGIC_CAPABILITY": "NO proponer optimizadores, selectores, o decomposers",
        "GOVERNANCE": "NO proponer nuevos guardianes, validadores, o auditores",
        "PROTOCOL_SPEC": "NO proponer nuevas interfaces, adapters, o gateways",
        "INVISIBLE_INFRA": "NO proponer nuevos runners, rotors, o dashboards",
        "CREATURE": "NO proponer nuevos productos sin firma T1",
        "FUTURE_VISION": "Existen como aspirantes, no duplicar",
    }

    for cls, entities in sorted(classes.items()):
        desc = class_descriptions.get(cls, cls)
        lines.append(f"### {cls}")
        lines.append(f"*{desc}*")
        lines.append("")
        lines.append("| Entidad | Path/Repo | Estado |")
        lines.append("|---|---|---|")
        for entity in entities:
            path = "kernel/"
            status = "production"
            for mod in genome_data["kernel_modules"]:
                if mod["id"] == entity:
                    path = mod["path"]
                    break
            for emb in genome_data["embriones"]:
                if emb["id"] == entity:
                    path = emb["path"]
                    break
            for sat in genome_data["satellites"]:
                if sat["id"] == entity:
                    path = sat.get("repo", sat["id"])
                    status = sat.get("status", "unknown")
                    break
            lines.append(f"| {entity} | `{path}` | {status} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 4. Caso de Prueba Obligatorio")
    lines.append("")
    lines.append("Si un agente propone: *\"Crear un sistema de memoria soberana para Manus\"*")
    lines.append("")
    lines.append("**Resultado esperado:** `RECHAZADO_DUPLICA_CANON`")
    lines.append("**Razon:** SMS v4.0 ya existe en `kernel/memory/`, con 12 tablas en Supabase,")
    lines.append("14 RPCs, knowledge graph, belief revision, y temporal validity.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Source Precedence (Jerarquia de la Verdad)")
    lines.append("")
    lines.append("| Nivel | Fuente | Autoridad |")
    lines.append("|---|---|---|")
    lines.append("| 1 | Codigo en produccion (Railway /health) | Maxima |")
    lines.append("| 2 | DSC firmado por T1 + T2 | Alta |")
    lines.append("| 3 | AGENTS.md | Alta |")
    lines.append("| 4 | MONSTRUO_GENOME.yaml (auto-generado) | Media |")
    lines.append("| 5 | Reality Kernel (este archivo, derivado) | Media-baja |")
    lines.append("| 6 | Propuestas no firmadas | Baja |")
    lines.append("")
    lines.append("> **Nota:** Este archivo es nivel 5 - PROPUESTA hasta firma T1.")
    lines.append("> No se auto-canoniza. Requiere audit T2 + firma T1 para subir a nivel 2.")
    lines.append("")
    lines.append("> **Regla de incertidumbre:** Si un agente no puede verificar nivel 1")
    lines.append("> (no tiene credenciales para pingar produccion), DEBE declarar incertidumbre")
    lines.append("> explicitamente en vez de asumir que el dato del nivel 4-5 es correcto.")
    lines.append("")

    return "\n".join(lines) + "\n"


def generate_entity_matrix(genome_data):
    """Generate 01_ENTITY_MATRIX.md from genome data."""
    entities = []

    for mod in genome_data["kernel_modules"]:
        entities.append({
            "id": mod["id"],
            "class": classify_entity(mod["id"]),
            "path": mod["path"],
            "files": mod["files"],
            "source": "kernel",
            "status": "production",
        })

    for emb in genome_data["embriones"]:
        entities.append({
            "id": emb["id"],
            "class": classify_entity(emb["id"]),
            "path": emb["path"],
            "files": 1,
            "source": "embrion",
            "status": "production",
        })

    for sat in genome_data["satellites"]:
        sat_type = sat.get("type", "unknown")
        entities.append({
            "id": sat["id"],
            "class": SATELLITE_CLASS_MAP.get(sat_type, "CREATURE"),
            "path": sat.get("repo", sat["id"]),
            "files": 0,
            "source": "satellite",
            "status": sat.get("status", "unknown"),
        })

    seen = set()
    unique_entities = []
    for e in entities:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique_entities.append(e)

    unique_entities.sort(key=lambda x: (x["class"], x["id"]))

    lines = []
    lines.append("# 01 - ENTITY MATRIX (Tabla Periodica del Monstruo)")
    lines.append("")
    lines.append(f"> Auto-generado desde MONSTRUO_GENOME.yaml ({genome_data['generated_at']})")
    lines.append(f"> Total entidades: {len(unique_entities)}")
    lines.append(f"> Regenerar: `python3 scripts/generate_reality_kernel.py`")
    lines.append("")
    lines.append("---")
    lines.append("")

    current_class = None
    for entity in unique_entities:
        if entity["class"] != current_class:
            if current_class is not None:
                lines.append("")
            current_class = entity["class"]
            class_desc = ""
            for _, cls, desc in ONTOLOGY_RULES:
                if cls == current_class:
                    class_desc = desc
                    break
            lines.append(f"## {current_class}")
            lines.append(f"*{class_desc}*")
            lines.append("")
            lines.append("| ID | Path | Files | Source | Status |")
            lines.append("|---|---|---|---|---|")

        lines.append(f"| {entity['id']} | `{entity['path']}` | {entity['files']} | {entity['source']} | {entity['status']} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Clases Ontologicas (Leyenda)")
    lines.append("")
    lines.append("| Clase | Significado | Regla de Veto |")
    lines.append("|---|---|---|")
    lines.append("| MEMORY_SYSTEM | Persistencia cognitiva | No crear nuevos stores sin conectar a SMS |")
    lines.append("| WORKER_ROLE | Agentes que ejecutan | No crear embriones sin verificar existentes |")
    lines.append("| INTELLIGENCE_SYSTEM | Registros y RAGs | No crear catastros/indexes paralelos |")
    lines.append("| MAGIC_CAPABILITY | Capacidades de alto nivel | No duplicar optimizadores/selectores |")
    lines.append("| GOVERNANCE | Gobierno y seguridad | No crear guardianes paralelos |")
    lines.append("| PROTOCOL_SPEC | Interfaces y protocolos | No crear adapters sin verificar MCP/A2UI |")
    lines.append("| INVISIBLE_INFRA | Infraestructura base | No crear runners/rotors paralelos |")
    lines.append("| CREATURE | Productos con vida propia | No crear productos sin firma T1 |")
    lines.append("| FUTURE_VISION | Aspirantes no implementados | Existen como concepto, no duplicar |")
    lines.append("")

    return "\n".join(lines) + "\n"


def generate_reality_pulse(genome_data):
    """Generate 02_REALITY_PULSE.yaml from genome data."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = []
    lines.append("# 02_REALITY_PULSE.yaml - Estado global del Monstruo")
    lines.append(f"# Auto-derivado de MONSTRUO_GENOME.yaml")
    lines.append(f"# Generado: {now}")
    lines.append("")
    lines.append("meta:")
    lines.append(f"  derived_from: MONSTRUO_GENOME.yaml ({genome_data['version']})")
    lines.append(f"  generated_at: {now}")
    lines.append("  generator: scripts/generate_reality_kernel.py")
    lines.append("  status: PROPUESTA  # Requiere firma T1 para canonizar")
    lines.append("")
    lines.append("source_precedence:")
    lines.append("  - level: 1")
    lines.append("    source: production_runtime")
    lines.append("    description: Codigo corriendo en Railway /health")
    lines.append("    authority: maxima")
    lines.append("  - level: 2")
    lines.append("    source: dsc_firmado")
    lines.append("    description: DSC con firma T1 + T2")
    lines.append("    authority: alta")
    lines.append("  - level: 3")
    lines.append("    source: agents_md")
    lines.append("    description: AGENTS.md reglas operativas")
    lines.append("    authority: alta")
    lines.append("  - level: 4")
    lines.append("    source: genome_yaml")
    lines.append("    description: MONSTRUO_GENOME.yaml auto-generado")
    lines.append("    authority: media")
    lines.append("  - level: 5")
    lines.append("    source: reality_kernel")
    lines.append("    description: Este archivo y sus hermanos (derivados)")
    lines.append("    authority: media-baja")
    lines.append("  - level: 6")
    lines.append("    source: propuestas")
    lines.append("    description: PRs, bridges, propuestas no firmadas")
    lines.append("    authority: baja")
    lines.append("")
    lines.append("vitals:")
    lines.append(f"  kernel_modules: {genome_data['total_kernel_modules']}")
    lines.append(f"  embriones: {genome_data['total_embriones']}")
    lines.append(f"  supabase_tables: {genome_data['total_supabase_tables']}")
    lines.append(f"  satellites: {genome_data['total_satellites']}")
    lines.append(f"  skills: {len(genome_data['skills'])}")
    lines.append(f"  genome_version: {genome_data['version']}")
    lines.append(f"  genome_generated: {genome_data['generated_at']}")
    lines.append("")
    lines.append("gaps:")
    for gap in genome_data["gaps"]:
        lines.append(f"  - id: {gap['id']}")
        lines.append(f"    description: {gap['description']}")
    lines.append("")
    lines.append("uncertainties:")
    lines.append("  - field: production.kernel.status")
    lines.append("    reason: Requiere curl a Railway - puede haber cambiado")
    lines.append("  - field: supabase.table_counts")
    lines.append("    reason: Conteos son snapshot, no live")
    lines.append("  - field: satellites.railway_status")
    lines.append("    reason: Health checks son puntuales")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    print("REALITY KERNEL Generator v1.0")
    print("=" * 50)

    if not GENOME_FILE.exists():
        print(f"ERROR: {GENOME_FILE} no existe.")
        print("   Ejecuta primero: python3 scripts/genome_generator.py")
        sys.exit(1)

    print("  [1/4] Parsing MONSTRUO_GENOME.yaml...")
    genome_data = parse_genome_lightweight(GENOME_FILE)
    print(f"         Found: {genome_data['total_kernel_modules']} modules, "
          f"{genome_data['total_embriones']} embriones, "
          f"{genome_data['total_satellites']} satellites")

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("  [2/4] Generating 00_DOCTRINE_VETO.md...")
    veto = generate_doctrine_veto(genome_data)
    (OUTPUT_DIR / "00_DOCTRINE_VETO.md").write_text(veto)
    print(f"         -> {len(veto.splitlines())} lines")

    print("  [3/4] Generating 01_ENTITY_MATRIX.md...")
    matrix = generate_entity_matrix(genome_data)
    (OUTPUT_DIR / "01_ENTITY_MATRIX.md").write_text(matrix)
    print(f"         -> {len(matrix.splitlines())} lines")

    print("  [4/4] Generating 02_REALITY_PULSE.yaml...")
    pulse = generate_reality_pulse(genome_data)
    (OUTPUT_DIR / "02_REALITY_PULSE.yaml").write_text(pulse)
    print(f"         -> {len(pulse.splitlines())} lines")

    print(f"\nReality Kernel generated in: {OUTPUT_DIR}/")
    print("   Files: 00_DOCTRINE_VETO.md, 01_ENTITY_MATRIX.md, 02_REALITY_PULSE.yaml")
    print("   Status: PROPUESTA (requiere firma T1 para canonizar)")


if __name__ == "__main__":
    main()
