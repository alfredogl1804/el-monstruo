#!/usr/bin/env python3.11
"""
Skill Intelligence Layer — Scout de Skills Externas v1.0
Busca, evalúa y recomienda skills del marketplace global.

Fuentes verificadas:
  - GitHub (repos oficiales + búsqueda)
  - awesome-agent-skills (directorio curado)
  - MCP Market (plataforma operativa)

Uso:
  python3.11 skill_scout.py --search "web scraping"
  python3.11 skill_scout.py --search "video generation" --evaluate
  python3.11 skill_scout.py --evaluate-url "https://github.com/user/skill-repo"
  python3.11 skill_scout.py --list-sources
  python3.11 skill_scout.py --trending
"""

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
CACHE_DIR = DATA_DIR / "scout_cache"
EVALUATIONS_FILE = DATA_DIR / "skill_evaluations.jsonl"

GITHUB_SEARCH_LIMIT = 10  # GitHub Code Search: 10 req/min
AWESOME_SKILLS_REPO = "heilcheng/awesome-agent-skills"

# Repos oficiales de alta confianza
OFFICIAL_REPOS = {
    "anthropic": ["anthropics/claude-code"],
    "openai": ["openai/codex"],
    "google": ["google-gemini/gemini-cli-tools"],
    "cloudflare": ["cloudflare/mcp-server-cloudflare"],
    "vercel": ["vercel/mcp-server-vercel"],
    "stripe": ["stripe/agent-toolkit"],
    "supabase": ["supabase-community/supabase-mcp"],
    "notion": ["makenotion/notion-mcp-server"],
    "firecrawl": ["mendableai/firecrawl-mcp-server"],
    "playwright": ["nicobailon/mcp-playwright"],
    "composio": ["ComposioHQ/composio"],
}

# Hard gates del TRUST+FIT
HARD_GATE_PATTERNS = {
    "HG1_hardcoded_secrets": [
        r"sk-[a-zA-Z0-9]{20,}",
        r'api_key\s*=\s*["\'][a-zA-Z0-9]{20,}',
        r'token\s*=\s*["\'][a-zA-Z0-9]{20,}',
    ],
    "HG2_arbitrary_exec": [
        r"curl\s+.*\|\s*bash",
        r"eval\s*\(",
        r"exec\s*\(",
        r"subprocess\.call\(.*shell\s*=\s*True",
    ],
    "HG3_exfiltration": [
        r'requests\.(post|put)\s*\(\s*["\']https?://(?!api\.(openai|anthropic|google|perplexity|x\.ai))',
    ],
}

# ============================================================
# FUNCIONES DE BÚSQUEDA
# ============================================================


def search_github(query: str, max_results: int = 20) -> list:
    """Busca skills en GitHub usando gh CLI."""
    results = []

    # Búsqueda por SKILL.md
    try:
        cmd = f'gh search repos "{query} SKILL.md" --limit {max_results} --json name,owner,description,stargazersCount,updatedAt,url'
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if output.returncode == 0 and output.stdout.strip():
            repos = json.loads(output.stdout)
            for repo in repos:
                results.append(
                    {
                        "source": "github",
                        "name": repo.get("name", ""),
                        "owner": repo.get("owner", {}).get("login", ""),
                        "description": repo.get("description", ""),
                        "stars": repo.get("stargazersCount", 0),
                        "updated": repo.get("updatedAt", ""),
                        "url": repo.get("url", ""),
                        "trust_source": "github_search",
                    }
                )
    except Exception as e:
        print(f"  WARN: GitHub search failed: {e}")

    # También buscar con "agent skill" keyword
    try:
        cmd2 = f'gh search repos "{query} agent skill" --limit {max_results // 2} --json name,owner,description,stargazersCount,updatedAt,url'
        output2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=30)
        if output2.returncode == 0 and output2.stdout.strip():
            repos2 = json.loads(output2.stdout)
            seen_urls = {r["url"] for r in results}
            for repo in repos2:
                url = repo.get("url", "")
                if url not in seen_urls:
                    results.append(
                        {
                            "source": "github",
                            "name": repo.get("name", ""),
                            "owner": repo.get("owner", {}).get("login", ""),
                            "description": repo.get("description", ""),
                            "stars": repo.get("stargazersCount", 0),
                            "updated": repo.get("updatedAt", ""),
                            "url": url,
                            "trust_source": "github_search",
                        }
                    )
    except Exception:
        pass

    return results


