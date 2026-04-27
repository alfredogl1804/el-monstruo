#!/usr/bin/env python3
"""
GUARDIA — Validador Anti-Boicoteo del Monstruo.

Este script NO es documentación. Es CÓDIGO que se EJECUTA.
Cualquier hilo que lo ejecute queda blindado contra:
1. Usar modelos incorrectos/obsoletos
2. Sobrescribir archivos protegidos
3. Ignorar decisiones arquitectónicas ya tomadas
4. Perder contexto después de compactación

USO:
  python3 guardia.py              → Validación completa + inyección de reglas
  python3 guardia.py check        → Solo validar (no modifica nada)
  python3 guardia.py rules        → Imprimir reglas duras
  python3 guardia.py scan <file>  → Escanear un archivo antes de escribirlo

INTEGRACIÓN:
  Ejecutar AL INICIO de cualquier hilo.
  Ejecutar ANTES de escribir código que toque el Monstruo.
  Ejecutar DESPUÉS de compactación para recuperar reglas.
"""

import os
import sys
import re
import json
import glob
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
# REGLAS DURAS — Estas NO se negocian, NO se "actualizan", NO se ignoran
# Solo se modifican editando ESTE archivo y haciendo push a GitHub.
# ═══════════════════════════════════════════════════════════════════

REGLAS = {
    "modelos_correctos": {
        "gpt": "gpt-5.5",
        "claude": "claude-opus-4-7-20250416",
        "gemini": "gemini-3.1-pro",
        "grok": "grok-4.3-beta",
        "deepseek": "deepseek-v4-pro",
        "perplexity": "sonar-reasoning-pro"
    },
    "modelos_prohibidos": [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4",
        "claude-3.5-sonnet", "claude-3-opus", "claude-sonnet-4",
        "gemini-2.5-flash", "gemini-2.5-pro", "gemini-pro",
        "grok-3", "grok-2",
        "deepseek-v3", "deepseek-r1",
        "sonar-pro", "sonar", "gpt-5.4", "gpt-5.4-pro", "claude-sonnet-4.6", "claude-opus-4.6", "grok-4.20", "deepseek-r1-0528"
    ],
    "archivos_protegidos": [
        # Kernel — NO tocar sin validar primero
        "server/kernel.py",
        "server/memory/",
        "server/knowledge/",
        # Configuración crítica
        ".env",
        "railway.toml",
        "Dockerfile",
    ],
    "decisiones_tomadas": {
        "runtime": "LangGraph + AsyncPostgresSaver (NO Temporal, DESCARTADO)",
        "cerebro": "GPT-5.5 Pro como modelo principal del SOP",
        "memoria": "4 capas: mempalace + mem0 + lightrag + checkpointer",
        "deploy": "Railway (NO Vercel, NO Cloudflare Workers)",
        "embeddings": "OpenAI text-embedding-3-small",
        "lightrag_llm": "Gemini 2.5 Flash (migrado de gpt-4o-mini en Sprint 31)",
        "persistencia_grafo": "PostgreSQL (NetworkX serializado, NO archivo local)",
        "orquestador": "Este hilo es el principal. Kernel Thread archivado.",
        "framework_web": "React 19 + Tailwind 4 + tRPC 11 (sitio web del Monstruo)"
    },
    "patrones_prohibidos": [
        # Patrones que indican que el hilo está usando info obsoleta
        r"gemini-2\.5-pro",
        r"gemini-2\.5-flash(?!.*lightrag)",  # OK solo para lightrag
        r"gpt-4o(?!-mini.*lightrag)",
        r"claude-3\.5",
        r"from temporal",
        r"import temporal",
        r"TemporalClient",
    ]
}

# ═══════════════════════════════════════════════════════════════════
# KERNEL CONNECTION
# ═══════════════════════════════════════════════════════════════════

KERNEL_URL = os.environ.get(
    "MONSTRUO_KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app"
)
KERNEL_KEY = os.environ.get(
    "MONSTRUO_API_KEY",
    "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259"
)


