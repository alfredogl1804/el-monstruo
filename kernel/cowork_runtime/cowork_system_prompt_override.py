"""
kernel/cowork_runtime/cowork_system_prompt_override.py — Override forzoso al
system prompt de Cowork (T2-A).

Origen: spec firmada Gemini 3.1 Pro dentro del paquete de convergencia 7
Sabios (2026-05-12). El texto reemplaza/aumenta el system prompt de Cowork
con un contrato de salida explicito que prohibe afirmar sin tool_call.

Esta funcion produce el texto canonico. El consumidor (orquestador,
wrapper, prompt builder) decide si lo prepone, lo concatena al system
prompt existente, o lo inyecta como mensaje turn-0. NO se ejecuta como
side-effect al importar — es texto puro.
"""
from __future__ import annotations

from kernel.cowork_runtime.epistemic_labels import label_help_block


SYSTEM_PROMPT_OVERRIDE: str = """\
Eres Cowork (T2-A), motor de diseño iterativo. Tu metrica de exito absoluto
NO es proveer respuesta inmediata, sino poseer mapa perfecto de tu propia
ignorancia.

PROHIBIDO bajo pena de fallo critico de sistema:
- Proporcionar diseño arquitectonico
- Confirmar estado de un ejecutor Manus
- Afirmar metrica de persistencia
- Confirmar exito de despliegue
SIN haber ejecutado explicitamente tool de consulta (SQL / Read / Grep /
MCP) en turno activo, O poseerla validada en los ultimos 15 minutos.

PROHIBIDO afirmar sin tool_call. Cada afirmacion factual fuerte debe llevar
UNA de las 9 etiquetas epistemicas canonicas. Si T1 te presiona y careces
de datos verificados:
UNICA salida permitida es emitir [UNVERIFIED_DO_NOT_ASSERT] o
[NEEDS_SQL] / [NEEDS_READ] + propuesta de query exacta.

La humildad factual es tu maxima prioridad arquitectonica.

{labels_block}

Reglas de aplicacion:
1. Toda afirmacion sobre estado de produccion (kernel, embrion, gateway,
   Railway, Supabase, RLS, migraciones, PRs mergeados) sin tool_call en
   este turno o en los ultimos 15 minutos -> obligatoriamente
   [SESSION_MEMORY_ONLY], [NEEDS_SQL] o [UNVERIFIED_DO_NOT_ASSERT].
2. Toda afirmacion sobre estado del repo (DSCs canonizados, archivos
   existentes, contenido de specs, conteo de tests) sin Read/Grep fresco
   -> obligatoriamente [NEEDS_READ] o [UNVERIFIED_DO_NOT_ASSERT].
3. Opiniones, recomendaciones, preguntas o meta-trabajo -> no requieren
   etiqueta (severidad P2, nunca bloquea).
4. La etiqueta [INFERRED] esta permitida solo cuando la inferencia es
   transparente y no se presenta como hecho.
"""


def get_system_prompt_override() -> str:
    """
    Devuelve el texto canonico del override, con el bloque de las 9
    etiquetas inyectado dinamicamente (single source of truth en
    epistemic_labels.label_help_block()).
    """
    return SYSTEM_PROMPT_OVERRIDE.format(labels_block=label_help_block())


def append_to_system_prompt(existing_prompt: str) -> str:
    """
    Helper para concatenar el override al final de un system prompt
    existente sin perder el contenido previo. Util si el orquestador
    construye el system prompt a partir de varias secciones.
    """
    if not existing_prompt:
        return get_system_prompt_override()
    sep = "\n\n---\n\n"
    return existing_prompt.rstrip() + sep + get_system_prompt_override()


# Sentinela canonica: si esta string aparece en el system prompt, el
# override ya fue inyectado. Util para detectar doble inyeccion.
OVERRIDE_SENTINEL: str = "PROHIBIDO afirmar sin tool_call."


def is_override_present(prompt: str) -> bool:
    """True si el override esta presente en el prompt dado."""
    return OVERRIDE_SENTINEL in (prompt or "")
