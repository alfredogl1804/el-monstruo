"""
ARQUITECTURA ENGRANAJE — CAPA 1: FÍSICA REAL
=============================================
Implementa las 4 propiedades físicas que distinguen a un sistema vivo
de un programa tradicional event-driven:

1. INERCIA (I)     — Resistencia al cambio de velocidad. Engranajes grandes
                     no arrancan instantáneamente; necesitan acumular energía.
2. FRICCIÓN (μ)    — Pérdida de energía en cada contacto. Cada salto entre
                     embriones cuesta tokens/latencia/dinero.
3. RESONANCIA (ω)  — Cuando dos engranajes giran en frecuencia armónica,
                     se amplifican mutuamente. Si están desincronizados,
                     se cancelan o destruyen.
4. HOLGURA (ε)     — Margen de juego entre dientes. Tolerancia a error
                     antes de propagar el cambio. Estabiliza el sistema
                     ante ruido.

Comparamos: comportamiento SIN física vs CON física en 3 escenarios.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional

# ============================================================
# CAPA 0 — ENGRANAJE SIMPLE (sin física, baseline)
# ============================================================


class EngranajeSimple:
    """Versión v1.0 — sin física. Cada vuelta entrante = transmisión inmediata."""

    def __init__(self, nombre: str, radio: float, accion: Callable):
        self.nombre = nombre
        self.radio = radio
        self.accion = accion
        self.engranados: List["EngranajeSimple"] = []
        self.vueltas_acumuladas = 0.0
        self.acciones_ejecutadas = 0

    def conectar(self, otro):
        if otro not in self.engranados:
            self.engranados.append(otro)
            otro.engranados.append(self)

    def girar(self, vueltas: float, origen=None):
        self.vueltas_acumuladas += vueltas
        if self.vueltas_acumuladas >= 1.0:
            n = int(self.vueltas_acumuladas)
            self.vueltas_acumuladas -= n
            for _ in range(n):
                self.accion(self.nombre)
                self.acciones_ejecutadas += 1
        for otro in self.engranados:
            if otro != origen:
                otro.girar(vueltas * (self.radio / otro.radio), origen=self)


# ============================================================
# CAPA 1 — ENGRANAJE FÍSICO (con las 4 propiedades reales)
# ============================================================


@dataclass
class EngranajeFisico:
    """
    Versión v2.0 — con física real.

    Propiedades:
      - inercia (I):   factor de resistencia al cambio de velocidad. Default 0.0 = sin inercia.
                       Mientras mayor, más vueltas se necesitan para alcanzar velocidad nominal.
      - friccion (μ):  fracción de torque perdido en cada contacto. 0.0 = sin pérdida, 1.0 = nada se transmite.
      - frecuencia_natural (ω): frecuencia preferida de giro. Si recibe cerca de esa, amplifica.
      - holgura (ε):   margen de tolerancia. Vueltas por debajo de este umbral no se propagan.
    """

    nombre: str
    radio: float
    accion: Callable
    inercia: float = 0.0
    friccion: float = 0.0
    frecuencia_natural: float = 1.0
    holgura: float = 0.0

    velocidad_actual: float = 0.0
    vueltas_acumuladas: float = 0.0
    acciones_ejecutadas: int = 0
    energia_perdida_friccion: float = 0.0
    veces_amortiguado_holgura: int = 0
    veces_resonancia: int = 0
    engranados: List["EngranajeFisico"] = field(default_factory=list)

    def conectar(self, otro: "EngranajeFisico"):
        if otro not in self.engranados:
            self.engranados.append(otro)
            otro.engranados.append(self)

    def girar(
        self, vueltas_entrantes: float, frecuencia_entrante: float = 1.0, origen: Optional["EngranajeFisico"] = None
    ):
        # 1. HOLGURA: si las vueltas entrantes son menores al margen de holgura, se absorben sin propagar
        if abs(vueltas_entrantes) < self.holgura:
            self.veces_amortiguado_holgura += 1
            return  # no propaga, no acumula

        # 2. INERCIA: la velocidad real del engranaje cambia GRADUALMENTE hacia las vueltas entrantes
        #    Si inercia=0, alcanza la velocidad entrante de inmediato
        #    Si inercia=0.5, alcanza solo el 50% del cambio en este step
        if self.inercia > 0:
            velocidad_objetivo = vueltas_entrantes
            cambio = (velocidad_objetivo - self.velocidad_actual) * (1.0 - self.inercia)
            self.velocidad_actual += cambio
            vueltas_efectivas = self.velocidad_actual
        else:
            self.velocidad_actual = vueltas_entrantes
            vueltas_efectivas = vueltas_entrantes

        # 3. RESONANCIA: si la frecuencia entrante es cercana a la natural, amplifica
        delta_freq = abs(frecuencia_entrante - self.frecuencia_natural)
        if delta_freq < 0.1:  # umbral de resonancia
            factor_resonancia = 1.0 + (0.1 - delta_freq) * 5.0  # hasta x1.5
            vueltas_efectivas *= factor_resonancia
            self.veces_resonancia += 1

        # 4. Acumular y posiblemente ejecutar acción
        self.vueltas_acumuladas += vueltas_efectivas
        if self.vueltas_acumuladas >= 1.0:
            n = int(self.vueltas_acumuladas)
            self.vueltas_acumuladas -= n
            for _ in range(n):
                self.accion(self.nombre)
                self.acciones_ejecutadas += 1

        # 5. Transmitir a engranados, aplicando FRICCIÓN
        for otro in self.engranados:
            if otro != origen:
                vueltas_brutas = vueltas_efectivas * (self.radio / otro.radio)
                vueltas_perdidas = vueltas_brutas * self.friccion
                vueltas_netas = vueltas_brutas - vueltas_perdidas
                self.energia_perdida_friccion += vueltas_perdidas
                otro.girar(vueltas_netas, frecuencia_entrante=frecuencia_entrante, origen=self)


# ============================================================
# ACCIONES (compartidas por ambas capas)
# ============================================================


def accion_log(nombre: str):
    print(f"      ⚡ [{nombre}] ejecutó acción")


# ============================================================
# ESCENARIO 1 — RUIDO DE ALTA FRECUENCIA
# (entradas chiquitas y constantes — ej. ping de monitoreo)
# ============================================================


def escenario_1_ruido(con_fisica: bool):
    print(f"\n{'=' * 60}")
    print(f"ESCENARIO 1: Ruido de alta frecuencia ({'CON' if con_fisica else 'SIN'} física)")
    print("Entrada: 100 micro-eventos de 0.05 vueltas cada uno")
    print(f"{'=' * 60}")
    if con_fisica:
        e1 = EngranajeFisico("Sensor", radio=1.0, accion=accion_log, holgura=0.1, friccion=0.1)
        e2 = EngranajeFisico("Procesador", radio=1.0, accion=accion_log, holgura=0.1, friccion=0.1)
        e3 = EngranajeFisico("Decisor", radio=2.0, accion=accion_log, holgura=0.1)
    else:
        e1 = EngranajeSimple("Sensor", 1.0, accion_log)
        e2 = EngranajeSimple("Procesador", 1.0, accion_log)
        e3 = EngranajeSimple("Decisor", 2.0, accion_log)
    e1.conectar(e2)
    e2.conectar(e3)

    for i in range(100):
        e1.girar(0.05) if not con_fisica else e1.girar(0.05, frecuencia_entrante=1.0)

    print("\nResultados:")
    print(f"  Sensor:     {e1.acciones_ejecutadas} acciones | acumulado: {e1.vueltas_acumuladas:.2f}")
    print(f"  Procesador: {e2.acciones_ejecutadas} acciones | acumulado: {e2.vueltas_acumuladas:.2f}")
    print(f"  Decisor:    {e3.acciones_ejecutadas} acciones | acumulado: {e3.vueltas_acumuladas:.2f}")
    if con_fisica:
        print(
            f"  → Holgura amortiguó {e1.veces_amortiguado_holgura + e2.veces_amortiguado_holgura + e3.veces_amortiguado_holgura} micro-eventos (no llegaron a propagarse)"
        )
        print(
            f"  → Energía perdida por fricción: {e1.energia_perdida_friccion + e2.energia_perdida_friccion:.2f} vueltas"
        )


# ============================================================
# ESCENARIO 2 — SHOCK BRUSCO
# (un evento gigante repentino — ej. lanzamiento de campaña)
# ============================================================


def escenario_2_shock(con_fisica: bool):
    print(f"\n{'=' * 60}")
    print(f"ESCENARIO 2: Shock brusco ({'CON' if con_fisica else 'SIN'} física)")
    print("Entrada: 1 evento de 10.0 vueltas (shock masivo)")
    print(f"{'=' * 60}")
    if con_fisica:
        e1 = EngranajeFisico("Recepción", radio=1.0, accion=accion_log, inercia=0.0)
        e2 = EngranajeFisico("Buffer", radio=1.0, accion=accion_log, inercia=0.7, friccion=0.05)
        e3 = EngranajeFisico("Ejecutor", radio=1.0, accion=accion_log, inercia=0.5)
    else:
        e1 = EngranajeSimple("Recepción", 1.0, accion_log)
        e2 = EngranajeSimple("Buffer", 1.0, accion_log)
        e3 = EngranajeSimple("Ejecutor", 1.0, accion_log)
    e1.conectar(e2)
    e2.conectar(e3)

    e1.girar(10.0) if not con_fisica else e1.girar(10.0, frecuencia_entrante=1.0)

    print("\nResultados:")
    print(f"  Recepción: {e1.acciones_ejecutadas} acciones")
    print(f"  Buffer:    {e2.acciones_ejecutadas} acciones | velocidad final: {getattr(e2, 'velocidad_actual', 'N/A')}")
    print(f"  Ejecutor:  {e3.acciones_ejecutadas} acciones | velocidad final: {getattr(e3, 'velocidad_actual', 'N/A')}")
    if con_fisica:
        print("  → INERCIA absorbió el shock: el Ejecutor solo recibió fracción del torque inicial.")


# ============================================================
# ESCENARIO 3 — RESONANCIA CONSTRUCTIVA
# (input rítmico que coincide con frecuencia natural)
# ============================================================


def escenario_3_resonancia(con_fisica: bool):
    print(f"\n{'=' * 60}")
    print(f"ESCENARIO 3: Resonancia ({'CON' if con_fisica else 'SIN'} física)")
    print("Entrada: 10 eventos de 0.3 vueltas a frecuencia 1.0 (sintonía perfecta)")
    print(f"{'=' * 60}")
    if con_fisica:
        e1 = EngranajeFisico("Antena", radio=1.0, accion=accion_log, frecuencia_natural=1.0)
        e2 = EngranajeFisico("Amplificador", radio=1.0, accion=accion_log, frecuencia_natural=1.0)
        e3 = EngranajeFisico("Salida", radio=1.0, accion=accion_log, frecuencia_natural=1.0)
    else:
        e1 = EngranajeSimple("Antena", 1.0, accion_log)
        e2 = EngranajeSimple("Amplificador", 1.0, accion_log)
        e3 = EngranajeSimple("Salida", 1.0, accion_log)
    e1.conectar(e2)
    e2.conectar(e3)

    for i in range(10):
        if con_fisica:
            e1.girar(0.3, frecuencia_entrante=1.0)
        else:
            e1.girar(0.3)

    print("\nResultados:")
    print(f"  Antena:        {e1.acciones_ejecutadas} acciones | acumulado: {e1.vueltas_acumuladas:.2f}")
    print(f"  Amplificador:  {e2.acciones_ejecutadas} acciones | acumulado: {e2.vueltas_acumuladas:.2f}")
    print(f"  Salida:        {e3.acciones_ejecutadas} acciones | acumulado: {e3.vueltas_acumuladas:.2f}")
    if con_fisica:
        total_resonancias = e1.veces_resonancia + e2.veces_resonancia + e3.veces_resonancia
        print(f"  → RESONANCIA se activó {total_resonancias} veces, amplificando la señal.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("█  ARQUITECTURA ENGRANAJE — CAPA 1: FÍSICA REAL  █")
    print("█  Comparativa SIN física (v1.0) vs CON física (v2.0)  █")
    print("█" * 60)

    for con_fisica in [False, True]:
        escenario_1_ruido(con_fisica)
        escenario_2_shock(con_fisica)
        escenario_3_resonancia(con_fisica)

    print("\n" + "=" * 60)
    print("FIN DE PRUEBAS — analizar logs arriba para detectar emergencias")
    print("=" * 60 + "\n")
