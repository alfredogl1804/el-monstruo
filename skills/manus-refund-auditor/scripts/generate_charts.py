import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def generate_charts(actual_credits, optimal_credits):
    actual = int(actual_credits)
    optimal = int(optimal_credits)
    waste = actual - optimal
    
    # 1. Gráfica de distribución de créditos (Pie Chart)
    plt.figure(figsize=(8, 6))
    labels = ['Créditos Óptimos (Productivos)', 'Créditos Desperdiciados (Falla Técnica)']
    sizes = [optimal, waste]
    colors = ['#2ecc71', '#e74c3c']
    explode = (0, 0.1)
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
    plt.title(f'Distribución de Créditos\nTotal Consumido: {actual:,}', fontsize=16, pad=20)
    plt.axis('equal')
    
    plt.savefig('evidencia_creditos.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # 2. Gráfica de barras comparativa
    plt.figure(figsize=(8, 6))
    categories = ['Consumo Real', 'Consumo Óptimo Estimado']
    values = [actual, optimal]
    
    bars = plt.bar(categories, values, color=['#e74c3c', '#2ecc71'], width=0.6)
    
    plt.title('Comparativa de Consumo de Créditos', fontsize=16, pad=20)
    plt.ylabel('Cantidad de Créditos', fontsize=12)
    
    # Añadir etiquetas de valor en las barras
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (actual*0.02), 
                 f'{int(yval):,}', ha='center', va='bottom', fontsize=12, weight='bold')
                 
    # Añadir texto de factor de ineficiencia
    factor = actual / optimal
    plt.text(0.5, actual*0.8, f'Factor de Ineficiencia: {factor:.2f}x', 
             ha='center', va='center', fontsize=14, weight='bold', 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='red', boxstyle='round,pad=0.5'))
             
    plt.savefig('evidencia_comparativa.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"✅ Gráficas generadas exitosamente en el directorio actual.")
    print(f"   - evidencia_creditos.png")
    print(f"   - evidencia_comparativa.png")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 generate_charts.py <actual_credits> <optimal_credits>")
        sys.exit(1)
        
    generate_charts(sys.argv[1], sys.argv[2])
