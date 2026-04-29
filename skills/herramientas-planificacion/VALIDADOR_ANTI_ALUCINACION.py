import os
import sys
import json
import argparse
import requests
from colorama import init, Fore, Style

init(autoreset=True)

class ValidadorAntiAlucinacion:
    def __init__(self):
        self.sonar_api_key = os.environ.get("SONAR_API_KEY")
        if not self.sonar_api_key:
            print(f"{Fore.RED}❌ Error: SONAR_API_KEY no configurada.{Style.RESET_ALL}")
            sys.exit(1)
            
    def validar_claim(self, claim):
        print(f"{Fore.CYAN}ℹ️ Validando contra la realidad: '{claim}'...{Style.RESET_ALL}")
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.sonar_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Actúa como un validador estricto de hechos.
        Voy a darte una afirmación. Debes buscar en internet si es verdadera o falsa al día de hoy (abril 2026).
        
        Afirmación a validar: "{claim}"
        
        Responde estrictamente en este formato JSON:
        {{
            "veredicto": "VERDADERO" o "FALSO" o "PARCIALMENTE VERDADERO",
            "evidencia": "Breve explicación con datos reales",
            "fuentes": ["url1", "url2"]
        }}
        """
        
        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [
                {"role": "system", "content": "Responde SOLO con un objeto JSON válido."},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            
            # Limpiar posible markdown formatting del JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            return json.loads(content)
        except Exception as e:
            print(f"{Fore.RED}❌ Error validando: {e}{Style.RESET_ALL}")
            return {"veredicto": "ERROR", "evidencia": str(e), "fuentes": []}
            
    def validar_lista(self, input_file, output_file):
        print(f"\n{Fore.MAGENTA}=== VALIDADOR ANTI-ALUCINACIÓN ==={Style.RESET_ALL}")
        
        if not os.path.exists(input_file):
            print(f"{Fore.RED}❌ Error: Archivo {input_file} no existe.{Style.RESET_ALL}")
            return
            
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        claims = data.get("claims", [])
        if not claims:
            print(f"{Fore.YELLOW}⚠️ No se encontraron claims para validar.{Style.RESET_ALL}")
            return
            
        resultados = []
        bloqueados = 0
        
        for claim in claims:
            resultado = self.validar_claim(claim)
            
            if resultado.get("veredicto") == "VERDADERO":
                print(f"{Fore.GREEN}✅ PASA: {claim}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ BLOQUEADO: {claim}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   Evidencia: {resultado.get('evidencia')}{Style.RESET_ALL}")
                bloqueados += 1
                
            resultados.append({
                "claim": claim,
                "validacion": resultado
            })
            
        # Guardar resultados
        with open(output_file, 'w') as f:
            json.dump({"resultados": resultados, "bloqueados": bloqueados}, f, indent=2)
            
        print(f"\n{Fore.CYAN}Resumen: {len(claims) - bloqueados} aprobados, {bloqueados} bloqueados.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Reporte guardado en {output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Ruta del archivo JSON con los claims a validar")
    parser.add_argument("--output", required=True, help="Ruta del archivo JSON de salida")
    args = parser.parse_args()
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    validador = ValidadorAntiAlucinacion()
    validador.validar_lista(args.input, args.output)
