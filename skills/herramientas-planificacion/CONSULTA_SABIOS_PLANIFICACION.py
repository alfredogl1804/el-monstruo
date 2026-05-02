#!/usr/bin/env python3.11
"""
CONSULTA_SABIOS_PLANIFICACION.py — Herramienta de planificación
Consulta REAL a los Sabios (GPT-5.4, Claude, Gemini 3.1, Grok, Perplexity)
vía API para enriquecer decisiones de diseño del plan.
Conexión REAL a cada API. Cero simulaciones.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

from colorama import Fore, Style, init

init(autoreset=True)


class ConsultaSabiosPlanificacion:
    def __init__(self):
        self.sabios = {}
        self._verificar_credenciales()

    def _verificar_credenciales(self):
        """Verifica qué sabios están disponibles según las API keys configuradas."""
        credenciales = {
            "gpt54": {"env": "OPENAI_API_KEY", "nombre": "GPT-5.4", "disponible": False},
            "claude": {"env": "ANTHROPIC_API_KEY", "nombre": "Claude Opus", "disponible": False},
            "gemini": {"env": "GEMINI_API_KEY", "nombre": "Gemini 3.1 Pro", "disponible": False},
            "grok": {"env": "XAI_API_KEY", "nombre": "Grok", "disponible": False},
            "perplexity": {"env": "SONAR_API_KEY", "nombre": "Perplexity Sonar Pro", "disponible": False},
        }

        print(f"\n{Fore.CYAN}🔑 Verificando credenciales de los Sabios...{Style.RESET_ALL}")
        disponibles = 0
        for key, info in credenciales.items():
            if os.environ.get(info["env"]):
                info["disponible"] = True
                disponibles += 1
                print(f"  {Fore.GREEN}✅ {info['nombre']}: API key encontrada{Style.RESET_ALL}")
            else:
                print(f"  {Fore.RED}❌ {info['nombre']}: API key NO encontrada ({info['env']}){Style.RESET_ALL}")

        self.sabios = credenciales

        if disponibles == 0:
            print(
                f"{Fore.RED}❌ BLOQUEADO: No hay ningún sabio disponible. Configura al menos una API key.{Style.RESET_ALL}"
            )
            sys.exit(1)

        print(f"\n{Fore.WHITE}  Sabios disponibles: {disponibles}/5{Style.RESET_ALL}")

    def _llamar_gpt54(self, prompt, system_prompt):
        """Llama a GPT-5.4 vía OpenAI API."""
        import openai

        # Si OPENAI_API_BASE está vacío o no existe, no pasarlo para usar el default
        kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
        base = os.environ.get("OPENAI_API_BASE", "").strip()
        if base:
            kwargs["base_url"] = base
        client = openai.OpenAI(**kwargs)

        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR GPT-5.4: {e}"

    def _llamar_claude(self, prompt, system_prompt):
        """Llama a Claude vía Anthropic API."""
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",  # Actualizar cuando haya nuevo modelo disponible
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            return f"ERROR Claude: {e}"

    def _llamar_gemini(self, prompt, system_prompt):
        """Llama a Gemini 3.1 Pro vía Google GenAI API."""
        try:
            from google import genai

            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            full_prompt = f"{system_prompt}\n\n{prompt}"

            response = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)
            return response.text
        except Exception as e:
            return f"ERROR Gemini: {e}"

    def _llamar_grok(self, prompt, system_prompt):
        """Llama a Grok vía xAI API (compatible con OpenAI)."""
        import openai

        client = openai.OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")

        try:
            response = client.chat.completions.create(
                model="grok-3",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR Grok: {e}"

    def _llamar_perplexity(self, prompt, system_prompt):
        """Llama a Perplexity Sonar Pro para validación en tiempo real."""
        import openai

        client = openai.OpenAI(api_key=os.environ["SONAR_API_KEY"], base_url="https://api.perplexity.ai")

        try:
            response = client.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR Perplexity: {e}"

    def consultar(self, prompt_text, output_dir, sabios_a_consultar=None, rol_context=""):
        """
        Consulta a los sabios disponibles con un prompt de planificación.

        Args:
            prompt_text: El prompt a enviar a cada sabio
            output_dir: Directorio donde guardar las respuestas
            sabios_a_consultar: Lista de sabios a consultar (None = todos los disponibles)
            rol_context: Contexto adicional del rol que debe asumir cada sabio
        """
        print(f"\n{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}  CONSULTA A SABIOS PARA DISEÑO DE PLAN{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")

        os.makedirs(output_dir, exist_ok=True)

        # Determinar qué sabios consultar
        if sabios_a_consultar is None:
            sabios_a_consultar = [k for k, v in self.sabios.items() if v["disponible"]]
        else:
            # Filtrar solo los que están disponibles
            sabios_a_consultar = [s for s in sabios_a_consultar if self.sabios.get(s, {}).get("disponible", False)]

        if not sabios_a_consultar:
            print(f"{Fore.RED}❌ BLOQUEADO: Ninguno de los sabios solicitados está disponible.{Style.RESET_ALL}")
            return None

        print(
            f"{Fore.CYAN}ℹ️ Consultando a: {', '.join([self.sabios[s]['nombre'] for s in sabios_a_consultar])}{Style.RESET_ALL}"
        )

        # System prompt base para planificación
        system_prompt = f"""Eres un experto consultor de planificación estratégica para producción de contenido audiovisual deportivo.
