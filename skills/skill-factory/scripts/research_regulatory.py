#!/usr/bin/env python3.11
"""
research_regulatory.py — Investigación regulatoria para dominios sensibles.

Investiga el marco regulatorio aplicable a la skill usando Perplexity Sonar.
Se activa automáticamente cuando la skill toca dominios regulados
(finanzas, salud, legal, datos personales, cripto).

Uso:
    python3.11 research_regulatory.py --spec spec.yaml --output regulatory.yaml
"""

import argparse, asyncio, json, os, sys, yaml
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

# Dominios que requieren investigación regulatoria
REGULATED_DOMAINS = {
    "finance": {
        "jurisdictions": ["México", "EE.UU.", "UE"],
        "topics": ["licencias requeridas", "KYC/AML", "protección al consumidor",
                   "regulación fintech", "valores y tokens"],
        "authorities": ["CNBV", "SEC", "ESMA", "Banxico"]
    },
    "health": {
        "jurisdictions": ["México", "EE.UU.", "UE"],
        "topics": ["HIPAA equivalentes", "datos de salud", "telemedicina",
                   "dispositivos médicos software", "consentimiento informado"],
        "authorities": ["COFEPRIS", "FDA", "EMA"]
    },
    "legal": {
        "jurisdictions": ["México", "EE.UU.", "UE"],
        "topics": ["práctica legal sin licencia", "confidencialidad",
                   "responsabilidad por consejo", "jurisdicción aplicable"],
        "authorities": ["Barra de abogados", "ABA"]
    },
    "crypto": {
        "jurisdictions": ["México", "EE.UU.", "UE", "Países Bajos"],
        "topics": ["clasificación de tokens", "exchanges regulados", "MiCA",
                   "Ley Fintech México", "impuestos cripto"],
        "authorities": ["CNBV", "SEC", "ESMA", "DNB"]
    },
    "data_privacy": {
        "jurisdictions": ["México", "EE.UU.", "UE"],
        "topics": ["GDPR", "LFPDPPP", "CCPA", "transferencia transfronteriza",
                   "derechos ARCO", "consentimiento"],
        "authorities": ["INAI", "FTC", "DPA europeas"]
    }
}


async def identify_applicable_regulations(spec: dict) -> dict:
    """Identifica qué regulaciones aplican a la skill."""
    domain = spec.get("domain", "").lower()
    regulated = spec.get("regulated", False)
    tags = [t.lower() for t in spec.get("tags", [])]
    
    applicable = {}
    
    for reg_domain, config in REGULATED_DOMAINS.items():
        if reg_domain in domain or reg_domain in " ".join(tags) or regulated:
            applicable[reg_domain] = config
    
    # Si no se detectó automáticamente pero está marcado como regulado, usar GPT para clasificar
    if not applicable and regulated:
        prompt = f"""Esta skill está marcada como regulada. Identifica qué dominios regulatorios aplican.

Skill: {spec.get('name')}
Dominio: {spec.get('domain')}
Descripción: {spec.get('description')}
Capacidades: {spec.get('core_capabilities', [])}

Responde con JSON:
{{"domains": ["finance", "health", "legal", "crypto", "data_privacy"]}}
Solo incluye los que realmente aplican."""

        response = await consultar_sabio("gpt54", prompt, timeout=30)
        text = response.get("respuesta", "")
        try:
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                for d in result.get("domains", []):
                    if d in REGULATED_DOMAINS:
                        applicable[d] = REGULATED_DOMAINS[d]
        except:
            pass
    
    return applicable


async def research_regulation(domain: str, config: dict, spec: dict) -> dict:
    """Investiga regulaciones específicas de un dominio."""
    
    topics_results = []
    
    for topic in config.get("topics", []):
        for jurisdiction in config.get("jurisdictions", []):
            query = f"Regulación vigente {topic} {jurisdiction} 2025-2026"
            
            prompt = f"""Investiga la regulación vigente sobre: {topic}
Jurisdicción: {jurisdiction}
Contexto: Skill de IA para {spec.get('domain')} - {spec.get('description')}

Responde con:
1. Ley/regulación aplicable (nombre exacto y fecha)
2. Requisitos específicos
3. Sanciones por incumplimiento
4. Estado actual (vigente, en consulta, propuesta)
5. Autoridad competente

Sé conciso y preciso. Solo hechos verificables."""

            try:
                response = await consultar_sabio("perplexity", prompt, timeout=30)
                topics_results.append({
                    "topic": topic,
                    "jurisdiction": jurisdiction,
                    "status": "ok",
                    "findings": response.get("respuesta", "")[:2000]
                })
            except Exception as e:
                topics_results.append({
                    "topic": topic,
                    "jurisdiction": jurisdiction,
                    "status": "error",
                    "error": str(e)
                })
    
    return {
        "domain": domain,
        "authorities": config.get("authorities", []),
        "topics_researched": len(topics_results),
        "successful": sum(1 for t in topics_results if t["status"] == "ok"),
        "results": topics_results
    }


def compile_regulatory_report(spec: dict, applicable: dict, research_results: list) -> dict:
    """Compila el reporte regulatorio."""
    
    disclaimers = []
    requirements = []
    risks = []
    
    for result in research_results:
        domain = result.get("domain", "")
        for finding in result.get("results", []):
            if finding["status"] == "ok":
                requirements.append({
                    "domain": domain,
                    "topic": finding["topic"],
                    "jurisdiction": finding["jurisdiction"],
                    "details": finding["findings"]
                })
    
    # Disclaimers estándar
    disclaimers.append("Esta skill NO constituye asesoría legal, financiera ni médica.")
    disclaimers.append("Los usuarios deben consultar profesionales licenciados para decisiones importantes.")
    disclaimers.append("La información regulatoria puede cambiar; verificar vigencia antes de actuar.")
    
    return {
        "skill_name": spec.get("name"),
        "regulated_domains": list(applicable.keys()),
        "disclaimers": disclaimers,
        "requirements": requirements,
        "risks": risks,
        "recommendation": "Incluir disclaimers en SKILL.md y en outputs de la skill"
    }


async def main():
    parser = argparse.ArgumentParser(description="Investigación regulatoria para skills")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--output", required=True, help="Path de salida para regulatory.yaml")
    args = parser.parse_args()
    
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    print(f"⚖️ Investigando regulaciones para: {spec.get('name')}")
    
    # Identificar regulaciones aplicables
    applicable = await identify_applicable_regulations(spec)
    
    if not applicable:
        print("  ℹ️ No se detectaron dominios regulados")
        report = {"skill_name": spec.get("name"), "regulated_domains": [], "disclaimers": [], "requirements": []}
    else:
        print(f"  📋 Dominios regulados: {list(applicable.keys())}")
        
        # Investigar cada dominio
        results = []
        for domain, config in applicable.items():
            print(f"  🔍 Investigando {domain}...")
            result = await research_regulation(domain, config, spec)
            results.append(result)
            print(f"    ✅ {result['successful']}/{result['topics_researched']} temas")
        
        report = compile_regulatory_report(spec, applicable, results)
    
    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\n📁 Reporte regulatorio guardado en: {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