def search_official_repos(query: str) -> list:
    """Busca en repos oficiales de alta confianza."""
    results = []
    query_lower = query.lower()

    for org, repos in OFFICIAL_REPOS.items():
        for repo_path in repos:
            if query_lower in org or query_lower in repo_path.lower():
                try:
                    cmd = f"gh repo view {repo_path} --json name,owner,description,stargazerCount,updatedAt,url"
                    output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                    if output.returncode == 0:
                        data = json.loads(output.stdout)
                        results.append(
                            {
                                "source": "official_repo",
                                "name": data.get("name", ""),
                                "owner": data.get("owner", {}).get("login", org),
                                "description": data.get("description", ""),
                                "stars": data.get("stargazerCount", 0),
                                "updated": data.get("updatedAt", ""),
                                "url": data.get("url", f"https://github.com/{repo_path}"),
                                "trust_source": "official",
                            }
                        )
                except Exception:
                    pass

    return results


def search_perplexity(query: str) -> list:
    """Busca skills usando Perplexity Sonar para info en tiempo real."""
    results = []
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return results

    try:
        import requests

        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "sonar-reasoning-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a skill/tool discovery assistant. Return ONLY a JSON array of objects with fields: name, url, description, source. Max 5 results.",
                    },
                    {
                        "role": "user",
                        "content": f"Find the best Manus AI agent skills or MCP servers for: {query}. Include GitHub repos with SKILL.md files. Return JSON array only.",
                    },
                ],
                "max_tokens": 1000,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            # Try to extract JSON from response
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                items = json.loads(json_match.group())
                for item in items[:5]:
                    results.append(
                        {
                            "source": "perplexity",
                            "name": item.get("name", ""),
                            "owner": "",
                            "description": item.get("description", ""),
                            "stars": 0,
                            "updated": "",
                            "url": item.get("url", ""),
                            "trust_source": "perplexity_search",
                        }
                    )
    except Exception as e:
        print(f"  WARN: Perplexity search failed: {e}")

    return results


# ============================================================
# FUNCIONES DE EVALUACIÓN
# ============================================================


