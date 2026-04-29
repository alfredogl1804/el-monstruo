import os
import sys
import json
import argparse
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

init(autoreset=True)

class InvestigadorRealidad:
    def __init__(self):
        self.sonar_api_key = os.environ.get("SONAR_API_KEY")
        if not self.sonar_api_key:
            print(f"{Fore.RED}❌ Error: SONAR_API_KEY no configurada.{Style.RESET_ALL}")
            sys.exit(1)
            
    def buscar_en_perplexity(self, query):
        print(f"{Fore.CYAN}ℹ️ Consultando a Perplexity Sonar: '{query}'...{Style.RESET_ALL}")
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.sonar_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [
                {"role": "system", "content": "Eres un investigador de datos reales. Responde solo con hechos verificados y listas estructuradas."},
                {"role": "user", "content": query}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"{Fore.RED}❌ Error en Perplexity: {e}{Style.RESET_ALL}")
            return None
            
    def scrape_leones_mx(self):
        print(f"{Fore.CYAN}ℹ️ Haciendo scraping de leones.mx...{Style.RESET_ALL}")
        try:
            # En una implementación real más compleja usaríamos selenium/playwright
            # Aquí hacemos un request básico como demostración de la herramienta
            response = requests.get("https://www.leones.mx", timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer imágenes/logos para identificar patrocinadores
            images = soup.find_all('img')
            patrocinadores = []
            for img in images:
                src = img.get('src', '').lower()
                alt = img.get('alt', '').lower()
                
                # Lista de patrocinadores conocidos para buscar coincidencias
                conocidos = ["caliente", "mifel", "dunosusa", "tecate", "telcel", "coca-cola", "boxito"]
                for p in conocidos:
                    if p in src or p in alt:
                        if p not in patrocinadores:
                            patrocinadores.append(p)
                            
            return patrocinadores
        except Exception as e:
            print(f"{Fore.RED}❌ Error en scraping: {e}{Style.RESET_ALL}")
            return []
            
    def investigar_patrocinadores(self, output_file):
        print(f"\n{Fore.MAGENTA}=== INVESTIGADOR DE REALIDAD: PATROCINADORES LEONES DE YUCATÁN ==={Style.RESET_ALL}")
        
        # 1. Scraping
        patrocinadores_web = self.scrape_leones_mx()
        if patrocinadores_web:
            print(f"{Fore.GREEN}✅ Encontrados en web: {', '.join(patrocinadores_web)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ No se encontraron patrocinadores por scraping directo.{Style.RESET_ALL}")
            
        # 2. Perplexity
        query = "Lista de patrocinadores oficiales actuales (2026) del equipo de béisbol Leones de Yucatán. Incluye marcas en el jersey y en el estadio."
        resultado_perplexity = self.buscar_en_perplexity(query)
        
        if resultado_perplexity:
            print(f"{Fore.GREEN}✅ Resultados de Perplexity obtenidos.{Style.RESET_ALL}")
        
        # Guardar resultados
        resultado_final = {
            "scraping": patrocinadores_web,
            "perplexity_raw": resultado_perplexity
        }
        
        with open(output_file, 'w') as f:
            json.dump(resultado_final, f, indent=2)
            
        print(f"{Fore.GREEN}✅ Investigación guardada en {output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Ruta del archivo JSON de salida")
    args = parser.parse_args()
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    investigador = InvestigadorRealidad()
    investigador.investigar_patrocinadores(args.output)
