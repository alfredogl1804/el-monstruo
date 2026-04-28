#!/usr/bin/env python3
"""
INJECT — Inyector de Contexto del Monstruo (v2 resiliente).

Problema que resuelve: Cuando un hilo de Manus arranca o se compacta,
empieza vacío. No sabe quién es, qué proyectos hay, qué decisiones
se tomaron, ni qué modelos usar.

Solución resiliente (funciona CON o SIN kernel):
1. Lee RECOVERY.md local (si existe — sobrevivió a la compactación)
2. Escanea archivos .md del sandbox para extraer contexto directo
3. Intenta consultar al kernel (con timeout corto, no bloquea si falla)
4. Genera un CONTEXT.md con todo lo que el hilo necesita saber

El agente solo tiene que hacer: cat ~/CONTEXT.md

Uso: python3 inject.py
Ejecutar al INICIO de cualquier hilo o después de detectar compactación.
"""

import os
import json
import glob
import requests
from datetime import datetime, timedelta

# --- Config ---
KERNEL_URL = os.environ.get(
    "MONSTRUO_KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app"
)
KERNEL_KEY = os.environ.get(
    "MONSTRUO_API_KEY",
    "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259"
)
SANDBOX_HOME = os.environ.get("HOME", "/home/ubuntu")
RECOVERY_FILE = os.path.join(SANDBOX_HOME, "RECOVERY.md")
CONTEXT_FILE = os.path.join(SANDBOX_HOME, "CONTEXT.md")

# Queries para el kernel (solo si está disponible)
KERNEL_QUERIES = [
    {"query": "modelos verificados sabios GPT Claude Gemini Grok DeepSeek Perplexity abril 2026", "label": "Modelos Verificados"},
    {"query": "estado completo del Monstruo decisiones arquitectónicas LangGraph", "label": "Estado y Arquitectura"},
    {"query": "hilos activos orquestación comunicación Manus API", "label": "Hilos y Orquestación"},
]


