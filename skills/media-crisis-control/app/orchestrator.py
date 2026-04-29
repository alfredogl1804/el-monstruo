#!/usr/bin/env python3.11
"""Orquestador maestro del Skill Media Crisis Control"""
import sys, os, json, argparse, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.collector import collect_mentions
from analysis.crisis_classifier import classify_crisis
from scoring.severity_score import calculate_severity
from strategy.response_playbooks import generate_strategy
from reporting.executive_report import generate_report

def run_crisis_cycle(target_name):
    print(f"🚀 Iniciando ciclo de control de crisis para: {target_name}")
    
    # 1. Ingestión
    print("📡 Recolectando menciones recientes...")
    mentions = collect_mentions(target_name)
    
    if not mentions:
        print("✅ No se encontraron menciones críticas. Nivel: Verde.")
        return
        
    # 2. Análisis
    print("🧠 Analizando sentimiento, narrativas y vectores de ataque...")
    analysis_data = classify_crisis(mentions, target_name)
    
    # 3. Scoring
    print("⚖️ Calculando score de severidad...")
    severity = calculate_severity(analysis_data)
    
    # 4. Estrategia
    print("🛡️ Generando playbook de respuesta...")
    strategy = generate_strategy(analysis_data, severity)
    
    # 5. Reporte
    print("📄 Generando reporte ejecutivo...")
    report_path = generate_report(target_name, analysis_data, severity, strategy)
    
    print(f"🏁 Ciclo completado. Reporte guardado en: {report_path}")
    return report_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media Crisis Control Orchestrator")
    parser.add_argument("--target", required=True, help="Nombre de la figura pública")
    args = parser.parse_args()
    
    run_crisis_cycle(args.target)
