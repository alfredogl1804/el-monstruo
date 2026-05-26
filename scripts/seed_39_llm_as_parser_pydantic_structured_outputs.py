r"""
Semilla #39 — LLM-as-parser con Pydantic Structured Outputs (anti-regex)
              (Sprint 86.5 — Catastro Macroárea 3 LLM Coding)

Lección a sembrar en la base error_memory:
  Cuando se necesita parsear o clasificar texto generado por LLMs
  (descripciones, releases, chain-of-thought, tags semánticos), NUNCA
  usar regex. Los regex sobre Markdown/texto LLM-generated son
  INESTABLES porque el LLM cambia formato silenciosamente entre runs
  (e.g., agrega un emoji, rompe sintaxis, cambia mayúsculas, etc.).

  El patrón ganador es **LLM-as-parser con Pydantic Structured Outputs**:
    1. Definir un Pydantic BaseModel con los campos esperados.
    2. Llamar al LLM con `client.beta.chat.completions.parse(
         model="...", messages=[...], response_format=MyModel
       )`.
    3. Validar el output contra un vocabulario controlado (whitelist).
    4. Fallback heurístico determinístico si el LLM no está disponible
       (capa Memento: degradación graciosa, no bloqueante).

Origen:
  - Trío A+B+C (Cowork audit Sprint 86.5 pre-investigación):
    * 27va semilla del Cowork (Spec Integración Radar): regex sobre
      Markdown LLM-generated del Radar es inestable. Solución: LLM-as-
      parser con Pydantic Structured Outputs.
    * 39va semilla extiende el patrón al `coding_classifier.py` del
      Catastro Macroárea 3.
  - Patrón documentado en `bridge/sprint86_5_preinvestigation/`
    `spec_integracion_radar_catastro.md` (decisión arquitectónica firmada).

Aplicaciones del patrón:
  1. coding_classifier.py (Sprint 86.5): clasifica modelos LLM por
     subcapacidades de coding usando un vocabulario controlado de 15 tags.
  2. radar_classifier.py (Sprint 86.7+, futuro): clasificará releases del
     Radar a estructuras tipadas para `catastro_repos`.
  3. Cualquier otro classifier futuro sobre texto LLM-generated.

Anti-pattern detectado en sprints previos:
  - Regex `r"^- \*\*(\w+)\*\*: (.+)$"` para parsear bullets de Markdown.
  - Falló cuando el LLM cambió a `r"^- (\w+) — (.+)$"` (sin asteriscos).
  - Pérdida silenciosa de datos. NUNCA detectado por tests porque los
    fixtures eran estáticos del primer run.

Disciplina anti-Dory aplicada:
  - El patrón se documenta en error_memory ANTES de que aparezca el bug.
  - El Cowork audit del trío A+B+C identificó el riesgo, NO el incidente.
  - Si en sprints futuros alguien propone regex sobre texto LLM-generated,
    el Guardian debe rechazarlo automáticamente (Sprint 89+).

Capa Memento:
  - El classifier siempre tiene fallback heurístico determinístico.
  - Si OPENAI_API_KEY ausente: usa heuristic (bajo confianza, no rompe).
  - Si LLM falla en runtime: catch + log warning + heuristic fallback.
  - Anti-Dory: el classifier NO bloquea el pipeline aunque el LLM no
    esté disponible.

Validación cruzada (Quorum 2-de-3 en mente):
  - El output del classifier NO es la única fuente de verdad.
  - Los scores numéricos (SWE-bench, HumanEval+, MBPP+) siguen siendo
    el ancla de quorum. El classifier solo asigna **subcapacidades
    semánticas**, no scores absolutos.

[Hilo Manus Catastro] · Sprint 86.5 · 2026-05-05
"""

from __future__ import annotations

# Esta semilla NO ejecuta nada. Es metadata consumida por el sistema
# de error_memory en su próximo refresh. Ver scripts/seed_*.py para
# patrón completo (todas las semillas son archivos de documentación
# estructurada, no scripts ejecutables).

SEMILLA_ID = "39_llm_as_parser_pydantic_structured_outputs"
SEMILLA_TITULO = "LLM-as-parser con Pydantic Structured Outputs (anti-regex)"
SEMILLA_SPRINT = "86.5"
SEMILLA_FECHA = "2026-05-05"
SEMILLA_AUTORIA = "Manus Catastro (Hilo B)"

LECCION_PRINCIPAL = (
    "Para parsear o clasificar texto generado por LLMs, NUNCA usar regex. "
    "Usar LLM-as-parser con Pydantic Structured Outputs + vocabulario "
    "controlado + fallback heuristico. Patron escalado a coding_classifier "
    "(Sprint 86.5) y radar_classifier (Sprint 86.7+ futuro)."
)


def get_semilla_metadata() -> dict:
    """Retorna metadata para que error_memory la consuma."""
    return {
        "id": SEMILLA_ID,
        "titulo": SEMILLA_TITULO,
        "sprint": SEMILLA_SPRINT,
        "fecha": SEMILLA_FECHA,
        "autoria": SEMILLA_AUTORIA,
        "leccion": LECCION_PRINCIPAL,
        "anti_pattern": "regex sobre Markdown LLM-generated",
        "patron_ganador": "LLM-as-parser + Pydantic Structured Outputs + vocabulario controlado + fallback heuristico",
        "aplicaciones": [
            "kernel/catastro/coding_classifier.py (Sprint 86.5)",
            "kernel/catastro/radar_classifier.py (Sprint 86.7+, futuro)",
        ],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(get_semilla_metadata(), indent=2, ensure_ascii=False))