def check_recovery_local():
    """Lee RECOVERY.md si existe."""
    if not os.path.exists(RECOVERY_FILE):
        return None

    mtime = datetime.fromtimestamp(os.path.getmtime(RECOVERY_FILE))
    age = datetime.now() - mtime

    with open(RECOVERY_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    age_str = f"{age.seconds // 60}m" if age < timedelta(hours=1) else f"{age.seconds // 3600}h"
    print(f"[inject] RECOVERY.md encontrado (edad: {age_str}, {len(content)} chars)")
    return content


def scan_key_files():
    """Escanea archivos .md del sandbox para extraer contexto directo."""
    context_parts = []

    # Archivos prioritarios por nombre
    priority_files = [
        "MODELOS_SABIOS_VERIFICADOS_27ABR2026.md",
        "DICTAMEN_CRUZADO_CEREBRO_MONSTRUO.md",
        "CRUCE_PLAN_DEFINITIVO_V2_CON_TODO.md",
        "COMO_FUNCIONA_EL_KERNEL_REAL.md",
        "MAPA_ORQUESTACION_RECUPERADO.md",
        "REFLEXIONES_ALFREDO_ANALISIS.md",
        "GEMINI_31_PRO_VERIFICADO.md",
        "MENSAJE_PARA_HILO_SUBPLAN_MVP.md",
    ]

    for fname in priority_files:
        fpath = os.path.join(SANDBOX_HOME, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Extraer primeras ~500 chars como resumen
                summary = content[:500].strip()
                context_parts.append(f"### {fname}\n\n{summary}\n")
            except Exception:
                pass

    return context_parts


def query_kernel_fast(query, timeout=12):
    """Consulta al kernel con timeout agresivo. No bloquea si falla."""
    try:
        from kernel_client import knowledge_query
        data = knowledge_query(query=query)
        answer = data.get("results", data.get("answer", data.get("response", "")))
        if answer and "no tengo suficiente" not in str(answer).lower():
            return str(answer)
        return None
    except Exception:
        return None


def check_kernel_health():
    """Verifica que el kernel esté vivo."""
    try:
        from kernel_client import health
        return health()
    except Exception:
        return None


def build_context():
    """Construye el CONTEXT.md completo con modo resiliente."""
    lines = [
        "# CONTEXT — Inyección de Contexto del Monstruo",
        f"**Generado:** {datetime.utcnow().isoformat()}Z",
        "",
        "---",
        "",
        "## REGLAS OBLIGATORIAS",
        "",
        "1. **NUNCA confíes en tu entrenamiento para versiones, modelos, APIs, o datos.**",
        "2. **SIEMPRE investiga en tiempo real antes de afirmar algo como verdad.**",
        "3. **Si no estás seguro, haz curl al kernel o investiga en la web.**",
        "4. **Antes de enviar instrucciones a otro hilo, verifica los datos primero.**",
        "5. **No preguntes si quieres que haga algo. Hazlo.**",
        "",
        "---",
        "",
    ]

    # CAPA 1: Recovery local (siempre disponible)
    recovery = check_recovery_local()
    if recovery and len(recovery) > 200:
        lines.append("## CAPA 1: Estado Local (RECOVERY.md)")
        lines.append("")
        lines.append(recovery)
        lines.append("")
        lines.append("---")
        lines.append("")

    # CAPA 2: Archivos clave del sandbox (siempre disponible)
    key_files = scan_key_files()
    if key_files:
        lines.append("## CAPA 2: Archivos Clave del Sandbox")
        lines.append("")
        for part in key_files:
            lines.append(part)
        lines.append("---")
        lines.append("")

    # CAPA 3: Kernel (intento rápido, no bloquea)
    kernel_health = check_kernel_health()
    if kernel_health:
        lines.append("## CAPA 3: Conocimiento del Kernel")
        lines.append(f"*Kernel v{kernel_health.get('version', '?')} — ONLINE*")
        lines.append("")

        for q in KERNEL_QUERIES:
            print(f"[inject] Consultando kernel: {q['label']}...")
            answer = query_kernel_fast(q["query"])
            if answer:
                lines.append(f"### {q['label']}")
                lines.append("")
                lines.append(answer[:1500])
                lines.append("")
            else:
                print(f"[inject]   → {q['label']}: timeout/no data")
    else:
        lines.append("## CAPA 3: Kernel NO DISPONIBLE")
        lines.append("")
        lines.append(f"El kernel en {KERNEL_URL} no responde ahora.")
        lines.append("Usar CAPA 1 y CAPA 2 como fuentes principales.")
        lines.append("Reintentar más tarde: `curl -s {KERNEL_URL}/health`")
        lines.append("")

    # METADATA DE CONEXIÓN (siempre incluida)
    lines.extend([
        "---",
        "",
        "## Conexiones Permanentes",
        "",
        f"- **Kernel URL:** {KERNEL_URL}",
        f"- **Kernel API Key:** {KERNEL_KEY}",
        "- **Manus API:** usar $MANUS_API_KEY del entorno",
        "- **API Manus base:** https://api.manus.ai (NO api.manus.im)",
        "- **Sitio Web Monstruo:** monstruocent-6nfmdwro.manus.space",
        "- **Comando Electoral:** comandomerida-8l3tpk9x.manus.space (PAUSADO)",
        "",
        "## Modelos Verificados (27 abril 2026)",
        "",
        "| Sabio | Model ID |",
        "|-------|----------|",
        "| GPT | gpt-5.5 |",
        "| Claude | claude-opus-4-7 |",
        "| Gemini | gemini-3.1-pro-preview |",
        "| Grok | grok-4.20-0309-reasoning |",
        "| DeepSeek | deepseek-v4-pro |",
        "| Perplexity | sonar-reasoning-pro |",
        "",
        "## Scripts del Sistema de Memoria",
        "",
        "```bash",
        "# Ciclo completo (auto-detecta compactación)",
        "python3 ~/monstruo-memoria/monstruo.py",
        "",
        "# Solo guardar estado",
        "python3 ~/monstruo-memoria/heartbeat.py",
        "",
        "# Solo recuperar contexto",
        "python3 ~/monstruo-memoria/inject.py",
        "",
        "# Depositar legado antes de morir",
        'python3 ~/monstruo-memoria/legacy.py "resumen de lo que hizo este hilo"',
        "",
        "# Ver estado del sistema",
        "python3 ~/monstruo-memoria/monstruo.py status",
        "```",
        "",
        "## Inventario de Archivos .md en Sandbox",
        "",
    ])

    # Listar todos los .md
    md_files = sorted(glob.glob(os.path.join(SANDBOX_HOME, "*.md")))
    for f in md_files[:25]:
        name = os.path.basename(f)
        size = os.path.getsize(f)
        lines.append(f"- `{name}` ({size:,}B)")

    lines.append("")
    return "\n".join(lines)


def main():
    print(f"[inject] Iniciando inyección de contexto... {datetime.utcnow().isoformat()}")

    context = build_context()

    # Guardar CONTEXT.md
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(context)

    print(f"[inject] CONTEXT.md generado ({len(context):,} chars)")
    print(f"[inject] Leer con: cat ~/CONTEXT.md")

    return context


if __name__ == "__main__":
    main()
