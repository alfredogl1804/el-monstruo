#!/usr/bin/env python3.11
"""
validate_registry.py v3.0 — Valida integridad completa del skill.

Verifica:
- YAML validity en references/, arsenals/, routing/
- Credential exposure en todos los archivos
- Env var references
- Arsenal structure
- Decision router: TODAS las rutas tienen "primary"
- Capability registry: todas las capabilities tienen providers
- Pipeline templates: todos los steps referencian capabilities existentes
- Cross-reference: capabilities ↔ router consistency
- TTL/freshness warnings

Uso:
    python3.11 validate_registry.py [--output report.json]
"""

import os
import re
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

SKILL_DIR = Path(__file__).parent.parent
REFERENCES_DIR = SKILL_DIR / "references"
ARSENALS_DIR = SKILL_DIR / "arsenals"
ROUTING_DIR = SKILL_DIR / "routing"
DOCS_DIR = SKILL_DIR / "docs"

CREDENTIAL_PATTERNS = [
    r'sk-[a-zA-Z0-9]{20,}',
    r'sk-ant-[a-zA-Z0-9]{20,}',
    r'AIza[a-zA-Z0-9_-]{35}',
    r'xai-[a-zA-Z0-9]{20,}',
    r'pplx-[a-zA-Z0-9]{20,}',
    r'Bearer [a-zA-Z0-9_-]{20,}',
    r'ghp_[a-zA-Z0-9]{36}',
    r'[a-f0-9]{32,64}',
]

SAFE_CONTEXTS = [
    'env_var', 'method:', '#', 'pattern', 'regex', 'r"', "r'",
    'notion_id', 'collection://', 'data_source', 'db_id',
    'project_url', 'endpoint', 'base_url', 'datasource',
    'db id', '**db', 'credential_ref', 'auth_ref', 'actor:',
    'model:', 'model_id', 'docs:', 'url:', 'input_example',
    'input_hint', 'connection_pattern', 'from_notion', 'apify_api',
    'account_id', 'project_id', 'run_id', 'voice_id', 'avatar_id',
    'video_id', 'trigger_pattern', 'description:', 'note:',
]


def validate_yaml_files():
    issues = []
    valid = []
    yaml_dirs = [
        ("references", REFERENCES_DIR),
        ("arsenals", ARSENALS_DIR),
        ("routing", ROUTING_DIR),
    ]
    for dir_name, dir_path in yaml_dirs:
        if not dir_path.exists():
            issues.append({"file": dir_name, "issue": f"Directorio {dir_name}/ no existe"})
            continue
        for yaml_file in sorted(dir_path.glob("*.yaml")):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data:
                    valid.append(f"{dir_name}/{yaml_file.name}")
                else:
                    issues.append({"file": f"{dir_name}/{yaml_file.name}", "issue": "Archivo vacío"})
            except yaml.YAMLError as e:
                issues.append({"file": f"{dir_name}/{yaml_file.name}", "issue": f"YAML inválido: {str(e)[:100]}"})
    return valid, issues


def check_credential_exposure():
    exposures = []
    for ext in ["*.yaml", "*.md", "*.py", "*.json"]:
        for filepath in SKILL_DIR.rglob(ext):
            if any(skip in str(filepath) for skip in ["cache", "snapshots", "__pycache__", ".git"]):
                continue
            try:
                content = filepath.read_text(encoding='utf-8')
                for pattern in CREDENTIAL_PATTERNS:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if len(match) > 15 and not match.startswith("env_var"):
                            context_line = ""
                            for line in content.split('\n'):
                                if match in line:
                                    context_line = line.strip()[:120]
                                    break
                            if any(safe in context_line.lower() for safe in SAFE_CONTEXTS):
                                continue
                            exposures.append({
                                "file": str(filepath.relative_to(SKILL_DIR)),
                                "pattern": pattern[:30],
                                "match_preview": match[:10] + "...",
                                "context": context_line
                            })
            except Exception:
                pass
    return exposures


