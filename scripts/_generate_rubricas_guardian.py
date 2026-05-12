"""
Generador de las 15 rubricas YAML del Guardian (Sprint GUARDIAN-AUTONOMO-001 T2).

Crea ``kernel/guardian_runner/rubricas/objetivo_NN.yaml`` con evidencias y
thresholds canonicos para cada Objetivo Maestro.

Diseno anti-Goodhart (spec §10):
- Las metricas son medibles via SQL/filesystem/git, NO LLM judges.
- Cada objetivo tiene 3-5 evidencias, cada una con weight, threshold y type.
- Score_pct = sum(weight si passed) / sum(all weights) * 100.
- Falsadores explicitos: thresholds inferiores que dispararian critical.

Run:
    python3 generate_rubricas.py <output_dir>
"""

from __future__ import annotations

import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────
#  Las 15 rubricas en forma declarativa
# ─────────────────────────────────────────────────────────────────────────

RUBRICAS = {
    1: {
        "objective_name": "Crear Empresas Digitales Completas",
        "rubrica_version": "1.0.0",
        "description": "Pipeline activo de empresas digitales generadas por El Monstruo.",
        "evidence": {
            "embriones_activos": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM embrion_memoria WHERE created_at > NOW() - INTERVAL '7 days';",
                "threshold_min": 10,
                "weight": 2.0,
            },
            "tablas_supabase_activas": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';",
                "threshold_min": 20,
                "weight": 1.5,
            },
            "kernel_modules": {
                "type": "filesystem",
                "pattern": "kernel/*.py",
                "operation": "count_files",
                "threshold_min": 15,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    2: {
        "objective_name": "Nivel Apple/Tesla",
        "rubrica_version": "1.0.0",
        "description": "Calidad premium de output: tests pasando, cobertura, DSCs firmados.",
        "evidence": {
            "dscs_firmados": {
                "type": "filesystem",
                "pattern": "discovery_forense/CAPILLA_DECISIONES/**/DSC-*.md",
                "operation": "count_files",
                "threshold_min": 30,
                "weight": 2.0,
            },
            "tests_existentes": {
                "type": "filesystem",
                "pattern": "tests/**/test_*.py",
                "operation": "count_files",
                "threshold_min": 50,
                "weight": 1.5,
            },
            "sprints_completados": {
                "type": "filesystem",
                "pattern": "bridge/sprints_completados/*.md",
                "operation": "count_files",
                "threshold_min": 5,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 30, "critical_below": 55, "warning_below": 80},
    },
    3: {
        "objective_name": "Maximo Poder, Minima Complejidad",
        "rubrica_version": "1.0.0",
        "description": "Modulos kernel pequenios y reutilizables. Cero archivos genericos.",
        "evidence": {
            "archivos_genericos_zero": {
                "type": "filesystem",
                "pattern": "kernel/**/handler.py",
                "operation": "count_files",
                "threshold_max": 0,
                "weight": 2.0,
            },
            "archivos_misc_zero": {
                "type": "filesystem",
                "pattern": "kernel/**/misc.py",
                "operation": "count_files",
                "threshold_max": 0,
                "weight": 2.0,
            },
            "archivos_utils_limited": {
                "type": "filesystem",
                "pattern": "kernel/**/utils.py",
                "operation": "count_files",
                "threshold_max": 1,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 20, "critical_below": 50, "warning_below": 80},
    },
    4: {
        "objective_name": "Nunca se Equivoca Dos Veces",
        "rubrica_version": "1.0.0",
        "description": "error_memory poblado y patrones registrados.",
        "evidence": {
            "error_memory_rows": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM error_memory;",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "incidentes_documentados": {
                "type": "filesystem",
                "pattern": "discovery_forense/INCIDENTES/*.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    5: {
        "objective_name": "Gasolina Magna vs Premium",
        "rubrica_version": "1.0.0",
        "description": "Cost tracking activo: run_costs persiste consumo.",
        "evidence": {
            "run_costs_rows_30d": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM run_costs WHERE created_at > NOW() - INTERVAL '30 days';",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "cost_history_tracked": {
                "type": "filesystem",
                "pattern": "kernel/cost_history.py",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    6: {
        "objective_name": "Vanguardia Perpetua",
        "rubrica_version": "1.0.0",
        "description": "Anti-autoboicot, validacion en tiempo real, ciclo de descubrimiento.",
        "evidence": {
            "skill_validacion_tiempo_real": {
                "type": "filesystem",
                "pattern": "skills/validacion-tiempo-real/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.5,
            },
            "anti_autoboicot_active": {
                "type": "filesystem",
                "pattern": "skills/anti-autoboicot/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.5,
            },
            "ciclo_descubrimiento": {
                "type": "filesystem",
                "pattern": "skills/ciclo-investigacion-descubrimiento-perpetuo/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 30, "critical_below": 55, "warning_below": 80},
    },
    7: {
        "objective_name": "No Inventar la Rueda",
        "rubrica_version": "1.0.0",
        "description": "Skills reutilizadas, api-context-injector activo.",
        "evidence": {
            "api_context_injector_skill": {
                "type": "filesystem",
                "pattern": "skills/api-context-injector/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "skills_total": {
                "type": "filesystem",
                "pattern": "skills/*/SKILL.md",
                "operation": "count_files",
                "threshold_min": 10,
                "weight": 1.5,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    8: {
        "objective_name": "Inteligencia Emergente Colectiva",
        "rubrica_version": "1.0.0",
        "description": "Consulta a sabios activa, enjambre operativo.",
        "evidence": {
            "consulta_sabios_skill": {
                "type": "filesystem",
                "pattern": "skills/consulta-sabios/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "perplexity_active": {
                "type": "filesystem",
                "pattern": "kernel/perplexity*.py",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.5,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    9: {
        "objective_name": "Transversalidad Total",
        "rubrica_version": "1.0.0",
        "description": "Las 7 capas transversales activas: Ventas, SEO, Pub, Tendencias, Ops, Finanzas, Resiliencia.",
        "evidence": {
            "capas_transversales_documentadas": {
                "type": "filesystem",
                "pattern": "AGENTS.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "bridge_completados": {
                "type": "filesystem",
                "pattern": "bridge/sprints_completados/*.md",
                "operation": "count_files",
                "threshold_min": 3,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    10: {
        "objective_name": "Simulador Predictivo",
        "rubrica_version": "1.0.0",
        "description": "Skill simulador-escenarios-ia disponible, ABM+Monte Carlo activos.",
        "evidence": {
            "simulador_skill": {
                "type": "filesystem",
                "pattern": "skills/simulador-escenarios-ia/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 2.0,
            },
        },
        "status_thresholds": {"emergency_below": 30, "critical_below": 60, "warning_below": 85},
    },
    11: {
        "objective_name": "Multiplicacion de Embriones",
        "rubrica_version": "1.0.0",
        "description": "Embriones ejecutandose y dejando huella en embrion_memoria.",
        "evidence": {
            "embriones_24h": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM embrion_memoria WHERE created_at > NOW() - INTERVAL '24 hours';",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "embriones_modulo_brand": {
                "type": "filesystem",
                "pattern": "kernel/embriones/brand_engine/brand_engine.py",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.0,
            },
            "embriones_loop_existe": {
                "type": "filesystem",
                "pattern": "kernel/embrion_loop.py",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.5,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    12: {
        "objective_name": "Ecosistema de Monstruos",
        "rubrica_version": "1.0.0",
        "description": "Bridge inter-cuenta operativo y hilos en colaboracion.",
        "evidence": {
            "bridge_skill": {
                "type": "filesystem",
                "pattern": "skills/manus-inter-cuenta/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "bridge_documentos": {
                "type": "filesystem",
                "pattern": "bridge/*.md",
                "operation": "count_files",
                "threshold_min": 5,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
    13: {
        "objective_name": "Del Mundo (i18n)",
        "rubrica_version": "1.0.0",
        "description": "Soporte multi-idioma. Por ahora declarativo, expansion gradual.",
        "evidence": {
            "agents_md_spanish": {
                "type": "filesystem",
                "pattern": "AGENTS.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 30, "critical_below": 60, "warning_below": 85},
    },
    14: {
        "objective_name": "El Guardian",
        "rubrica_version": "1.0.0",
        "description": "Guardian existe, scheduler activo, audit_log poblandose.",
        "evidence": {
            "guardian_module": {
                "type": "filesystem",
                "pattern": "kernel/guardian.py",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 2.0,
            },
            "scheduler_module": {
                "type": "filesystem",
                "pattern": "kernel/embrion_scheduler.py",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.5,
            },
            "audit_log_table_exists": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='guardian_audit_log';",
                "threshold_min": 1,
                "weight": 1.5,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 80},
    },
    15: {
        "objective_name": "Memoria Soberana",
        "rubrica_version": "1.0.0",
        "description": "embrion_memoria persiste eventos clave, no se pierde contexto entre hilos.",
        "evidence": {
            "embrion_memoria_total": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM embrion_memoria;",
                "threshold_min": 100,
                "weight": 2.0,
            },
            "embrion_memoria_recent": {
                "type": "sql",
                "query": "SELECT COUNT(*) FROM embrion_memoria WHERE created_at > NOW() - INTERVAL '7 days';",
                "threshold_min": 10,
                "weight": 1.5,
            },
            "memento_protocol_active": {
                "type": "filesystem",
                "pattern": "skills/el-monstruo*/SKILL.md",
                "operation": "count_files",
                "threshold_min": 1,
                "weight": 1.0,
            },
        },
        "status_thresholds": {"emergency_below": 25, "critical_below": 50, "warning_below": 75},
    },
}


def render_yaml(obj_id: int, data: dict) -> str:
    """Renderizar una rubrica como YAML (sin libreria, formato canonico)."""
    lines = [
        "# Rubrica Guardian de los Objetivos",
        "# Sprint: GUARDIAN-AUTONOMO-001 (T2)",
        f"# Objetivo Maestro #{obj_id}: {data['objective_name']}",
        "# Owner: Hilo Ejecutor 2 (manus_hilo_b)",
        "# DSC enforzados: DSC-G-008 v2 (rubrica + evidencia + falsadores), DSC-G-017",
        "",
        f"objective_id: {obj_id}",
        f'objective_name: "{data["objective_name"]}"',
        f'rubrica_version: "{data["rubrica_version"]}"',
        f'description: "{data["description"]}"',
        "",
        "evidence:",
    ]

    for metric_key, spec in data["evidence"].items():
        lines.append(f"  {metric_key}:")
        for k, v in spec.items():
            if isinstance(v, str):
                if "\n" in v or '"' in v:
                    lines.append(f"    {k}: |")
                    for sub in v.splitlines():
                        lines.append(f"      {sub}")
                else:
                    lines.append(f'    {k}: "{v}"')
            elif isinstance(v, bool):
                lines.append(f"    {k}: {str(v).lower()}")
            else:
                lines.append(f"    {k}: {v}")

    lines.extend(["", "status_thresholds:"])
    for k, v in data["status_thresholds"].items():
        lines.append(f"  {k}: {v}")

    lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("usage: generate_rubricas.py <output_dir>", file=sys.stderr)
        sys.exit(2)

    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    for obj_id, data in RUBRICAS.items():
        path = out / f"objetivo_{obj_id:02d}.yaml"
        path.write_text(render_yaml(obj_id, data), encoding="utf-8")
        print(f"wrote {path}")

    print(f"DONE: {len(RUBRICAS)} rubricas escritas en {out}")


if __name__ == "__main__":
    main()
