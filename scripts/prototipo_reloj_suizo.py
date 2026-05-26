"""
ARQUITECTURA RELOJ SUIZO — CAPA 2: TIEMPO Y ENERGIA
====================================================
Prototipo funcional que demuestra autonomia sostenida con dependencia
minima de energia externa, inspirado en la mecanica de los relojes
suizos de alta gama (Patek Philippe Caliber 240, Greubel Forsey).

Piezas implementadas:
- Mainspring (Resorte): almacena energia
- Escapement (Escape): libera en pulsos discretos
- Balance Wheel (Volante): oscila a frecuencia constante
- Hairspring (Espiral): feedback negativo / homeostasis
- Rotor (Automatico): convierte actividad del usuario en cuerda
- Jewels (Rubies): puntos de friccion casi cero
- Remontoir (Constant Force): garantiza calidad constante de output

Ejecuta 3 escenarios:
1. CUERDA MANUAL: un solo impulso inicial, ver cuanto dura
2. AUTOMATICO: usuario activo, rotor recarga continuamente
3. DESCARGA TOTAL: sin recarga, medir punto de muerte
"""

from dataclasses import dataclass, field
from typing import List, Optional

# ============================================================
# PIEZAS DEL RELOJ
# ============================================================


@dataclass
class Mainspring:
    """Resorte: almacena energia potencial."""

    capacidad_maxima: float = 1000.0
    energia_actual: float = 1000.0

    def cargar(self, cantidad: float):
        self.energia_actual = min(self.capacidad_maxima, self.energia_actual + cantidad)

    def descargar(self, cantidad: float) -> float:
        """Devuelve la cantidad realmente descargada."""
        cantidad_real = min(cantidad, self.energia_actual)
        self.energia_actual -= cantidad_real
        return cantidad_real

    def porcentaje(self) -> float:
        return (self.energia_actual / self.capacidad_maxima) * 100


@dataclass
class Escapement:
    """Escape: libera energia en pulsos discretos.
    En un reloj suizo real: 21,600 vibraciones/hora = 6 Hz.
    Aqui: cada N latidos del volante, libera M unidades de energia.
    """

    pulso_cada_n_latidos: int = 1
    energia_por_pulso: float = 1.0
    contador_latidos: int = 0
    pulsos_emitidos: int = 0

    def tick(self, mainspring: Mainspring) -> Optional[float]:
        """Llamado en cada latido del volante. Si toca pulso, libera energia."""
        self.contador_latidos += 1
        if self.contador_latidos >= self.pulso_cada_n_latidos:
            self.contador_latidos = 0
            energia_liberada = mainspring.descargar(self.energia_por_pulso)
            if energia_liberada > 0:
                self.pulsos_emitidos += 1
                return energia_liberada
        return None


@dataclass
class BalanceWheel:
    """Volante: oscila a frecuencia constante. El latido del Monstruo."""

    frecuencia_hz: float = 1.0  # Para el prototipo, 1 latido por step (acelerado vs reloj real)
    latidos_totales: int = 0

    def tick(self):
        self.latidos_totales += 1


@dataclass
class Hairspring:
    """Espiral: feedback negativo. Despues de actividad alta, regresa al estado base."""

    nivel_actividad: float = 0.0
    fuerza_retroceso: float = 0.1  # 10% de retorno por tick

    def perturbar(self, magnitud: float):
        self.nivel_actividad += magnitud

    def tick(self):
        # Feedback negativo: la actividad regresa hacia 0
        self.nivel_actividad *= 1.0 - self.fuerza_retroceso


@dataclass
class Rotor:
    """Rotor automatico: captura actividad natural del usuario y la convierte en cuerda.
    En un reloj automatico real: el movimiento de la muneca recarga el resorte.
    Aqui: cada accion del usuario (mensaje, click, archivo guardado) recarga energia.
    """

    eficiencia: float = 5.0  # cuanta energia genera por unidad de actividad del usuario
    energia_generada_total: float = 0.0

    def captar_actividad(self, magnitud_actividad: float, mainspring: Mainspring):
        energia = magnitud_actividad * self.eficiencia
        antes = mainspring.energia_actual
        mainspring.cargar(energia)
        delta_real = mainspring.energia_actual - antes
        self.energia_generada_total += delta_real
        return delta_real


@dataclass
class Remontoir:
    """Constant Force: garantiza calidad constante del output sin importar
    si el resorte esta lleno o casi vacio. Innovacion de Greubel Forsey.
    En software: ajusta el modelo (fallback) segun el presupuesto restante.
    """

    umbral_low_energy: float = 30.0  # % por debajo del cual baja calidad

    def ajustar_calidad(self, mainspring: Mainspring) -> str:
        """Devuelve el nivel de calidad mantenido."""
        pct = mainspring.porcentaje()
        if pct > 70:
            return "PREMIUM (GPT-5.5 / Claude Opus 4.7)"
        elif pct > self.umbral_low_energy:
            return "ESTANDAR (GPT-4o / Claude Sonnet 4)"
        else:
            return "ECO (Llama 3.3 70B / GPT-4o-mini)"


# ============================================================
# EL MONSTRUO RELOJ
# ============================================================