def validate_env_references():
    missing = []
    present = []
    for dir_path in [REFERENCES_DIR, ARSENALS_DIR, ROUTING_DIR]:
        if not dir_path.exists():
            continue
        for yaml_file in dir_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                env_refs = re.findall(r'env_var:\s*(\w+)', content)
                env_refs += re.findall(r'env:(\w+)', content)
                env_refs = list(set(env_refs))
                for env_var in env_refs:
                    if os.environ.get(env_var):
                        present.append({"env_var": env_var, "source": yaml_file.name})
                    else:
                        missing.append({"env_var": env_var, "source": yaml_file.name})
            except Exception:
                pass
    return present, missing


def validate_arsenals():
    issues = []
    if not ARSENALS_DIR.exists():
        return [{"file": "arsenals/", "issue": "Directorio no existe"}]
    required_fields = ["connector", "type"]
    for yaml_file in sorted(ARSENALS_DIR.glob("*.yaml")):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if not data:
                issues.append({"file": yaml_file.name, "issue": "Arsenal vacío"})
                continue
            for field in required_fields:
                if field not in data:
                    issues.append({"file": yaml_file.name, "issue": f"Falta campo: {field}"})
        except Exception as e:
            issues.append({"file": yaml_file.name, "issue": str(e)[:100]})
    return issues


def validate_router_primaries():
    """Verifica que TODAS las rutas del decision_router tengan 'primary' explícito."""
    issues = []
    router_file = ROUTING_DIR / "decision_router.yaml"
    if not router_file.exists():
        return [{"issue": "decision_router.yaml no existe"}]
    try:
        with open(router_file, 'r', encoding='utf-8') as f:
            router = yaml.safe_load(f)
        routes = router.get("routes", {})
        routes_without_primary = []
        for route_name, route_config in routes.items():
            if isinstance(route_config, dict) and "primary" not in route_config:
                routes_without_primary.append(route_name)
        if routes_without_primary:
            for r in routes_without_primary:
                issues.append({"route": r, "issue": "Sin 'primary' explícito"})
        return issues
    except Exception as e:
        return [{"issue": f"Error parseando router: {str(e)[:100]}"}]


