import argparse
import json
import os

from colorama import Fore, Style, init

init(autoreset=True)


class ArquitectoNarrativo:
    def __init__(self):
        self.rituales_base = [
            {
                "nombre": "El Rugido",
                "descripcion": "Leoncio se para en la cima de la Zona 313 y ruge, la multitud responde.",
                "personaje_principal": "leoncio",
            },
            {
                "nombre": "El Saludo del Coronel",
                "descripcion": "Leonel hace un saludo militar impecable a la cámara, los niños imitan.",
                "personaje_principal": "leonel",
            },
            {
                "nombre": "La Voltereta de Yuna",
                "descripcion": "Yuna hace una voltereta acrobática espectacular antes de un momento clave.",
                "personaje_principal": "yuna",
            },
            {
                "nombre": "El Kayfabe (La Rivalidad)",
                "descripcion": "Leonel y Leoncio se miran fijamente, a punto de pelear, pero terminan chocando puños o siendo interrumpidos cómicamente.",
                "personaje_principal": "ambos",
            },
            {
                "nombre": "La Mascota Invitada",
                "descripcion": "La mascota del patrocinador del día (ej. el perrito de Dunosusa) hace un gag visual que resuelve la tensión.",
                "personaje_principal": "invitado",
            },
        ]

    def estructurar_episodio(self, tema, patrocinador_invitado):
        print(f"{Fore.CYAN}ℹ️ Estructurando episodio piloto: '{tema}'...{Style.RESET_ALL}")

        episodio = {
            "tema": tema,
            "patrocinador_invitado": patrocinador_invitado,
            "estructura": [
                {
                    "acto": 1,
                    "fase": "Setup (20%)",
                    "descripcion": f"Establecer el status quo. Leonel patrulla el estadio manteniendo el orden. Yuna anima a los niños. Introducción del patrocinador {patrocinador_invitado}.",
                    "rituales_incluidos": ["El Saludo del Coronel"],
                },
                {
                    "acto": 2,
                    "fase": "Desarrollo y Conflicto (60%)",
                    "descripcion": f"Leoncio aparece en la Zona 313 causando revuelo (el {tema}). Leonel intenta detenerlo. Se inicia la rivalidad.",
                    "rituales_incluidos": ["El Rugido", "El Kayfabe (La Rivalidad)"],
                },
                {
                    "acto": 3,
                    "fase": "Payoff y Resolución (20%)",
                    "descripcion": f"La tensión llega al clímax, pero la mascota de {patrocinador_invitado} interviene con un gag cómico. Yuna hace su acrobacia. Todos celebran a los Leones.",
                    "rituales_incluidos": ["La Mascota Invitada", "La Voltereta de Yuna"],
                },
            ],
        }

        return episodio

    def generar_plan(self, tema, patrocinador, output_file):
        print(f"\n{Fore.MAGENTA}=== ARQUITECTO NARRATIVO (PLANIFICACIÓN) ==={Style.RESET_ALL}")

        episodio = self.estructurar_episodio(tema, patrocinador)

        print(f"\n{Fore.WHITE}Estructura Generada:{Style.RESET_ALL}")
        for acto in episodio["estructura"]:
            print(f"{Fore.YELLOW}{acto['acto']}. {acto['fase']}{Style.RESET_ALL}")
            print(f"   {acto['descripcion']}")
            print(f"   Rituales: {', '.join(acto['rituales_incluidos'])}")

        # Guardar resultados
        with open(output_file, "w") as f:
            json.dump(episodio, f, indent=2)

        print(f"\n{Fore.GREEN}✅ Estructura narrativa guardada en {output_file}{Style.RESET_ALL}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tema", required=True, help="Tema central del episodio")
    parser.add_argument("--patrocinador", required=True, help="Patrocinador invitado")
    parser.add_argument("--output", required=True, help="Ruta del archivo JSON de salida")
    args = parser.parse_args()

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    arquitecto = ArquitectoNarrativo()
    arquitecto.generar_plan(args.tema, args.patrocinador, args.output)
