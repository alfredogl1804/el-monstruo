def calculate_severity(analysis_data):
    print("  -> Calculando índices de severidad (LATAM-POLICRIS)...")

    # Base sentiment score
    sentiment = analysis_data.get("sentiment_score", 50)

    # Multiplicadores LATAM
    crisis_type = analysis_data.get("crisis_type", "")
    allegations = analysis_data.get("allegations", [])

    score = sentiment * 0.5

    # Ajustes por gravedad de la acusación
    if "criminal_association" in crisis_type or any("narco" in str(a).lower() for a in allegations):
        score += 30
        print("    ⚠️ Detectada acusación de narcotráfico (+30)")

    if "policy_backlash" in crisis_type:
        score += 10
        print("    ⚠️ Detectada controversia política (+10)")

    # Limitar a 100
    final_score = min(100, max(0, score))

    # Asignar nivel
    if final_score < 25:
        level = "VERDE"
    elif final_score < 50:
        level = "AMARILLO"
    elif final_score < 75:
        level = "NARANJA"
    else:
        level = "ROJO"

    return {"score": final_score, "level": level}
