#!/usr/bin/env python3.11
"""
inject_context.py — Genera contexto dinámico según tipo de tarea.

Dado un tipo de tarea, genera el contexto mínimo necesario con:
- Proveedor recomendado
- Fallbacks
- Env vars requeridas
- Patrones de conexión
- Caveats

Uso:
    python3.11 inject_context.py --task-type "video_generation"
    python3.11 inject_context.py --task-type "web_research" --format json
    python3.11 inject_context.py --list-types
"""

import os
import json
import yaml
import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
REFERENCES_DIR = SKILL_DIR / "references"


# Mapeo de tipos de tarea a proveedores y contexto
TASK_ROUTING = {
    "planning": {
        "description": "Planificación, síntesis, diseño de estrategia",
        "primary": "openai",
        "fallbacks": ["anthropic", "xai"],
        "registry_file": "llm-registry.yaml",
        "notes": "GPT-5.4 es el mejor orquestador. Usar max_completion_tokens."
    },
    "long_analysis": {
        "description": "Análisis largo, crítica, revisión de documentos",
        "primary": "anthropic",
        "fallbacks": ["openai", "xai"],
        "registry_file": "llm-registry.yaml",
        "notes": "Claude Opus 4.6 con 1M de contexto. SDK nativo, NO OpenAI."
    },
    "multimodal": {
        "description": "Análisis de imágenes, video, audio + texto",
        "primary": "google",
        "fallbacks": ["openai"],
        "registry_file": "llm-registry.yaml",
        "notes": "Gemini 3.1 Pro es nativo multimodal."
    },
    "brainstorming": {
        "description": "Ideas creativas, ángulos no obvios, pensamiento lateral",
        "primary": "xai",
        "fallbacks": ["openai", "google"],
        "registry_file": "llm-registry.yaml",
        "notes": "Grok 4.20 con 2M de contexto. Modelo reasoning."
    },
    "technical_analysis": {
        "description": "Análisis técnico profundo, optimización, matemáticas",
        "primary": "deepseek",
        "fallbacks": ["google", "openai"],
        "registry_file": "llm-registry.yaml",
        "notes": "DeepSeek R1 via OpenRouter. Budget-friendly."
    },
    "web_research": {
        "description": "Búsqueda web en tiempo real, verificación de hechos",
        "primary": "perplexity",
        "fallbacks": ["google"],
        "registry_file": "llm-registry.yaml",
        "notes": "SOLO requests, PROHIBIDO SDK OpenAI. Citas verificables."
    },
    "video_avatar": {
        "description": "Videos con avatares AI realistas",
        "primary": "heygen",
        "fallbacks": ["atlas_cloud"],
        "registry_file": "media-apis.yaml",
        "notes": "HeyGen API v2. Header: X-Api-Key."
    },
    "voice_generation": {
        "description": "Text-to-speech, clonación de voz, dubbing",
        "primary": "elevenlabs",
        "fallbacks": [],
        "registry_file": "media-apis.yaml",
        "notes": "SDK: pip install elevenlabs. Multilingual v2."
    },
    "image_generation": {
        "description": "Generación de imágenes AI",
        "primary": "together_ai",
        "fallbacks": ["replicate", "novita_ai"],
        "registry_file": "media-apis.yaml",
        "notes": "FLUX state-of-art. Credencial en Notion."
    },
    "video_generation": {
        "description": "Generación de video AI (sin avatar)",
        "primary": "novita_ai",
        "fallbacks": ["atlas_cloud"],
        "registry_file": "media-apis.yaml",
        "notes": "Proxy a Kling v3, Minimax Hailuo, Seedance."
    },
    "3d_generation": {
        "description": "Generación de modelos 3D",
        "primary": "meshy_ai",
        "fallbacks": [],
        "registry_file": "media-apis.yaml",
        "notes": "Text-to-3D e Image-to-3D."
    },
    "virtual_tryon": {
        "description": "Virtual try-on de ropa",
        "primary": "fashn_ai",
        "fallbacks": ["replicate"],
        "registry_file": "media-apis.yaml",
        "notes": "Especializado en fashion e-commerce."
    },
    "email": {
        "description": "Enviar/leer emails",
        "primary": "gmail_mcp",
        "fallbacks": ["outlook_mcp"],
        "registry_file": "mcp-registry.yaml",
        "notes": "Usar MCP: manus-mcp-cli tool call <tool> --server gmail"
    },
    "task_management": {
        "description": "Gestión de tareas y proyectos",
        "primary": "asana_mcp",
        "fallbacks": [],
        "registry_file": "mcp-registry.yaml",
        "notes": "Usar MCP: manus-mcp-cli tool call <tool> --server asana"
    },
    "payments": {
        "description": "Procesamiento de pagos y facturación",
        "primary": "paypal_mcp",
        "fallbacks": ["stripe"],
        "registry_file": "payment-apis.yaml",
        "notes": "PayPal via MCP. Stripe en test mode (credencial en Notion)."
    },
    "deployment": {
        "description": "Deploy de aplicaciones web",
        "primary": "vercel",
        "fallbacks": ["cloudflare"],
        "registry_file": "infra-apis.yaml",
        "notes": "Vercel MCP disponible. Cloudflare via API token."
    },
    "database": {
        "description": "Operaciones de base de datos",
        "primary": "supabase",
        "fallbacks": [],
        "registry_file": "infra-apis.yaml",
        "notes": "Supabase MCP disponible. PostgreSQL + Auth + Storage."
    },
    "web_scraping": {
        "description": "Scraping web, extracción de datos de redes sociales",
        "primary": "apify",
        "fallbacks": [],
        "registry_file": "data-apis.yaml",
        "notes": "Plan Scale. Scraping Facebook/Instagram. Credencial en Notion."
    },
    "social_listening": {
        "description": "Monitoreo de menciones, sentiment analysis, brand monitoring",
        "primary": "brandmentions",
        "fallbacks": ["mentionlytics"],
        "registry_file": "data-apis.yaml",
        "notes": "BrandMentions Plan Expert $499/mes. Endpoint: api.brandmentions.com/v1/mentions. Credencial en Notion."
    },
    "sabios_consultation": {
        "description": "Consulta al Consejo de 6 Sabios",
        "primary": "consulta-sabios",
        "fallbacks": [],
        "registry_file": "skills-registry.yaml",
        "notes": "Usar skill consulta-sabios. Leer semilla v7.3 primero."
    },
}