def query_kernel(query, top_k=2):
    """Consulta rápida al kernel. Timeout agresivo — no bloquea si falla."""
    try:
        resp = requests.post(
            f"{KERNEL_URL}/v1/knowledge/query",
            headers={"X-API-Key": KERNEL_KEY, "Content-Type": "application/json"},
            json={"query": query, "mode": "naive", "top_k": top_k},
            timeout=12
        )
        if resp.status_code == 200:
            return resp.json().get("results", "")
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════
# VALIDADORES
# ═══════════════════════════════════════════════════════════════════

def validar_modelos_en_archivo(filepath):
    """Escanea un archivo buscando modelos prohibidos."""
    violaciones = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return violaciones

    for modelo in REGLAS["modelos_prohibidos"]:
        if modelo in content:
            violaciones.append({
                "tipo": "MODELO_PROHIBIDO",
                "archivo": filepath,
                "modelo_encontrado": modelo,
                "correccion": f"Reemplazar con el modelo correcto. Ver REGLAS.modelos_correctos"
            })

    for pattern in REGLAS["patrones_prohibidos"]:
        matches = re.findall(pattern, content)
        if matches:
            violaciones.append({
                "tipo": "PATRON_PROHIBIDO",
                "archivo": filepath,
                "patron": pattern,
                "matches": matches[:3],
                "correccion": "Este patrón indica uso de tecnología obsoleta/descartada"
            })

    return violaciones


def validar_sandbox():
    """Escanea todo el sandbox buscando violaciones."""
    violaciones = []
    home = os.environ.get("HOME", "/home/ubuntu")

    # Escanear archivos Python y JS/TS
    extensiones = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.md"]
    for ext in extensiones:
        for filepath in glob.glob(os.path.join(home, "**", ext), recursive=True):
            # Ignorar node_modules y .git
            if "node_modules" in filepath or ".git/" in filepath:
                continue
            violaciones.extend(validar_modelos_en_archivo(filepath))

    return violaciones


def validar_archivo_antes_de_escribir(filepath, contenido):
    """Valida contenido ANTES de que se escriba. Retorna violaciones."""
    violaciones = []

    # Verificar si es archivo protegido
    for protegido in REGLAS["archivos_protegidos"]:
        if protegido in filepath:
            violaciones.append({
                "tipo": "ARCHIVO_PROTEGIDO",
                "archivo": filepath,
                "correccion": f"Este archivo está protegido. Verificar con el kernel antes de modificar."
            })

    # Verificar modelos prohibidos en el contenido nuevo
    for modelo in REGLAS["modelos_prohibidos"]:
        if modelo in contenido:
            violaciones.append({
                "tipo": "MODELO_PROHIBIDO_EN_NUEVO_CODIGO",
                "archivo": filepath,
                "modelo_encontrado": modelo,
                "correccion": f"NO usar {modelo}. Modelos correctos: {json.dumps(REGLAS['modelos_correctos'])}"
            })

    # Verificar patrones prohibidos
    for pattern in REGLAS["patrones_prohibidos"]:
        if re.search(pattern, contenido):
            violaciones.append({
                "tipo": "PATRON_PROHIBIDO_EN_NUEVO_CODIGO",
                "archivo": filepath,
                "patron": pattern,
                "correccion": "Patrón indica tecnología obsoleta/descartada"
            })

    return violaciones


# ═══════════════════════════════════════════════════════════════════
# INYECTOR DE REGLAS
# ═══════════════════════════════════════════════════════════════════

