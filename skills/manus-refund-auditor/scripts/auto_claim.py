import os
import sys
import time

def run_auto_claim(task_link, user_email, actual_credits, optimal_credits, phase_failed):
    print(f"🚀 Iniciando proceso automatizado de reclamo para: {task_link}")
    
    # 1. Generar gráficas
    print("📊 Generando evidencia visual...")
    os.system(f"python3 /home/ubuntu/skills/manus-refund-auditor/scripts/generate_charts.py {actual_credits} {optimal_credits}")
    
    # 2. Preparar el reclamo
    print("📝 Redactando reclamo formal...")
    with open('/home/ubuntu/skills/manus-refund-auditor/templates/claim_template.md', 'r') as f:
        template = f.read()
        
    factor = round(int(actual_credits) / int(optimal_credits), 2)
    waste = int(actual_credits) - int(optimal_credits)
    
    claim = template.replace('[TASK_LINK]', task_link)
    claim = claim.replace('[WASTED_CREDITS]', f"{waste:,}")
    claim = claim.replace('[ACTUAL_CREDITS]', f"{int(actual_credits):,}")
    claim = claim.replace('[OPTIMAL_CREDITS]', f"{int(optimal_credits):,}")
    claim = claim.replace('[FACTOR]', str(factor))
    claim = claim.replace('[PHASE_NUMBER]', str(phase_failed))
    claim = claim.replace('[USER_NAME]', user_email.split('@')[0])
    claim = claim.replace('[USER_EMAIL]', user_email)
    
    with open('/home/ubuntu/reclamo_listo.md', 'w') as f:
        f.write(claim)
        
    print("✅ Reclamo generado en /home/ubuntu/reclamo_listo.md")
    print("\n⚠️ ATENCIÓN AGENTE: Ahora debes usar las herramientas del navegador para:")
    print("1. Abrir https://manus.im/feedback")
    print("2. Seleccionar 'Task report'")
    print("3. Inyectar el contenido de /home/ubuntu/reclamo_listo.md")
    print("4. Subir evidencia_creditos.png y evidencia_comparativa.png")
    print(f"5. Llenar el link: {task_link}")
    print(f"6. Llenar el email: {user_email}")
    print("7. Pedir confirmación al usuario para enviar.")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Uso: python3 auto_claim.py <task_link> <email> <actual_credits> <optimal_credits> <phase_failed>")
        sys.exit(1)
        
    run_auto_claim(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
