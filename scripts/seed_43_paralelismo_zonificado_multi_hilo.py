"""
Semilla 43 (candidata) — Paralelismo zonificado entre hilos Manus.

Patrón empíricamente validado durante:
  - Sprint 86.7: Hilo Catastro y Hilo Memento commitearon en paralelo
                 sin colisión de archivos.
  - Sprint 86.8: Hilo Catastro y Sprint 87.1 (Memento) — zero overlap
                 confirmado por anti-Dory `git stash → pull rebase → pop`.

CONTEXTO

El Cowork firmó hoy política: "mientras Alfredo coordina activamente,
NINGÚN hilo Manus entra en standby". Esto creó la necesidad de
paralelismo seguro entre hilos. La solución empírica fue zonificación
**estricta** de archivos modificables por sprint en la spec firmada.

REGLA CANÓNICA

Cada spec firmada por Cowork debe declarar:
  1. ZONA PRIMARIA: lista de paths/dirs que el hilo PUEDE modificar.
  2. NO TOCÁS: lista explícita de paths/dirs prohibidos.
  3. EXCEPCIONES MÍNIMAS: archivos compartidos (ej. un generator script
     que el sprint necesita pero no posee) deben citarse explícitamente
     y modificarse con el mínimo cambio posible.

Anti-Dory `git stash --include-untracked → git pull --rebase → git
stash pop` ANTES de cada commit es OBLIGATORIO. Si detecta archivos
no míos, NO se commitean bajo mi autoría — se descartan o se respetan
para el dueño legítimo.

EVIDENCIA EMPÍRICA

Sprint 86.7 (paralelo con Sprint 87 NUEVO E2E del Ejecutor):
  - Catastro tocó: kernel/catastro/sources/, kernel/catastro/pipeline.py,
                   kernel/catastro/reasoning_classifier.py
  - Ejecutor tocó: kernel/e2e/, kernel/main.py, scripts/021_e2e_*.sql
  - Conflictos en pull rebase: 0
  - Anti-Dory detecciones: 5 archivos del Ejecutor preservados sin tocar

Sprint 86.8 (paralelo con Sprint 87.1 Memento):
  - Catastro tocó: kernel/catastro/recommendation.py + scripts/027_*
  - Memento tocó: kernel/embriones/, scripts/0XX_memento_*.sql
  - Conflictos en pull rebase: 0
  - Anti-Dory detecciones: ninguno (limpio)

CUÁNDO SE ROMPE

El paralelismo zonificado FALLA cuando:
  1. Dos sprints requieren modificar el mismo archivo de "puente" (ej.
     kernel/main.py registra ambas zonas).
  2. La spec NO declara explícitamente la zona y los hilos asumen
     scope distinto.
  3. Un hilo viola la zona del otro por error o por refactor de scope.

MITIGACIÓN ANTE FALLA

  - Cowork detecta colisión vía `git log --stat` o conflict en rebase.
  - Re-firma spec con división más fina (extrae archivo de puente a
    sprint propio).
  - Si ya hay colisión en código: rebase manual con preservación de
    autoría dual via `git commit --amend --author="..."`.

ESTADO

Candidata. Pendiente formalización por Cowork tras 3+ sprints
consecutivos paralelos sin colisión. Sprint 86.8 fue el segundo —
falta uno más para promover de candidata a semilla canónica.

[Hilo Manus Catastro] · Sprint 86.8 · 2026-05-05
"""
from __future__ import annotations

SEMILLA = {
    "numero": 43,
    "estado": "candidata",
    "titulo": "Paralelismo zonificado entre hilos Manus",
    "patron": (
        "Cada spec firmada declara zona primaria + NO TOCÁS explícitos. "
        "Anti-Dory git stash → pull rebase → pop antes de commit detecta "
        "archivos huérfanos. Cero colisión empírica en 2 sprints "
        "consecutivos (86.7 y 86.8)."
    ),
    "criterio_promocion": (
        "Promover a semilla canónica tras 3+ sprints consecutivos "
        "paralelos sin colisión de archivos."
    ),
    "evidencia_empirica": [
        {
            "sprint": "86.7",
            "fecha": "2026-05-05",
            "hilos_paralelos": ["Manus Catastro", "Ejecutor"],
            "zonas": {
                "Catastro": ["kernel/catastro/"],
                "Ejecutor": ["kernel/e2e/", "kernel/main.py"],
            },
            "conflictos_rebase": 0,
            "antidory_detecciones": 5,
        },
        {
            "sprint": "86.8",
            "fecha": "2026-05-05",
            "hilos_paralelos": ["Manus Catastro", "Memento (Sprint 87.1)"],
            "zonas": {
                "Catastro": ["kernel/catastro/recommendation.py", "scripts/027_*"],
                "Memento": ["kernel/embriones/"],
            },
            "conflictos_rebase": 0,
            "antidory_detecciones": 0,
        },
    ],
    "modos_de_fallo_conocidos": [
        "Archivo puente compartido (ej. kernel/main.py) que ambos sprints requieren",
        "Spec sin declaracion explicita de zona → asunciones divergentes",
        "Refactor de scope que rompe la zonificacion firmada",
    ],
    "mitigaciones": [
        "Cowork detecta colision via git log --stat antes de aprobar",
        "Re-firma spec con division mas fina extrayendo archivo puente",
        "git commit --amend --author=... para preservar autoria dual",
    ],
}


if __name__ == "__main__":
    import json
    print(json.dumps(SEMILLA, indent=2, ensure_ascii=False))