def inyectar_reglas():
    """Genera un archivo REGLAS_DURAS.md en el sandbox para referencia rápida."""
    home = os.environ.get("HOME", "/home/ubuntu")
    output = os.path.join(home, "REGLAS_DURAS.md")

    lines = [
        "# REGLAS DURAS DEL MONSTRUO",
        f"**Generado por guardia.py:** {datetime.utcnow().isoformat()}Z",
        "",
        "## Modelos Correctos (ÚNICOS permitidos)",
        ""
    ]

    for sabio, modelo in REGLAS["modelos_correctos"].items():
        lines.append(f"- **{sabio.upper()}:** `{modelo}`")

    lines.extend([
        "",
        "## Modelos PROHIBIDOS (si los ves, CORRIGE inmediatamente)",
        ""
    ])
    for m in REGLAS["modelos_prohibidos"]:
        lines.append(f"- ~~{m}~~")

    lines.extend([
        "",
        "## Decisiones Arquitectónicas YA TOMADAS (no rediscutir)",
        ""
    ])
    for k, v in REGLAS["decisiones_tomadas"].items():
        lines.append(f"- **{k}:** {v}")

    lines.extend([
        "",
        "## Archivos Protegidos (no modificar sin validar)",
        ""
    ])
    for f in REGLAS["archivos_protegidos"]:
        lines.append(f"- `{f}`")

    lines.extend([
        "",
        "---",
        "**Este archivo fue generado por código. No editarlo manualmente.**",
        "**Para actualizar reglas: editar guardia.py y hacer push a GitHub.**",
        ""
    ])

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"

    if cmd == "rules":
        # Solo imprimir reglas
        print("═══ MODELOS CORRECTOS ═══")
        for k, v in REGLAS["modelos_correctos"].items():
            print(f"  {k.upper()}: {v}")
        print("\n═══ DECISIONES TOMADAS ═══")
        for k, v in REGLAS["decisiones_tomadas"].items():
            print(f"  {k}: {v}")
        return

    if cmd == "scan":
        # Escanear un archivo específico
        if len(sys.argv) < 3:
            print("Uso: guardia.py scan <archivo>")
            sys.exit(1)
        filepath = sys.argv[2]
        try:
            with open(filepath, "r") as f:
                contenido = f.read()
        except Exception as e:
            print(f"Error leyendo {filepath}: {e}")
            sys.exit(1)
        violaciones = validar_archivo_antes_de_escribir(filepath, contenido)
        if violaciones:
            print(f"⛔ {len(violaciones)} VIOLACIONES en {filepath}:")
            for v in violaciones:
                print(f"  [{v['tipo']}] {v.get('modelo_encontrado', v.get('patron', ''))}")
                print(f"  → {v['correccion']}")
            sys.exit(1)
        else:
            print(f"✓ {filepath} — limpio")
        return

    if cmd == "check":
        # Validar todo el sandbox sin modificar nada
        print("[guardia] Escaneando sandbox...")
        violaciones = validar_sandbox()
        if violaciones:
            print(f"⛔ {len(violaciones)} VIOLACIONES encontradas:")
            for v in violaciones:
                print(f"  [{v['tipo']}] {v['archivo']}")
                print(f"    → {v.get('modelo_encontrado', v.get('patron', ''))}")
                print(f"    → {v['correccion']}")
            sys.exit(1)
        else:
            print("✓ Sandbox limpio. Sin violaciones.")
        return

    # cmd == "full" — Validación completa + inyección
    print("═══════════════════════════════════════════════════════")
    print("  GUARDIA DEL MONSTRUO — Anti-Boicoteo Activo")
    print("═══════════════════════════════════════════════════════")

    # 1. Inyectar reglas
    output = inyectar_reglas()
    print(f"[guardia] Reglas inyectadas → {output}")

    # 2. Validar sandbox
    print("[guardia] Escaneando sandbox...")
    violaciones = validar_sandbox()
    if violaciones:
        print(f"⛔ {len(violaciones)} VIOLACIONES:")
        for v in violaciones[:10]:  # Máximo 10 para no saturar
            print(f"  [{v['tipo']}] {v['archivo']}")
            print(f"    {v.get('modelo_encontrado', v.get('patron', ''))}")
        if len(violaciones) > 10:
            print(f"  ... y {len(violaciones) - 10} más")
    else:
        print("[guardia] ✓ Sin violaciones")

    # 3. Consultar kernel para reglas actualizadas (si disponible)
    print("[guardia] Consultando kernel...")
    kernel_rules = query_kernel("reglas duras decisiones arquitectónicas modelos verificados")
    if kernel_rules:
        print("[guardia] ✓ Kernel respondió — reglas confirmadas")
    else:
        print("[guardia] ⚠ Kernel no disponible — usando reglas locales (hardcoded)")

    # 4. Resumen
    print("═══════════════════════════════════════════════════════")
    print("  MODELOS CORRECTOS:")
    for k, v in REGLAS["modelos_correctos"].items():
        print(f"    {k.upper()}: {v}")
    print("═══════════════════════════════════════════════════════")
    print(f"  Leer reglas completas: cat ~/REGLAS_DURAS.md")
    print(f"  Validar archivo: python3 guardia.py scan <archivo>")
    print("═══════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