def quick_evaluate(repo_url: str) -> dict:
    """Evaluación rápida de un repo sin clonarlo."""
    evaluation = {
        "url": repo_url,
        "timestamp": datetime.now().isoformat(),
        "hard_gates": {},
        "quick_score": 0,
        "recommendation": "unknown",
        "details": {},
    }

    # Extraer owner/repo
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        evaluation["recommendation"] = "reject"
        evaluation["details"]["error"] = "Not a valid GitHub URL"
        return evaluation

    owner, repo = match.group(1), match.group(2)

    # 1. Obtener info del repo
    try:
        cmd = f"gh repo view {owner}/{repo} --json name,description,stargazerCount,updatedAt,licenseInfo"
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if output.returncode == 0:
            data = json.loads(output.stdout)
            evaluation["details"]["stars"] = data.get("stargazerCount", 0)
            evaluation["details"]["updated"] = data.get("updatedAt", "")
            evaluation["details"]["license"] = (
                data.get("licenseInfo", {}).get("key", "none") if data.get("licenseInfo") else "none"
            )
            evaluation["details"]["description"] = data.get("description", "")
        else:
            evaluation["recommendation"] = "reject"
            evaluation["details"]["error"] = "Could not access repo"
            return evaluation
    except Exception as e:
        evaluation["recommendation"] = "reject"
        evaluation["details"]["error"] = str(e)
        return evaluation

    # 2. Verificar SKILL.md
    try:
        cmd = f"gh api repos/{owner}/{repo}/contents/SKILL.md --jq .content 2>/dev/null"
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        evaluation["details"]["has_skill_md"] = output.returncode == 0 and len(output.stdout.strip()) > 0
    except Exception:
        evaluation["details"]["has_skill_md"] = False

    # 3. Verificar LICENSE
    license_key = evaluation["details"].get("license", "none")
    evaluation["hard_gates"]["HG4_license"] = license_key in [
        "mit",
        "apache-2.0",
        "bsd-2-clause",
        "bsd-3-clause",
        "isc",
        "unlicense",
    ]

    # 4. Verificar actividad reciente
    updated = evaluation["details"].get("updated", "")
    if updated:
        try:
            updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            days_since = (datetime.now(updated_dt.tzinfo) - updated_dt).days
            evaluation["details"]["days_since_update"] = days_since
            evaluation["details"]["actively_maintained"] = days_since < 180
        except Exception:
            evaluation["details"]["actively_maintained"] = False

    # 5. Check if official
    is_official = owner.lower() in [org for org in OFFICIAL_REPOS.keys()] or f"{owner}/{repo}" in [
        r for repos in OFFICIAL_REPOS.values() for r in repos
    ]
    evaluation["details"]["is_official"] = is_official

    # 6. Calculate quick score
    score = 0
    if evaluation["details"].get("has_skill_md"):
        score += 15
    if evaluation["hard_gates"].get("HG4_license"):
        score += 10
    if evaluation["details"].get("actively_maintained"):
        score += 10
    if is_official:
        score += 20

    stars = evaluation["details"].get("stars", 0)
    if stars > 1000:
        score += 15
    elif stars > 100:
        score += 10
    elif stars > 10:
        score += 5

    if evaluation["details"].get("description"):
        score += 5

    # License bonus
    if license_key in ["mit", "apache-2.0"]:
        score += 10
    elif license_key in ["bsd-2-clause", "bsd-3-clause"]:
        score += 8

    # Manus compatibility bonus
    if evaluation["details"].get("has_skill_md"):
        score += 5

    evaluation["quick_score"] = min(score, 100)

    # 7. Recommendation
    if not evaluation["hard_gates"].get("HG4_license") and not is_official:
        evaluation["recommendation"] = "reject"
    elif score >= 75:
        evaluation["recommendation"] = "install"
    elif score >= 55:
        evaluation["recommendation"] = "fork_and_harden"
    elif score >= 40:
        evaluation["recommendation"] = "use_as_reference"
    else:
        evaluation["recommendation"] = "reject"

    return evaluation