def validate_capabilities():
    """Verifica capability_registry.yaml: todas las capabilities tienen providers."""
    issues = []
    cap_file = ROUTING_DIR / "capability_registry.yaml"
    if not cap_file.exists():
        return [{"issue": "capability_registry.yaml no existe"}], 0
    try:
        with open(cap_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        capabilities = data.get("capabilities", {})
        cap_count = len(capabilities)
        for cap_name, cap_config in capabilities.items():
            if not isinstance(cap_config, dict):
                issues.append({"capability": cap_name, "issue": "No es un dict"})
                continue
            if "providers" not in cap_config:
                issues.append({"capability": cap_name, "issue": "Sin providers"})
            if "description" not in cap_config:
                issues.append({"capability": cap_name, "issue": "Sin description"})
            if "triggers" not in cap_config:
                issues.append({"capability": cap_name, "issue": "Sin triggers"})
        return issues, cap_count
    except Exception as e:
        return [{"issue": f"Error: {str(e)[:100]}"}], 0


def validate_pipelines():
    """Verifica pipeline_templates.yaml: steps referencian capabilities existentes."""
    issues = []
    pipe_file = ROUTING_DIR / "pipeline_templates.yaml"
    cap_file = ROUTING_DIR / "capability_registry.yaml"
    if not pipe_file.exists():
        return [{"issue": "pipeline_templates.yaml no existe"}], 0
    try:
        with open(pipe_file, 'r', encoding='utf-8') as f:
            pipe_data = yaml.safe_load(f)
        # Load capabilities for cross-reference
        known_caps = set()
        if cap_file.exists():
            with open(cap_file, 'r', encoding='utf-8') as f:
                cap_data = yaml.safe_load(f)
            known_caps = set(cap_data.get("capabilities", {}).keys())

        pipelines = pipe_data.get("pipelines", {})
        pipe_count = len(pipelines)
        for pipe_name, pipe_config in pipelines.items():
            if not isinstance(pipe_config, dict):
                issues.append({"pipeline": pipe_name, "issue": "No es un dict"})
                continue
            if "steps" not in pipe_config:
                issues.append({"pipeline": pipe_name, "issue": "Sin steps"})
                continue
            if "trigger_patterns" not in pipe_config:
                issues.append({"pipeline": pipe_name, "issue": "Sin trigger_patterns"})
            for step_name, step_config in pipe_config["steps"].items():
                if isinstance(step_config, dict) and "capability" in step_config:
                    cap = step_config["capability"]
                    if known_caps and cap not in known_caps:
                        issues.append({
                            "pipeline": pipe_name,
                            "step": step_name,
                            "issue": f"Capability '{cap}' no existe en capability_registry"
                        })
        return issues, pipe_count
    except Exception as e:
        return [{"issue": f"Error: {str(e)[:100]}"}], 0


def validate_ttl_freshness():
    """Verifica TTL/freshness de archivos con last_verified."""
    warnings = []
    today = datetime.now()
    for dir_path in [REFERENCES_DIR, ARSENALS_DIR, ROUTING_DIR]:
        if not dir_path.exists():
            continue
        for yaml_file in dir_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    continue
                last_verified = data.get("last_verified")
                ttl_days = data.get("ttl_days", 30)
                if last_verified:
                    verified_date = datetime.strptime(str(last_verified), "%Y-%m-%d")
                    age_days = (today - verified_date).days
                    if age_days > ttl_days:
                        warnings.append({
                            "file": yaml_file.name,
                            "last_verified": str(last_verified),
                            "ttl_days": ttl_days,
                            "age_days": age_days,
                            "status": "STALE"
                        })
                    elif age_days > ttl_days * 0.8:
                        warnings.append({
                            "file": yaml_file.name,
                            "last_verified": str(last_verified),
                            "ttl_days": ttl_days,
                            "age_days": age_days,
                            "status": "EXPIRING_SOON"
                        })
            except Exception:
                pass
    return warnings


def validate_docs():
    """Verifica que los docs modulares existan."""
    issues = []
    required_docs = ["connection_patterns.md", "fallback_policy.md"]
    for doc in required_docs:
        if not (DOCS_DIR / doc).exists():
            issues.append({"file": f"docs/{doc}", "issue": "No existe"})
    return issues


def main():
    parser = argparse.ArgumentParser(description="Valida integridad de registros v3.0")
    parser.add_argument("--output", help="Guardar reporte en JSON")
    args = parser.parse_args()

    print("=" * 60)
    print("  Registry Validation Report v3.0 (Capability-Routed)")
    print("=" * 60)

    # 1. YAML validity
    valid_yamls, yaml_issues = validate_yaml_files()
    print(f"\n📄 YAML Files: {len(valid_yamls)} válidos, {len(yaml_issues)} problemas")
    for v in valid_yamls:
        print(f"   ✅ {v}")
    for issue in yaml_issues:
        print(f"   ❌ {issue['file']}: {issue['issue']}")

    # 2. Credential exposure
    exposures = check_credential_exposure()
    print(f"\n🔒 Credentials: {len(exposures)} exposiciones")
    if exposures:
        for exp in exposures[:5]:
            print(f"   ⚠️  {exp['file']}: {exp['context'][:80]}")
    else:
        print("   ✅ Sin credenciales expuestas")

    # 3. Env vars
    present_envs, missing_envs = validate_env_references()
    print(f"\n🔑 Env Vars: {len(present_envs)} presentes, {len(missing_envs)} faltantes")
    for m in missing_envs:
        print(f"   ⚠️  {m['env_var']} (ref en {m['source']})")

    # 4. Arsenals
    arsenal_issues = validate_arsenals()
    print(f"\n🏰 Arsenals: {len(arsenal_issues)} problemas")
    if arsenal_issues:
        for issue in arsenal_issues:
            print(f"   ⚠️  {issue.get('file','')}: {issue['issue']}")
    else:
        print("   ✅ Arsenals válidos")

    # 5. Router primaries
    router_issues = validate_router_primaries()
    print(f"\n🔀 Router Primaries: {len(router_issues)} rutas sin primary")
    if router_issues:
        for issue in router_issues:
            print(f"   ❌ {issue.get('route','')}: {issue['issue']}")
    else:
        print("   ✅ Todas las rutas tienen primary")

    # 6. Capabilities
    cap_issues, cap_count = validate_capabilities()
    print(f"\n🧠 Capabilities: {cap_count} definidas, {len(cap_issues)} problemas")
    if cap_issues:
        for issue in cap_issues:
            print(f"   ⚠️  {issue.get('capability','')}: {issue['issue']}")
    else:
        print("   ✅ Todas las capabilities válidas")

    # 7. Pipelines
    pipe_issues, pipe_count = validate_pipelines()
    print(f"\n🔗 Pipelines: {pipe_count} definidos, {len(pipe_issues)} problemas")
    if pipe_issues:
        for issue in pipe_issues:
            print(f"   ⚠️  {issue.get('pipeline','')}/{issue.get('step','')}: {issue['issue']}")
    else:
        print("   ✅ Todos los pipelines válidos")

    # 8. TTL/Freshness
    ttl_warnings = validate_ttl_freshness()
    print(f"\n⏰ TTL/Freshness: {len(ttl_warnings)} warnings")
    if ttl_warnings:
        for w in ttl_warnings:
            print(f"   ⚠️  {w['file']}: {w['status']} (age={w['age_days']}d, ttl={w['ttl_days']}d)")
    else:
        print("   ✅ Todo fresco")

    # 9. Docs
    doc_issues = validate_docs()
    print(f"\n📚 Docs: {len(doc_issues)} faltantes")
    if doc_issues:
        for issue in doc_issues:
            print(f"   ❌ {issue['file']}: {issue['issue']}")
    else:
        print("   ✅ Docs completos")

    # Summary
    total_critical = len(yaml_issues) + len(exposures) + len(router_issues)
    total_warnings = len(arsenal_issues) + len(cap_issues) + len(pipe_issues) + len(ttl_warnings) + len(doc_issues)

    # Count routes
    try:
        with open(ROUTING_DIR / "decision_router.yaml", 'r') as f:
            route_count = len(yaml.safe_load(f).get("routes", {}))
    except:
        route_count = 0

    print(f"\n{'=' * 60}")
    print(f"  YAML válidos:      {len(valid_yamls)}")
    print(f"  Arsenals:          {len(list(ARSENALS_DIR.glob('*.yaml')))} archivos")
    print(f"  Rutas de decisión: {route_count}")
    print(f"  Capabilities:      {cap_count}")
    print(f"  Pipelines:         {pipe_count}")
    print(f"  Critical issues:   {total_critical}")
    print(f"  Warnings:          {total_warnings}")
    print(f"  Status: {'✅ HEALTHY' if total_critical == 0 else '❌ CRITICAL ISSUES'}")
    print(f"{'=' * 60}")

    if args.output:
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0",
            "yaml_valid": valid_yamls,
            "yaml_issues": yaml_issues,
            "credential_exposures": exposures,
            "env_vars_present": present_envs,
            "env_vars_missing": missing_envs,
            "arsenal_issues": arsenal_issues,
            "router_issues": router_issues,
            "capability_issues": cap_issues,
            "capability_count": cap_count,
            "pipeline_issues": pipe_issues,
            "pipeline_count": pipe_count,
            "ttl_warnings": ttl_warnings,
            "doc_issues": doc_issues,
            "total_critical": total_critical,
            "total_warnings": total_warnings,
        }
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReporte guardado: {args.output}")


if __name__ == "__main__":
    main()
