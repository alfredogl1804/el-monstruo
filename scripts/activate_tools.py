"""
El Monstruo — El Despertador (Sprint 81 prep)
==============================================
Despierta las tools dormidas: las que viven en `kernel/tool_dispatch.py`
como ToolSpec pero no están registradas en la tabla `tool_registry` de
Supabase, ni tienen `binding` activo en `tool_bindings`.

Diseño:
    - Lee las 16 ToolSpecs canónicas de kernel.tool_dispatch.get_tool_specs()
    - Compara contra el estado real en Supabase (tool_registry + tool_bindings)
    - Decide por cada tool: ya_activa | despertar | pendiente_credencial | omitir
    - En modo --apply: ejecuta upsert en tool_registry y tool_bindings
    - En modo --dry-run (default): solo imprime el plan, no toca DB
    - Aplica Brand Compliance Checklist al output

Uso:
    python3 scripts/activate_tools.py            # dry-run, imprime plan
    python3 scripts/activate_tools.py --apply    # ejecuta, requiere confirmación
    python3 scripts/activate_tools.py --json     # output JSON para Command Center
    python3 scripts/activate_tools.py --tenant alfredo --apply

Soberanía (Obj #12):
    Si Supabase no está disponible, el script imprime el SQL equivalente
    para ejecución manual via psql o el SQL Editor de Supabase. El sistema
    no depende del script para activar tools — el script es ergonomía.

Fail-closed (Obj #11):
    --apply requiere confirmación interactiva ("ACTIVAR" en mayúsculas).
    Tools con riesgo HIGH o requires_hitl=True NUNCA se activan en modo
    auto — el operador debe intervenir manualmente.

Sprint 81 prep — 2026-05-02
Autor: Hilo B (Cowork)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

# Asegurar que la raíz del repo esté en el path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


# ─── Excepciones con identidad ─────────────────────────────────────────

class DespertadorDbNoDisponible(RuntimeError):
    """No se pudo conectar a Supabase para escribir el registro de tools.

    Causa: SUPABASE_URL/SUPABASE_SERVICE_KEY ausentes o conexión rechazada.
    Sugerencia: Verificar variables de entorno, o usar --print-sql para
    obtener el SQL equivalente y ejecutarlo manualmente.
    """


class DespertadorToolNoCodeada(ValueError):
    """Se intentó activar una tool que no existe como ToolSpec.

    Causa: El nombre solicitado no aparece en tool_dispatch.get_tool_specs().
    Sugerencia: Usar `--list` para ver el inventario disponible.
    """


class DespertadorCredencialFaltante(RuntimeError):
    """La tool requiere una variable de entorno que no está definida.

    Causa: secret_env_var apunta a una variable ausente del entorno.
    Sugerencia: Definir la variable en Railway o configurar la tool como
    pendiente_credencial hasta que se aprovisione.
    """


# ─── Inventario canónico ───────────────────────────────────────────────

# Mapa de tool → metadata para registry + bindings.
# Fuente de verdad: kernel/tool_dispatch.py (ToolSpecs) cruzado con
# scripts/005_adr_tool_broker_tables.sql (secret_env_var pre-poblados).
INVENTARIO_CANONICO: dict[str, dict] = {
    "web_search": {
        "display_name": "Búsqueda Web (Sonar)",
        "category": "awareness",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": "SONAR_API_KEY",
        "description": "Búsqueda web en tiempo real vía Perplexity Sonar.",
    },
    "consult_sabios": {
        "display_name": "Consejo de los Sabios",
        "category": "awareness",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": None,  # Usa router multi-modelo
        "description": "Consulta paralela a 6 modelos para análisis multi-perspectiva.",
    },
    "start_cidp_research": {
        "display_name": "Iniciar Ciclo CIDP",
        "category": "autonomy",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "CIDP_SERVICE_URL",
        "description": "Lanza ciclo de investigación profunda multi-iteración.",
    },
    "check_cidp_status": {
        "display_name": "Estado de Ciclo CIDP",
        "category": "awareness",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": "CIDP_SERVICE_URL",
        "description": "Consulta progreso de un ciclo CIDP en marcha.",
    },
    "cancel_cidp_research": {
        "display_name": "Cancelar Ciclo CIDP",
        "category": "orchestration",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "CIDP_SERVICE_URL",
        "description": "Detiene un ciclo CIDP activo y libera recursos.",
    },
    "call_webhook": {
        "display_name": "Webhook Externo",
        "category": "orchestration",
        "risk_level": "HIGH",
        "requires_hitl": True,  # Siempre humano-en-el-loop por seguridad
        "secret_env_var": None,
        "description": "Dispara webhook HTTPS contra dominio whitelisted.",
    },
    "github": {
        "display_name": "GitHub (Forja Externa)",
        "category": "write",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "GITHUB_TOKEN",
        "description": "Operaciones sobre repos: search, issues, PRs, commits.",
    },
    "notion": {
        "display_name": "Notion (Memoria Compartida)",
        "category": "write",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "NOTION_TOKEN",
        "description": "Lectura/escritura de páginas y bases de datos en Notion.",
    },
    "delegate_task": {
        "display_name": "Delegación a Roles",
        "category": "orchestration",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": None,  # Usa router interno
        "description": "Delega sub-tarea a rol especializado (estratega, crítico, etc.).",
    },
    "schedule_task": {
        "display_name": "Programador de Tareas",
        "category": "autonomy",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": None,  # Usa DB
        "description": "Agenda ejecución autónoma futura (hasta 30 días).",
    },
    "user_dossier": {
        "display_name": "Dossier del Usuario",
        "category": "awareness",
        "risk_level": "MEDIUM",
        # HITL=True heredado de migración 004 (línea 127). Defensivo por diseño:
        # las acciones update_dossier/create_mission/update_mission mutan estado
        # persistente del usuario. El flag aplica al tool completo, no por acción.
        # Para permitir get_dossier sin HITL habría que dividir en dos tools.
        "requires_hitl": True,
        "secret_env_var": None,  # Usa DB
        "description": "Lectura/actualización del perfil persistente del usuario.",
    },
    "browse_web": {
        "display_name": "Navegador (Cloudflare)",
        "category": "awareness",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": "CLOUDFLARE_API_TOKEN",
        "description": "Render JS + extracción markdown vía Cloudflare Browser Run.",
    },
    "code_exec": {
        "display_name": "Sandbox de Código (E2B)",
        "category": "orchestration",
        "risk_level": "LOW",  # E2B es la frontera de seguridad
        "requires_hitl": False,
        "secret_env_var": "E2B_API_KEY",
        "description": "Ejecuta Python/shell en sandbox aislado E2B.",
    },
    "email": {
        "display_name": "Correo Saliente",
        "category": "write",
        # HIGH+HITL heredado de migración 004 (línea 126). Postura defensiva:
        # enviar correo al exterior puede facilitar suplantación o spam si el
        # LLM se equivoca de destinatario. El humano aprueba cada envío.
        "risk_level": "HIGH",
        "requires_hitl": True,
        "secret_env_var": "GMAIL_APP_PASSWORD",
        "description": "Envío de email vía Gmail SMTP.",
    },
    "wide_research": {
        "display_name": "Investigación Amplia (Swarm)",
        "category": "awareness",
        "risk_level": "LOW",
        "requires_hitl": False,
        "secret_env_var": None,  # Usa web_search internamente
        "description": "Hasta 10 sub-agentes paralelos (Kimi K2.6 Swarm).",
    },
    "manus_bridge": {
        "display_name": "Puente a Manus",
        "category": "orchestration",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "MANUS_API_KEY",
        "description": "Delega tareas complejas a agentes Manus (5/hora).",
    },
    # ── Sprint 84 Bloque 1 ──
    "deploy_to_github_pages": {
        "display_name": "Deploy a GitHub Pages (Forja Pública)",
        "category": "write",
        "risk_level": "MEDIUM",
        # Auto-aprobado: el repo público nuevo es reversible (delete repo) y
        # GitHub mismo es el gate de auditoría (commits firmados, historial).
        "requires_hitl": False,
        "secret_env_var": "GITHUB_TOKEN",
        "description": "Publica sitio estático (HTML/CSS/JS) end-to-end a GitHub Pages.",
    },
    # ── Sprint 84 Bloque 2 ──
    "deploy_to_railway": {
        "display_name": "Deploy a Railway (Forja Backend)",
        "category": "write",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "RAILWAY_API_TOKEN",
        "description": "Crea proyecto Railway desde repo GitHub y despliega backend.",
    },
    "deploy_app": {
        "display_name": "Deploy App (Magna decide)",
        "category": "write",
        "risk_level": "MEDIUM",
        "requires_hitl": False,
        "secret_env_var": "GITHUB_TOKEN",  # Railway opcional, GitHub siempre requerido
        "description": "Wrapper unificado: Magna decide entre GitHub Pages y Railway.",
    },
}


# ─── Brand Compliance ──────────────────────────────────────────────────

PROHIBIDOS_NAMING = ("service", "handler", "utils", "helper", "misc")


def validar_nombre_tool(tool_name: str) -> tuple[bool, list[str]]:
    """Brand DNA: nombres con identidad. Sin genéricos."""
    issues: list[str] = []
    bajo = tool_name.lower()
    for f in PROHIBIDOS_NAMING:
        if f in bajo:
            issues.append(f"Nombre prohibido '{f}' en tool '{tool_name}'")
    if not bajo.replace("_", "").isalnum():
        issues.append(f"Tool '{tool_name}' tiene caracteres no permitidos")
    return (len(issues) == 0, issues)


# ─── Tipos de decisión ─────────────────────────────────────────────────

@dataclass
class DecisionTool:
    tool_name: str
    estado_anterior: str  # ausente | inactiva | activa | sin_binding
    estado_objetivo: str  # activa | pendiente_credencial | requiere_hitl_manual | omitir
    razon: str
    secret_env_var: Optional[str]
    secret_disponible: bool
    risk_level: str
    requires_hitl: bool
    brand_issues: list[str] = field(default_factory=list)


# ─── Lógica principal ──────────────────────────────────────────────────

async def _cargar_estado_db(db) -> tuple[dict[str, dict], dict[str, dict]]:
    """Carga estado actual de tool_registry y tool_bindings."""
    registry_rows = await db.select("tool_registry", columns="*")
    bindings_rows = await db.select("tool_bindings", columns="*")

    registry = {r["tool_name"]: r for r in (registry_rows or [])}
    bindings = {(b["tenant_id"], b["tool_name"]): b for b in (bindings_rows or [])}
    return registry, bindings


def _decidir(
    tool_name: str,
    spec_meta: dict,
    registry_actual: dict[str, dict],
    bindings_actual: dict,
    tenant: str,
) -> DecisionTool:
    """Decide qué hacer con una tool dada su metadata canónica y el estado real."""
    # Brand check
    ok_naming, brand_issues = validar_nombre_tool(tool_name)

    # Estado anterior
    en_registry = tool_name in registry_actual
    activa_en_registry = en_registry and registry_actual[tool_name].get("is_active", False)
    binding_key = (tenant, tool_name)
    tiene_binding = binding_key in bindings_actual and bindings_actual[binding_key].get("is_enabled", False)

    if not en_registry:
        estado_anterior = "ausente"
    elif not activa_en_registry:
        estado_anterior = "inactiva"
    elif not tiene_binding:
        estado_anterior = "sin_binding"
    else:
        estado_anterior = "activa"

    # ¿Credencial disponible?
    secret_var = spec_meta.get("secret_env_var")
    secret_disponible = (secret_var is None) or bool(os.environ.get(secret_var))

    # Decisión de objetivo
    if estado_anterior == "activa":
        objetivo = "activa"
        razon = "Ya activa con binding — sin acción requerida."
    elif spec_meta.get("requires_hitl"):
        objetivo = "requiere_hitl_manual"
        razon = (
            f"Riesgo {spec_meta['risk_level']} con requires_hitl=True. "
            "Activación manual requerida — no se auto-despierta."
        )
    elif not secret_disponible:
        objetivo = "pendiente_credencial"
        razon = f"Falta variable de entorno '{secret_var}' — registrar como inactiva."
    else:
        objetivo = "activa"
        razon = "Credenciales presentes — despertar y crear binding."

    return DecisionTool(
        tool_name=tool_name,
        estado_anterior=estado_anterior,
        estado_objetivo=objetivo,
        razon=razon,
        secret_env_var=secret_var,
        secret_disponible=secret_disponible,
        risk_level=spec_meta["risk_level"],
        requires_hitl=spec_meta["requires_hitl"],
        brand_issues=brand_issues,
    )


async def _aplicar_decision(db, decision: DecisionTool, tenant: str) -> dict:
    """Ejecuta upsert en tool_registry + tool_bindings según decisión."""
    spec_meta = INVENTARIO_CANONICO[decision.tool_name]
    is_active = decision.estado_objetivo == "activa"

    # Upsert tool_registry
    registry_data = {
        "tool_name": decision.tool_name,
        "display_name": spec_meta["display_name"],
        "category": spec_meta["category"],
        "description": spec_meta["description"],
        "risk_level": spec_meta["risk_level"],
        "requires_hitl": spec_meta["requires_hitl"],
        "secret_env_var": spec_meta["secret_env_var"],
        "is_active": is_active,
        "metadata": {
            "sprint_added": "10",
            "despertado_por": "scripts/activate_tools.py",
            "despertado_at": datetime.now(timezone.utc).isoformat(),
            "razon": decision.razon,
        },
    }
    await db.upsert("tool_registry", data=registry_data, on_conflict="tool_name")

    # Upsert tool_bindings (solo si va a quedar activa)
    if is_active:
        binding_data = {
            "tenant_id": tenant,
            "tool_name": decision.tool_name,
            "is_enabled": True,
            "rate_limit": 100,
        }
        await db.upsert(
            "tool_bindings",
            data=binding_data,
            on_conflict="tenant_id,tool_name",
        )

    return {
        "tool": decision.tool_name,
        "registry_active": is_active,
        "binding_creado": is_active,
    }


def _imprimir_plan(decisiones: list[DecisionTool], modo: str) -> None:
    """Tabla legible para humanos. Identidad de marca en el formato."""
    print(f"\n╔══ EL DESPERTADOR — Plan ({modo}) ══════════════════════════")
    print(f"║ Tenant: {os.environ.get('MONSTRUO_TENANT', 'alfredo')}")
    print(f"║ Generado: {datetime.now(timezone.utc).isoformat()}")
    print(f"║ Tools en inventario canónico: {len(INVENTARIO_CANONICO)}")
    print("╚════════════════════════════════════════════════════════════\n")

    headers = ("tool", "anterior", "objetivo", "riesgo", "razón")
    rows = [
        (
            d.tool_name,
            d.estado_anterior,
            d.estado_objetivo,
            d.risk_level,
            d.razon[:60] + ("…" if len(d.razon) > 60 else ""),
        )
        for d in decisiones
    ]
    widths = [max(len(str(r[i])) for r in (rows + [headers])) for i in range(len(headers))]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("─" * w for w in widths)))
    for r in rows:
        print(fmt.format(*r))

    # Resumen
    por_objetivo: dict[str, int] = {}
    for d in decisiones:
        por_objetivo[d.estado_objetivo] = por_objetivo.get(d.estado_objetivo, 0) + 1
    print("\nResumen:")
    for k, v in sorted(por_objetivo.items()):
        print(f"  • {k}: {v}")

    # Brand compliance
    issues = [(d.tool_name, d.brand_issues) for d in decisiones if d.brand_issues]
    if issues:
        print("\n⚠ Brand Compliance Issues:")
        for nombre, lst in issues:
            for i in lst:
                print(f"  • {nombre}: {i}")
    else:
        print("\n✓ Brand Compliance: todos los nombres cumplen.")


def _imprimir_sql_equivalente(decisiones: list[DecisionTool], tenant: str) -> None:
    """Output SQL para ejecución manual cuando Supabase no esté disponible (Obj #12)."""
    print("-- ═══ SQL Equivalente (ejecutar en Supabase SQL Editor) ═══")
    for d in decisiones:
        if d.estado_objetivo not in ("activa", "pendiente_credencial"):
            continue
        spec = INVENTARIO_CANONICO[d.tool_name]
        is_active = "TRUE" if d.estado_objetivo == "activa" else "FALSE"
        secret = f"'{spec['secret_env_var']}'" if spec["secret_env_var"] else "NULL"
        print(f"""
-- {d.tool_name}: {d.razon}
INSERT INTO tool_registry (tool_name, display_name, category, description,
    risk_level, requires_hitl, is_active, secret_env_var)
VALUES ('{d.tool_name}', '{spec["display_name"]}', '{spec["category"]}',
    '{spec["description"]}', '{spec["risk_level"]}',
    {"TRUE" if spec["requires_hitl"] else "FALSE"}, {is_active}, {secret})
ON CONFLICT (tool_name) DO UPDATE SET
    is_active = EXCLUDED.is_active,
    secret_env_var = EXCLUDED.secret_env_var,
    updated_at = NOW();""")
        if d.estado_objetivo == "activa":
            print(f"""INSERT INTO tool_bindings (tenant_id, tool_name, is_enabled, rate_limit)
VALUES ('{tenant}', '{d.tool_name}', TRUE, 100)
ON CONFLICT (tenant_id, tool_name) DO UPDATE SET
    is_enabled = TRUE,
    updated_at = NOW();""")


# ─── Entrypoint ────────────────────────────────────────────────────────

async def main_async(args) -> int:
    # Importar las ToolSpecs reales
    try:
        from kernel.tool_dispatch import get_tool_specs
        specs = get_tool_specs()
    except Exception as e:
        print(f"despertador_specs_no_cargadas: {e}", file=sys.stderr)
        return 2

    # Validar que el inventario canónico cubre todas las ToolSpecs
    nombres_specs = {s.name for s in specs}
    nombres_canon = set(INVENTARIO_CANONICO.keys())
    faltantes = nombres_specs - nombres_canon
    sobrantes = nombres_canon - nombres_specs
    if faltantes:
        print(
            f"despertador_inventario_desincronizado: ToolSpecs sin "
            f"metadata canónica: {sorted(faltantes)}",
            file=sys.stderr,
        )
        return 3
    if sobrantes:
        print(
            f"⚠ Inventario tiene metadata para tools no presentes en "
            f"tool_dispatch.get_tool_specs(): {sorted(sobrantes)}",
            file=sys.stderr,
        )

    # Conectar a DB (opcional — en --print-sql no se requiere)
    db = None
    registry_actual: dict[str, dict] = {}
    bindings_actual: dict = {}
    if not args.print_sql:
        try:
            from kernel.memory.supabase_client import SupabaseClient
            db = SupabaseClient()
            await db.connect()
            if not db.connected:
                raise DespertadorDbNoDisponible(
                    "SupabaseClient.connect() retornó connected=False"
                )
            registry_actual, bindings_actual = await _cargar_estado_db(db)
        except Exception as e:
            print(
                f"despertador_db_no_disponible: {e}\n"
                "  Sugerencia: usa --print-sql para obtener el SQL "
                "equivalente y ejecutarlo manualmente.",
                file=sys.stderr,
            )
            return 4

    # Generar decisiones
    decisiones: list[DecisionTool] = []
    for spec in specs:
        meta = INVENTARIO_CANONICO[spec.name]
        d = _decidir(spec.name, meta, registry_actual, bindings_actual, args.tenant)
        decisiones.append(d)

    # Output
    if args.json:
        print(json.dumps([asdict(d) for d in decisiones], indent=2, ensure_ascii=False))
        return 0
    if args.print_sql:
        _imprimir_sql_equivalente(decisiones, args.tenant)
        return 0

    modo = "APLICAR" if args.apply else "DRY-RUN"
    _imprimir_plan(decisiones, modo)

    if not args.apply:
        print("\n→ Modo dry-run. Para ejecutar: --apply")
        return 0

    # Confirmación interactiva
    print("\n⚠ Modo --apply: se modificará la tabla tool_registry y tool_bindings.")
    confirmacion = input("Escribe ACTIVAR para proceder (cualquier otra cosa cancela): ").strip()
    if confirmacion != "ACTIVAR":
        print("despertador_cancelado_por_operador")
        return 1

    # Aplicar
    resultados: list[dict] = []
    for d in decisiones:
        if d.estado_objetivo in ("requiere_hitl_manual", "omitir"):
            continue
        try:
            r = await _aplicar_decision(db, d, args.tenant)
            resultados.append(r)
            print(f"  ✓ {d.tool_name}: {d.estado_objetivo}")
        except Exception as e:
            print(f"  ✗ despertador_aplicacion_fallida: {d.tool_name} — {e}", file=sys.stderr)

    print(f"\n✓ Aplicado. Cambios: {len(resultados)}/{len(decisiones)}")
    print("  Verificar: curl ${KERNEL_BASE_URL}/v1/tools")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="El Despertador — activa tools dormidas en El Monstruo",
    )
    parser.add_argument("--apply", action="store_true",
                        help="Ejecuta cambios. Sin esto, dry-run.")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON para consumo del Command Center.")
    parser.add_argument("--print-sql", action="store_true",
                        help="Imprime SQL equivalente (no requiere DB).")
    parser.add_argument("--tenant", default=os.environ.get("MONSTRUO_TENANT", "alfredo"),
                        help="Tenant para tool_bindings. Default: alfredo")
    parser.add_argument("--list", action="store_true",
                        help="Lista el inventario canónico y sale.")
    args = parser.parse_args()

    if args.list:
        for name, meta in sorted(INVENTARIO_CANONICO.items()):
            print(f"{name:25s} {meta['risk_level']:7s} {meta['category']:14s} "
                  f"{meta['secret_env_var'] or '-'}")
        return 0

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