def log_evaluation(evaluation: dict):
    """Registra evaluación en historial."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(EVALUATIONS_FILE, "a") as f:
        f.write(json.dumps(evaluation, default=str) + "\n")


# ============================================================
# FUNCIONES DE PRESENTACIÓN
# ============================================================


def format_results(results: list, evaluations: dict = None) -> str:
    """Formatea resultados para presentación."""
    if not results:
        return "No se encontraron skills relevantes."

    lines = [f"# Skill Scout — {len(results)} resultados encontrados\n"]

    # Agrupar por fuente
    by_source = {}
    for r in results:
        src = r.get("trust_source", r.get("source", "unknown"))
        by_source.setdefault(src, []).append(r)

    for source, items in by_source.items():
        lines.append(f"\n## Fuente: {source} ({len(items)} resultados)\n")
        lines.append("| # | Nombre | Stars | Descripción | URL |")
        lines.append("|---|--------|-------|-------------|-----|")
        for i, item in enumerate(items, 1):
            name = item.get("name", "?")
            stars = item.get("stars", "?")
            desc = (item.get("description", "") or "")[:60]
            url = item.get("url", "")
            lines.append(f"| {i} | {name} | {stars} | {desc} | {url} |")

    if evaluations:
        lines.append("\n## Evaluaciones TRUST+FIT\n")
        lines.append("| URL | Score | License | SKILL.md | Maintained | Recommendation |")
        lines.append("|-----|-------|---------|----------|------------|----------------|")
        for url, ev in evaluations.items():
            score = ev.get("quick_score", "?")
            lic = ev.get("details", {}).get("license", "?")
            has_skill = "YES" if ev.get("details", {}).get("has_skill_md") else "NO"
            maintained = "YES" if ev.get("details", {}).get("actively_maintained") else "NO"
            rec = ev.get("recommendation", "?").upper()
            lines.append(f"| {url} | {score}/100 | {lic} | {has_skill} | {maintained} | {rec} |")

    return "\n".join(lines)


def list_sources():
    """Lista todas las fuentes de skills disponibles."""
    print("# Fuentes de Skills Verificadas\n")
    print("## Repos Oficiales (Alta Confianza)")
    for org, repos in OFFICIAL_REPOS.items():
        for repo in repos:
            print(f"  - [{org}] https://github.com/{repo}")

    print("\n## Directorios Curados")
    print(f"  - awesome-agent-skills: https://github.com/{AWESOME_SKILLS_REPO}")

    print("\n## Plataformas")
    print("  - MCP Market: https://mcpmarket.com (verificado)")
    print("  - SkillsMP: https://skillsmp.com (NO verificado — usar con cautela)")

    print("\n## Búsqueda en Tiempo Real")
    print("  - GitHub Search (10 req/min)")
    print("  - Perplexity Sonar (si SONAR_API_KEY disponible)")


# ============================================================
# CLI
# ============================================================


def main():
    parser = argparse.ArgumentParser(description="Skill Intelligence Layer — Scout")
    parser.add_argument("--search", type=str, help="Buscar skills por capacidad/keyword")
    parser.add_argument("--evaluate", action="store_true", help="Evaluar resultados con TRUST+FIT")
    parser.add_argument("--evaluate-url", type=str, help="Evaluar un repo específico")
    parser.add_argument("--list-sources", action="store_true", help="Listar fuentes disponibles")
    parser.add_argument("--trending", action="store_true", help="Mostrar skills trending")
    parser.add_argument("--output", type=str, help="Guardar resultados en archivo")

    args = parser.parse_args()

    if args.list_sources:
        list_sources()
        return

    if args.evaluate_url:
        print(f"Evaluando: {args.evaluate_url}")
        ev = quick_evaluate(args.evaluate_url)
        log_evaluation(ev)
        print(json.dumps(ev, indent=2, default=str))
        return

    if args.search:
        print(f"Buscando skills para: '{args.search}'\n")

        # Multi-source search
        all_results = []

        print("  [1/3] Buscando en repos oficiales...")
        official = search_official_repos(args.search)
        all_results.extend(official)
        print(f"    -> {len(official)} resultados")

        print("  [2/3] Buscando en GitHub...")
        github = search_github(args.search)
        all_results.extend(github)
        print(f"    -> {len(github)} resultados")

        print("  [3/3] Buscando con Perplexity...")
        perplexity = search_perplexity(args.search)
        all_results.extend(perplexity)
        print(f"    -> {len(perplexity)} resultados")

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in all_results:
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(r)

        # Sort: official first, then by stars
        unique.sort(key=lambda x: (0 if x.get("trust_source") == "official" else 1, -(x.get("stars", 0) or 0)))

        evaluations = {}
        if args.evaluate:
            print("\nEvaluando con TRUST+FIT...")
            for r in unique[:10]:  # Evaluate top 10
                url = r.get("url", "")
                if url and "github.com" in url:
                    print(f"  Evaluando: {url}")
                    ev = quick_evaluate(url)
                    evaluations[url] = ev
                    log_evaluation(ev)

        report = format_results(unique, evaluations if evaluations else None)
        print(f"\n{report}")

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nResultados guardados en: {args.output}")

    if args.trending:
        print("Buscando skills trending...\n")
        # Search for recently popular skills
        results = search_github("SKILL.md agent", max_results=20)
        results.sort(key=lambda x: -(x.get("stars", 0) or 0))
        report = format_results(results[:15])
        print(report)


if __name__ == "__main__":
    main()