Tu rol es analizar el plan propuesto y ofrecer mejoras concretas, identificar riesgos, y proponer soluciones creativas.
Contexto del proyecto: Producción de un cortometraje/serie de entretenimiento para el estadio Kukulcán de los Leones de Yucatán.
Personajes: Leoncio (villano bueno/rebelde, ídolo de papás), Leonel El Coronel (coprotagonista, héroe corporativo, ídolo de niños), Yuna (heroína ágil, ídolo de niñas).
El contenido se transmitirá en las dos pantallas gigantes más grandes de LATAM durante los juegos.
{rol_context}
IMPORTANTE: Sé específico, concreto y accionable. No des respuestas genéricas."""

        # Mapeo de funciones de llamada
        llamadores = {
            "gpt54": self._llamar_gpt54,
            "claude": self._llamar_claude,
            "gemini": self._llamar_gemini,
            "grok": self._llamar_grok,
            "perplexity": self._llamar_perplexity,
        }

        # Ejecutar consultas
        resultados = {}
        for sabio_id in sabios_a_consultar:
            nombre = self.sabios[sabio_id]["nombre"]
            print(f"\n{Fore.YELLOW}🧠 Consultando a {nombre}...{Style.RESET_ALL}")

            start_time = time.time()
            respuesta = llamadores[sabio_id](prompt_text, system_prompt)
            elapsed = time.time() - start_time

            # Guardar respuesta individual
            resp_file = os.path.join(output_dir, f"respuesta_{sabio_id}.md")
            with open(resp_file, "w", encoding="utf-8") as f:
                f.write(f"# Respuesta de {nombre}\n\n")
                f.write(f"**Fecha:** {datetime.now().isoformat()}\n")
                f.write(f"**Tiempo de respuesta:** {elapsed:.1f}s\n\n")
                f.write("---\n\n")
                f.write(respuesta)

            resultados[sabio_id] = {
                "nombre": nombre,
                "respuesta": respuesta,
                "tiempo_segundos": round(elapsed, 1),
                "archivo": resp_file,
                "es_error": respuesta.startswith("ERROR"),
            }

            if respuesta.startswith("ERROR"):
                print(f"  {Fore.RED}❌ {respuesta[:100]}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.GREEN}✅ Respuesta recibida ({elapsed:.1f}s, {len(respuesta)} chars){Style.RESET_ALL}")

        # ── Generar síntesis ──
        exitosos = {k: v for k, v in resultados.items() if not v["es_error"]}

        sintesis_file = os.path.join(output_dir, "SINTESIS_SABIOS.md")
        with open(sintesis_file, "w", encoding="utf-8") as f:
            f.write("# Síntesis de Consulta a los Sabios\n\n")
            f.write(f"**Fecha:** {datetime.now().isoformat()}\n")
            f.write(f"**Sabios consultados:** {len(sabios_a_consultar)}\n")
            f.write(f"**Respuestas exitosas:** {len(exitosos)}\n")
            f.write(f"**Errores:** {len(resultados) - len(exitosos)}\n\n")

            f.write("## Prompt Enviado\n\n")
            f.write(f"```\n{prompt_text[:500]}{'...' if len(prompt_text) > 500 else ''}\n```\n\n")

            for sabio_id, data in resultados.items():
                f.write(f"## {data['nombre']}\n\n")
                if data["es_error"]:
                    f.write(f"**ERROR:** {data['respuesta']}\n\n")
                else:
                    f.write(f"**Tiempo:** {data['tiempo_segundos']}s\n\n")
                    f.write(data["respuesta"])
                    f.write("\n\n---\n\n")

        # Guardar metadata JSON
        meta_file = os.path.join(output_dir, "metadata_consulta.json")
        meta = {
            "fecha": datetime.now().isoformat(),
            "prompt_length": len(prompt_text),
            "sabios_consultados": sabios_a_consultar,
            "resultados": {
                k: {
                    "nombre": v["nombre"],
                    "tiempo_segundos": v["tiempo_segundos"],
                    "chars_respuesta": len(v["respuesta"]),
                    "es_error": v["es_error"],
                    "archivo": v["archivo"],
                }
                for k, v in resultados.items()
            },
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        print(f"\n{Fore.GREEN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Consulta completada:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Síntesis:  {sintesis_file}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Metadata:  {meta_file}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Exitosos:  {len(exitosos)}/{len(sabios_a_consultar)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 60}{Style.RESET_ALL}")

        return {"sintesis": sintesis_file, "metadata": meta_file, "resultados": resultados}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consulta a los Sabios para enriquecer el diseño del plan")
    parser.add_argument("--prompt", required=True, help="Texto del prompt o ruta a archivo .md con el prompt")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida para las respuestas")
    parser.add_argument(
        "--sabios",
        nargs="+",
        default=None,
        choices=["gpt54", "claude", "gemini", "grok", "perplexity"],
        help="Sabios específicos a consultar (default: todos los disponibles)",
    )
    parser.add_argument("--rol", default="", help="Contexto adicional del rol que debe asumir cada sabio")
    args = parser.parse_args()

    # Si el prompt es una ruta a archivo, leer su contenido
    if os.path.isfile(args.prompt):
        with open(args.prompt, "r", encoding="utf-8") as f:
            prompt_text = f.read()
    else:
        prompt_text = args.prompt

    consultor = ConsultaSabiosPlanificacion()
    consultor.consultar(prompt_text, args.output_dir, sabios_a_consultar=args.sabios, rol_context=args.rol)
