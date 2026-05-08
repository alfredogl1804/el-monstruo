import time

class Engranaje:
    def __init__(self, nombre: str, radio: float, accion):
        """
        :param nombre: Identificador del engranaje
        :param radio: Tamaño/peso del engranaje. Define la relación de transmisión.
        :param accion: Función a ejecutar cuando el engranaje recibe suficiente torque (da 1 vuelta completa).
        """
        self.nombre = nombre
        self.radio = radio
        self.accion = accion
        self.engranados = []  # Lista de tuplas (engranaje, direccion_transmision)
        self.vueltas_acumuladas = 0.0

    def conectar(self, otro_engranaje):
        """Conecta físicamente este engranaje con otro."""
        if otro_engranaje not in self.engranados:
            self.engranados.append(otro_engranaje)
            otro_engranaje.engranados.append(self)
            print(f"⚙️  Conexión: [{self.nombre}] (r={self.radio}) <---> [{otro_engranaje.nombre}] (r={otro_engranaje.radio})")

    def girar(self, vueltas_recibidas: float, origen=None):
        """
        Recibe un giro. Acumula las vueltas y si llega a 1.0 (o más), ejecuta su acción.
        Luego transmite el giro a los engranajes conectados.
        """
        self.vueltas_acumuladas += vueltas_recibidas
        
        # Log del movimiento actual
        print(f"   🔄 [{self.nombre}] gira {vueltas_recibidas:.2f} vueltas. (Acumulado: {self.vueltas_acumuladas:.2f})")

        # Si completó al menos una vuelta entera, dispara su acción
        if self.vueltas_acumuladas >= 1.0:
            vueltas_enteras = int(self.vueltas_acumuladas)
            self.vueltas_acumuladas -= vueltas_enteras # Mantiene el remanente
            
            for _ in range(vueltas_enteras):
                print(f"   ⚡ [{self.nombre}] COMPLETÓ 1 VUELTA -> Ejecutando acción...")
                self.accion()

        # Transmitir a los engranajes conectados (excepto de donde vino el giro)
        for otro in self.engranados:
            if otro != origen:
                # Relación de transmisión mecánica: vueltas_salida = vueltas_entrada * (radio_entrada / radio_salida)
                vueltas_transmitidas = vueltas_recibidas * (self.radio / otro.radio)
                print(f"      ↳ Transmitiendo {vueltas_transmitidas:.2f} vueltas de [{self.nombre}] a [{otro.nombre}]")
                time.sleep(0.5) # Efecto visual de propagación
                otro.girar(vueltas_transmitidas, origen=self)


# ==========================================
# DEFINICIÓN DE ACCIONES ATÓMICAS
# ==========================================

def accion_detector_lead():
    print("      [ACCION] Lead detectado en webhook.")

def accion_notificador_slack():
    print("      [ACCION] Mensaje enviado a Slack: 'Nuevo lead ingresado'.")

def accion_reporte_gerencial():
    print("      [ACCION] 📊 GENERANDO REPORTE GERENCIAL: Se han procesado 5 leads.")

# ==========================================
# ENSAMBLAJE DEL MECANISMO
# ==========================================

if __name__ == "__main__":
    print("\n--- ENSAMBLANDO ARQUITECTURA ENGRANAJE ---\n")

    # Engranaje 1: Chico, gira rápido. Detecta leads individuales.
    e_detector = Engranaje("Detector de Leads", radio=1.0, accion=accion_detector_lead)
    
    # Engranaje 2: Mediano. Notifica al equipo. Por cada lead, notifica.
    e_notificador = Engranaje("Notificador Slack", radio=1.0, accion=accion_notificador_slack)
    
    # Engranaje 3: Grande. Genera reporte. Necesita que el detector gire 5 veces para dar 1 vuelta.
    e_reporte = Engranaje("Reporte Gerencial", radio=5.0, accion=accion_reporte_gerencial)

    # Conexiones físicas
    e_detector.conectar(e_notificador)
    e_notificador.conectar(e_reporte)

    print("\n--- INICIANDO TRANSMISIÓN DE TORQUE ---\n")

    # Simulamos la llegada de 5 leads en distintos momentos
    for i in range(1, 6):
        print(f"\n[!] EVENTO EXTERNO: Ingresa Lead #{i}")
        # El evento externo hace girar al detector 1 vuelta completa
        e_detector.girar(1.0)
        time.sleep(1)

    print("\n--- FIN DE LA TRANSMISIÓN ---")