def load_registry(filename: str) -> dict:
    """Carga un archivo de registro YAML."""
    filepath = REFERENCES_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def get_provider_details(provider_id: str, registry: dict) -> dict:
    """Obtiene detalles de un proveedor del registro."""
    providers = registry.get("providers", registry.get("servers", registry.get("skills", {})))
    return providers.get(provider_id, {})


def check_env_available(env_var: str) -> bool:
    """Verifica si una variable de entorno está disponible."""
    return bool(os.environ.get(env_var, ""))


def inject_context(task_type: str, format_type: str = "markdown") -> str:
    """Genera contexto para un tipo de tarea."""
    if task_type not in TASK_ROUTING:
        return f"Tipo de tarea desconocido: {task_type}\nTipos disponibles: {', '.join(TASK_ROUTING.keys())}"
    
    route = TASK_ROUTING[task_type]
    registry = load_registry(route["registry_file"])
    primary = get_provider_details(route["primary"], registry)
    
    # Verificar disponibilidad de credenciales
    env_var = primary.get("auth", {}).get("env_var", "")
    env_available = check_env_available(env_var) if env_var else False
    
    context = {
        "task_type": task_type,
        "description": route["description"],
        "recommended_provider": {
            "id": route["primary"],
            "name": primary.get("name", route["primary"]),
            "model_id": primary.get("model_id", "N/A"),
            "env_var": env_var,
            "env_available": env_available,
            "env_source": "sandbox" if env_available else primary.get("auth", {}).get("env_var_source", "unknown"),
        },
        "fallbacks": route["fallbacks"],
        "notes": route["notes"],
        "anti_errors": primary.get("anti_errors", []),
    }
    
    if format_type == "json":
        return json.dumps(context, indent=2, ensure_ascii=False)
    
    # Markdown format
    lines = [
        f"## Contexto para: {route['description']}",
        f"",
        f"**Proveedor recomendado:** {context['recommended_provider']['name']}",
        f"**Model ID:** {context['recommended_provider']['model_id']}",
        f"**Env Var:** `{env_var}`" + (" ✅" if env_available else " ❌ (consultar Notion)"),
        f"**Fallbacks:** {', '.join(route['fallbacks']) if route['fallbacks'] else 'Ninguno'}",
        f"",
        f"**Notas:** {route['notes']}",
    ]
    
    if context["anti_errors"]:
        lines.append("")
        lines.append("**Anti-errores:**")
        for err in context["anti_errors"]:
            lines.append(f"- {err}")
    
    return "\n".join(lines)


def list_types():
    """Lista todos los tipos de tarea disponibles."""
    print("\nTipos de tarea disponibles:")
    print("-" * 60)
    for task_type, route in TASK_ROUTING.items():
        print(f"  {task_type:25s} → {route['primary']:15s} | {route['description']}")
    print("-" * 60)
    print(f"\nTotal: {len(TASK_ROUTING)} tipos")


def main():
    parser = argparse.ArgumentParser(description="Genera contexto dinámico por tipo de tarea")
    parser.add_argument("--task-type", help="Tipo de tarea")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--list-types", action="store_true", help="Listar tipos disponibles")
    args = parser.parse_args()
    
    if args.list_types:
        list_types()
        return
    
    if not args.task_type:
        parser.error("Se requiere --task-type o --list-types")
    
    result = inject_context(args.task_type, args.format)
    print(result)


if __name__ == "__main__":
    main()
