"""kernel.espiral — Pieza Espiral (Hairspring) del Reloj Suizo.

Sprint ESPIRAL-001 — Pieza magna #5 del Reloj Suizo (DSC-MO-010 §2.1 fila 5).

La Espiral es la pieza que da PRECISIÓN al reloj mecánico. En El Monstruo,
detecta deviation del pulse_rate observado vs baseline canónico del consumer
en una ventana móvil (default 15 min) y aplica feedback negativo dinámico
sobre el Escape: aumenta pulse_intervals durante spikes (dampening), los
reduce durante undershoots (acceleration), o los retorna al canonical
cuando la deviation cae bajo umbral.

Spec firmado T1 commit `0de35e6`, gate VERDE Cowork commit `5325f17`.

DSC enforzado:
- DSC-MO-006 v1.1 (doctrina del silencio — marcadores ESPIRAL_BEGIN/END en embrion_loop)
- DSC-MO-010 (Reloj Suizo §2.1 fila 5)
- DSC-G-008 v3 (anti-Goodhart + deducción consecuencias)
- DSC-S-006 v1.1 (RLS en embrion_homeostasis_log)
- DSC-MO-011 (Embryo Patch Lane — marcadores reversibles)

Módulos:
- homeostasis: clase Hairspring (sense_deviation + apply_correction + return_to_canonical)
- sensor: observador pulse_rate ventana móvil
- controller: P-controller (proportional only en v1, PID en v2)
"""

from kernel.espiral.controller import ProportionalController
from kernel.espiral.homeostasis import Hairspring
from kernel.espiral.sensor import PulseRateSensor

__all__ = ["Hairspring", "PulseRateSensor", "ProportionalController"]