@dataclass
class MonstruoReloj:
    nombre: str = "El Monstruo"
    mainspring: Mainspring = field(default_factory=Mainspring)
    escapement: Escapement = field(default_factory=Escapement)
    volante: BalanceWheel = field(default_factory=BalanceWheel)
    espiral: Hairspring = field(default_factory=Hairspring)
    rotor: Rotor = field(default_factory=Rotor)
    remontoir: Remontoir = field(default_factory=Remontoir)
    historial: List[dict] = field(default_factory=list)
    acciones_ejecutadas: int = 0
    vivo: bool = True

    def pulso(self, tarea_pendiente: bool = True):
        """Un latido del Monstruo."""
        self.volante.tick()
        self.espiral.tick()
        energia = self.escapement.tick(self.mainspring)
        if energia is None or energia == 0:
            self.vivo = self.mainspring.energia_actual > 0
            return None
        if tarea_pendiente:
            calidad = self.remontoir.ajustar_calidad(self.mainspring)
            self.espiral.perturbar(0.5)
            self.acciones_ejecutadas += 1
            self.historial.append(
                {
                    "latido": self.volante.latidos_totales,
                    "energia_restante": round(self.mainspring.energia_actual, 2),
                    "calidad": calidad,
                    "actividad_residual": round(self.espiral.nivel_actividad, 3),
                }
            )
            return calidad
        return None

    def usuario_activo(self, magnitud: float = 1.0):
        """El usuario hace algo (mensaje, click, archivo guardado).
        El rotor capta esa actividad y recarga el mainspring.
        """
        self.rotor.captar_actividad(magnitud, self.mainspring)


# ============================================================
# ESCENARIOS
# ============================================================


def escenario_cuerda_manual():
    print("\n" + "=" * 60)
    print("ESCENARIO 1: CUERDA MANUAL (Patek Philippe puro)")
    print("Un solo impulso inicial. Sin recarga. ¿Cuanto dura?")
    print("=" * 60)
    monstruo = MonstruoReloj(
        mainspring=Mainspring(capacidad_maxima=100.0, energia_actual=100.0),
        escapement=Escapement(pulso_cada_n_latidos=1, energia_por_pulso=1.0),
    )
    latido = 0
    while monstruo.vivo and latido < 200:
        latido += 1
        monstruo.pulso(tarea_pendiente=True)

    print("\nResultados:")
    print(f"  Latidos totales: {monstruo.volante.latidos_totales}")
    print(f"  Acciones ejecutadas: {monstruo.acciones_ejecutadas}")
    print(f"  Energia final: {monstruo.mainspring.energia_actual:.2f} / {monstruo.mainspring.capacidad_maxima}")
    print(f"  Vivo: {monstruo.vivo}")
    print(f"  Pulsos emitidos por escape: {monstruo.escapement.pulsos_emitidos}")


def escenario_automatico():
    print("\n" + "=" * 60)
    print("ESCENARIO 2: AUTOMATICO (Patek Calatrava con rotor)")
    print("Usuario activo. Rotor recarga continuamente.")
    print("Simulamos 500 latidos con actividad usuario cada 10 latidos.")
    print("=" * 60)
    monstruo = MonstruoReloj(
        mainspring=Mainspring(capacidad_maxima=100.0, energia_actual=100.0),
        escapement=Escapement(pulso_cada_n_latidos=1, energia_por_pulso=1.0),
        rotor=Rotor(eficiencia=2.0),
    )
    for latido in range(1, 501):
        if latido % 10 == 0:
            monstruo.usuario_activo(magnitud=1.0)
        monstruo.pulso(tarea_pendiente=True)
        if not monstruo.vivo:
            print(f"\n  ⚠️  Murio en latido {latido} (rotor no compenso consumo)")
            break

    print("\nResultados:")
    print(f"  Latidos totales: {monstruo.volante.latidos_totales}")
    print(f"  Acciones ejecutadas: {monstruo.acciones_ejecutadas}")
    print(f"  Energia final: {monstruo.mainspring.energia_actual:.2f}")
    print(f"  Energia generada por rotor: {monstruo.rotor.energia_generada_total:.2f}")
    print(f"  Vivo: {monstruo.vivo}")


def escenario_descarga_total():
    print("\n" + "=" * 60)
    print("ESCENARIO 3: DESCARGA TOTAL (sin remontoir)")
    print("Sin recarga. Medimos como cae la calidad y cuando muere.")
    print("=" * 60)
    monstruo = MonstruoReloj(
        mainspring=Mainspring(capacidad_maxima=100.0, energia_actual=100.0),
        escapement=Escapement(pulso_cada_n_latidos=1, energia_por_pulso=1.5),
    )
    transiciones_calidad = []
    calidad_anterior = None
    latido = 0
    while monstruo.vivo and latido < 200:
        latido += 1
        calidad = monstruo.pulso(tarea_pendiente=True)
        if calidad and calidad != calidad_anterior:
            transiciones_calidad.append((latido, calidad, monstruo.mainspring.porcentaje()))
            calidad_anterior = calidad

    print("\nResultados:")
    print(f"  Latidos hasta muerte: {monstruo.volante.latidos_totales}")
    print(f"  Acciones ejecutadas: {monstruo.acciones_ejecutadas}")
    print("  Transiciones de calidad (downgrade automatico via remontoir):")
    for lat, cal, pct in transiciones_calidad:
        print(f"    - Latido {lat:3d}: cambio a {cal} (energia: {pct:.1f}%)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("█  EL MONSTRUO — ARQUITECTURA RELOJ SUIZO v1.0  █")
    print("█  Capa 2: Tiempo y Energia (Autonomia Sostenida)  █")
    print("█" * 60)

    escenario_cuerda_manual()
    escenario_automatico()
    escenario_descarga_total()

    print("\n" + "=" * 60)
    print("FIN — analizar resultados arriba")
    print("=" * 60 + "\n")
