def generate_strategy(analysis_data, severity):
    level = severity["level"]
    crisis_type = analysis_data.get("crisis_type", "")

    strategy = {"24h_actions": [], "72h_strategy": [], "7d_campaign": []}

    # Base actions
    if level == "ROJO":
        strategy["24h_actions"].extend(
            [
                "Activar comité de crisis inmediatamente",
                "No improvisar declaraciones",
                "Preparar rueda de prensa con evidencia",
            ]
        )
    elif level == "NARANJA":
        strategy["24h_actions"].extend(["Preparar statement oficial", "Monitoreo cada 30 min", "Contactar aliados"])
    else:
        strategy["24h_actions"].extend(["Monitoreo continuo", "Evitar sobre-reacción"])

    # Playbook específico: Narcotráfico
    if "criminal_association" in crisis_type or "narco" in str(analysis_data.get("allegations", [])).lower():
        strategy["24h_actions"].append(
            "PLAYBOOK NARCO: Emitir rechazo categórico, jurídico y factual. Exigir evidencia a acusadores."
        )
        strategy["72h_strategy"].append(
            "Activar terceros creíbles (abogados, organizaciones) para desmentir. No usar defensa ideológica."
        )
        strategy["7d_campaign"].append("Documentar cronología del ataque para posible denuncia por difamación.")

    # Playbook específico: Iniciativa polémica (VIH)
    if "policy_backlash" in crisis_type:
        strategy["24h_actions"].append(
            "PLAYBOOK POLICY: Reencuadrar el debate hacia 'salud pública y derechos humanos'."
        )
        strategy["72h_strategy"].append("Desplegar vocería técnica de organizaciones civiles y médicos.")
        strategy["7d_campaign"].append(
            "Campañas de concientización para combatir la desinformación sobre la iniciativa."
        )

    # Compound Crisis (ambas)
    if "compound_crisis" in crisis_type:
        strategy["24h_actions"].insert(
            0,
            "CRÍTICO: Separar narrativas. NO defender la iniciativa VIH usando el desmentido del narco, ni viceversa.",
        )

    return strategy
