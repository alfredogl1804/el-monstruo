import datetime


def generate_report(target_name, analysis_data, severity, strategy):
    print("  -> Escribiendo reporte en Markdown...")

    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    md = f"""# Diagnóstico de Crisis en Medios: {target_name}
**Fecha/Hora:** {date_str}
**Nivel de Crisis:** {severity["level"]} (Score: {severity["score"]}/100)

## 1. Executive Snapshot
- **Tipo de Crisis:** {analysis_data.get("crisis_type", "Desconocido")}
- **Ejes de Daño:** {", ".join(analysis_data.get("damage_axes", []))}
- **Tipos de Acusación:** {", ".join(analysis_data.get("accusation_types", []))}
- **Estado Probatorio:** {analysis_data.get("evidence_state", "No especificado")}
- **Sentimiento (Hostilidad):** {analysis_data.get("sentiment_score", "N/A")}/100

## 2. Acusaciones y Narrativas Dominantes
"""
    for allegation in analysis_data.get("allegations", []):
        md += f"- {allegation}\n"

    md += "\n## 3. Vectores de Ataque (Quién y Cómo)\n"
    vectors = analysis_data.get("attack_vectors", {})
    if isinstance(vectors, dict):
        for key, val in vectors.items():
            md += f"- **{key}**: {val}\n"
    elif isinstance(vectors, list):
        for val in vectors:
            md += f"- {val}\n"

    md += "\n## 4. Estrategia de Contención (Playbooks LATAM-POLICRIS)\n"
    md += "### Próximas 24 Horas (Acción Inmediata)\n"
    for action in strategy.get("24h_actions", []):
        md += f"- [ ] {action}\n"

    md += "\n### Próximas 72 Horas (Táctica a Corto Plazo)\n"
    for action in strategy.get("72h_strategy", []):
        md += f"- [ ] {action}\n"

    md += "\n### Próximos 7 Días (Campaña y Reencuadre)\n"
    for action in strategy.get("7d_campaign", []):
        md += f"- [ ] {action}\n"

    md += "\n---\n*Reporte generado por Media Crisis Control Skill (Framework LATAM-POLICRIS v1)*"

    report_path = f"/home/ubuntu/skills/media-crisis-control/data/reports/reporte_{target_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.md"

    import os

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    return report_path
