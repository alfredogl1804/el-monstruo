import os
import sys
import json
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

class GuardianCanonPlanificacion:
    def __init__(self):
        self.canon = {
            "leoncio": {
                "cara": "AMARILLO BRILLANTE",
                "ojos": "VERDES",
                "nariz": "NEGRA redonda",
                "melena": "CAFÉ ROJIZO",
                "barba": "BLANCA/GRIS",
                "vestuario": "Playera VERDE LIMÓN con motivos mayas y logo DUNOSUSA"
            },
            "leonel": {
                "cara": "NARANJA",
                "ojos": "BLANCOS con pupilas NEGRAS",
                "melena": "CAFÉ OSCURO",
                "detalles": "whiskers NEGROS pintados",
                "vestuario": "Jersey BLANCO baseball con PINSTRIPES grises, texto LEONES en rojo, logo Caliente.mx"
            },
            "yuna": {
                "cara": "NARANJA suave",
                "ojos": "MARRONES",
                "melena": "Sin melena (leona), mechón café como flequillo",
                "vestuario": "Jersey BLANCO con texto LEONES en ROJO, collar/cadena"
            }
        }
        
    def validar_y_enriquecer_prompt(self, personaje, prompt_original):
        print(f"{Fore.CYAN}ℹ️ Validando prompt para {personaje.capitalize()}...{Style.RESET_ALL}")
        
        personaje = personaje.lower()
        if personaje not in self.canon:
            print(f"{Fore.RED}❌ Error: Personaje '{personaje}' no existe en el canon.{Style.RESET_ALL}")
            return prompt_original, False
            
        reglas = self.canon[personaje]
        faltantes = []
        prompt_lower = prompt_original.lower()
        
        # Verificar cada regla
        for atributo, valor in reglas.items():
            # Simplificamos la verificación para la herramienta
            # Buscamos palabras clave principales del valor
            palabras_clave = [p.lower() for p in valor.split() if len(p) > 3 and "/" not in p]
            
            # Si al menos una palabra clave importante no está en el prompt
            if any(p not in prompt_lower for p in palabras_clave[:2]):
                faltantes.append(f"{atributo}: {valor}")
                
        if not faltantes:
            print(f"{Fore.GREEN}✅ Prompt válido. Cumple el canon.{Style.RESET_ALL}")
            return prompt_original, True
            
        print(f"{Fore.YELLOW}⚠️ Prompt incompleto. Faltan atributos canónicos:{Style.RESET_ALL}")
        for f in faltantes:
            print(f"  - {f}")
            
        # Enriquecer automáticamente
        print(f"{Fore.CYAN}ℹ️ Enriqueciendo prompt automáticamente...{Style.RESET_ALL}")
        
        prompt_enriquecido = f"{prompt_original}. MUST INCLUDE EXACT DETAILS: "
        detalles = []
        for atributo, valor in reglas.items():
            detalles.append(f"{atributo} {valor}")
            
        prompt_enriquecido += ", ".join(detalles)
        
        return prompt_enriquecido, False
        
    def procesar_archivo(self, input_file, output_file):
        print(f"\n{Fore.MAGENTA}=== GUARDIÁN DEL CANON (PLANIFICACIÓN) ==={Style.RESET_ALL}")
        
        if not os.path.exists(input_file):
            print(f"{Fore.RED}❌ Error: Archivo {input_file} no existe.{Style.RESET_ALL}")
            return
            
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        escenas = data.get("escenas", [])
        if not escenas:
            print(f"{Fore.YELLOW}⚠️ No se encontraron escenas para validar.{Style.RESET_ALL}")
            return
            
        resultados = []
        corregidos = 0
        
        for escena in escenas:
            personaje = escena.get("personaje")
            prompt = escena.get("prompt")
            
            print(f"\n{Fore.WHITE}Escena {escena.get('id')}: {personaje}{Style.RESET_ALL}")
            prompt_final, es_valido = self.validar_y_enriquecer_prompt(personaje, prompt)
            
            if not es_valido:
                corregidos += 1
                
            resultados.append({
                "id": escena.get("id"),
                "personaje": personaje,
                "prompt_original": prompt,
                "prompt_validado": prompt_final,
                "fue_corregido": not es_valido
            })
            
        # Guardar resultados
        with open(output_file, 'w') as f:
            json.dump({"escenas_validadas": resultados, "total_corregidos": corregidos}, f, indent=2)
            
        print(f"\n{Fore.CYAN}Resumen: {len(escenas)} procesadas, {corregidos} corregidas automáticamente.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Reporte guardado en {output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Ruta del archivo JSON con los prompts a validar")
    parser.add_argument("--output", required=True, help="Ruta del archivo JSON de salida")
    args = parser.parse_args()
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    guardian = GuardianCanonPlanificacion()
    guardian.procesar_archivo(args.input, args.output)
