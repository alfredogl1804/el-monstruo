#!/usr/bin/env python3.11
"""
validar_sintesis.py — Paso 7: Validación Post-Síntesis en Tiempo Real
=======================================================================
Se ejecuta DESPUÉS de que GPT-5.4 genera la síntesis final (Paso 6).
Cierra el ciclo de verificación que antes quedaba abierto.

Tres capas de validación:
    1. Extracción de afirmaciones clave de la síntesis final
    2. Verificación independiente con Gemini (grounding) + Grok (segunda opinión)
       → NO usa Perplexity para evitar dependencia circular con Paso 5
    3. Cross-validation: ¿la síntesis incorporó las correcciones del informe de validación?

Si hay discrepancias graves, genera una síntesis corregida automáticamente.

Uso:
    python3.11 validar_sintesis.py \\
        --sintesis /ruta/sintesis_final.md \\
        --informe-validacion /ruta/informe_validacion.md \\
        --output /ruta/validacion_sintesis.md \\
        [--corregir] \\
        [--profundidad rapida|normal|profunda]

Creado: 2026-04-09 (Paso 7 — cierre del ciclo de verificación)
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import consultar_sabio

# Semáforo para limitar concurrencia de verificaciones
VERIFY_SEMAPHORE = asyncio.Semaphore(3)


# ═══════════════════════════════════════════════════════════════════
# CAPA 1: Extraer afirmaciones clave de la síntesis
# ═══════════════════════════════════════════════════════════════════

SYSTEM_EXTRACTOR_SINTESIS = """Eres un fact-checker de élite. Tu tarea es analizar una SÍNTESIS FINAL
generada por un orquestador de IA y extraer las afirmaciones más críticas que podrían
contener errores introducidos durante la síntesis.

CONTEXTO IMPORTANTE: Esta síntesis fue generada por GPT-5.4 a partir de respuestas de
6 modelos de IA. El orquestador pudo haber:
- Introducido errores propios al sintetizar
- Ignorado correcciones del informe de validación
- Confundido datos de diferentes sabios
- Inventado consensos que no existían

Responde ÚNICAMENTE con un JSON válido:
{
    "afirmaciones_criticas": [
        {
            "texto": "La afirmación textual exacta de la síntesis",
            "seccion": "Sección donde aparece",
            "tipo": "dato_numerico|tecnologia|regulacion|herramienta|fecha|precio|recomendacion|consenso",
            "query_verificacion": "Query en inglés para verificar en tiempo real",
            "riesgo": "alto|medio|bajo",
            "razon_riesgo": "Por qué esta afirmación podría ser incorrecta"
        }
    ],
    "consensos_declarados": [
        {
            "texto": "Consenso que la síntesis declara entre los sabios",
            "verificable": true,
            "nota": "Cómo verificar si realmente hubo consenso"
        }
    ]
}

Reglas:
- Máximo 8 afirmaciones para "rapida", 15 para "normal", 25 para "profunda"
- Prioriza afirmaciones que la síntesis presenta como HECHOS, no como opiniones
- Las queries deben ser en inglés para máxima cobertura
- Incluye al menos 2 "consensos_declarados" si la síntesis menciona acuerdos entre sabios"""


PROFUNDIDAD_LIMITES = {
    "rapida": {"afirmaciones": 8, "consensos": 3},
    "normal": {"afirmaciones": 15, "consensos": 5},
    "profunda": {"afirmaciones": 25, "consensos": 8},
}


async def extraer_afirmaciones_sintesis(sintesis: str, profundidad: str) -> dict:
    """Grok extrae afirmaciones verificables de la síntesis final.
    Usa Grok (no GPT-5.4) para evitar que el mismo modelo que sintetizó
    sea el que evalúe su propia síntesis."""
    print("  Capa 1: Extrayendo afirmaciones clave de la sintesis...")

    limites = PROFUNDIDAD_LIMITES.get(profundidad, PROFUNDIDAD_LIMITES["normal"])

    prompt = f"""Analiza la siguiente SINTESIS FINAL generada por GPT-5.4 como orquestador.
Fecha de hoy: {datetime.now().strftime("%d de %B de %Y")}
Profundidad: {profundidad} (max {limites["afirmaciones"]} afirmaciones, {limites["consensos"]} consensos)

SINTESIS A ANALIZAR:
---
{sintesis[:80000]}
---

Extrae las afirmaciones mas criticas que podrian contener errores."""

    # Usa GROK como extractor (evita auto-evaluacion de GPT-5.4)
    resultado = await consultar_sabio(
        sabio_id="grok",
        prompt=prompt,
        system=SYSTEM_EXTRACTOR_SINTESIS,
        reintentos=2,
    )

    if not resultado["exito"]:
        # Fallback a Claude
        print("    Grok fallo, intentando con Claude...")
        resultado = await consultar_sabio(
            sabio_id="claude",
            prompt=prompt,
            system=SYSTEM_EXTRACTOR_SINTESIS,
            reintentos=2,
        )

    if not resultado["exito"]:
        print(f"    Error al extraer: {resultado.get('error', '?')[:100]}")
        return {"afirmaciones_criticas": [], "consensos_declarados": []}

    try:
        texto = resultado["respuesta"]
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0]
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0]
        datos = json.loads(texto.strip())
        n_af = len(datos.get("afirmaciones_criticas", []))
        n_co = len(datos.get("consensos_declarados", []))
        print(f"    {n_af} afirmaciones criticas, {n_co} consensos declarados")
        return datos
    except (json.JSONDecodeError, IndexError) as e:
        print(f"    Error parseando JSON: {str(e)[:100]}")
        return {"afirmaciones_criticas": [], "consensos_declarados": []}


# ═══════════════════════════════════════════════════════════════════
# CAPA 2: Verificación independiente (Gemini + Grok, NO Perplexity)
# ═══════════════════════════════════════════════════════════════════


async def verificar_con_gemini(afirmacion: dict) -> dict:
    """Verifica una afirmacion usando Gemini (con grounding/search capabilities).
    Gemini tiene acceso a Google Search integrado, lo que lo hace ideal
    para verificacion factual independiente de Perplexity."""

    prompt = f"""Verifica si la siguiente afirmacion es correcta al dia de hoy ({datetime.now().strftime("%d de %B de %Y")}):

AFIRMACION: "{afirmacion["texto"]}"
TIPO: {afirmacion["tipo"]}
SECCION: {afirmacion.get("seccion", "N/A")}
QUERY DE VERIFICACION: {afirmacion["query_verificacion"]}

Responde de forma estructurada:
1. VEREDICTO: correcta | parcialmente_correcta | incorrecta | no_verificable
2. EVIDENCIA: Datos concretos que respaldan tu veredicto (max 150 palabras)
3. CORRECCION: Si es incorrecta o parcialmente correcta, cual es la informacion correcta
4. CONFIANZA: alta | media | baja
5. FUENTES: Menciona fuentes si las conoces"""

    async with VERIFY_SEMAPHORE:
        resultado = await consultar_sabio(
            sabio_id="gemini",
            prompt=prompt,
            system="Eres un verificador de hechos riguroso. Verifica contra datos actuales. Se preciso y conciso.",
            reintentos=2,
        )

    return {
        "afirmacion": afirmacion["texto"],
        "seccion": afirmacion.get("seccion", "N/A"),
        "tipo": afirmacion["tipo"],
        "riesgo": afirmacion["riesgo"],
        "verificacion_gemini": resultado["respuesta"] if resultado["exito"] else "No se pudo verificar con Gemini",
        "exito_gemini": resultado["exito"],
        "verificador": "Gemini 3.1 Pro (Google Search grounding)",
    }


async def segunda_opinion_grok(afirmacion: dict, verificacion_gemini: str) -> dict:
    """Grok da segunda opinion SOLO en afirmaciones de riesgo alto
    donde Gemini reporto problemas."""

    prompt = f"""Un verificador (Gemini) reviso la siguiente afirmacion y encontro posibles problemas.
Dame tu opinion independiente.

AFIRMACION ORIGINAL: "{afirmacion["texto"]}"
TIPO: {afirmacion["tipo"]}

VERIFICACION DE GEMINI:
{verificacion_gemini[:2000]}

Tu tarea:
1. Confirmas o contradices la verificacion de Gemini?
2. Tienes informacion adicional que cambie el veredicto?
3. Cual es tu veredicto final: correcta | parcialmente_correcta | incorrecta | no_verificable

Se conciso (max 200 palabras)."""

    async with VERIFY_SEMAPHORE:
        resultado = await consultar_sabio(
            sabio_id="grok",
            prompt=prompt,
            system="Eres un analista critico. Da tu opinion honesta e independiente.",
            reintentos=1,
        )

    return {
        "segunda_opinion": resultado["respuesta"] if resultado["exito"] else "Sin segunda opinion",
        "exito_grok": resultado["exito"],
    }


async def verificar_afirmacion_completa(afirmacion: dict) -> dict:
    """Pipeline completo de verificacion: Gemini primero, Grok si es riesgo alto."""

    # Paso 1: Gemini verifica
    resultado = await verificar_con_gemini(afirmacion)

    # Paso 2: Si es riesgo alto Y Gemini detecto problemas, pedir segunda opinion a Grok
    necesita_segunda = (
        afirmacion["riesgo"] == "alto"
        and resultado["exito_gemini"]
        and any(
            kw in resultado["verificacion_gemini"].lower()
            for kw in ["incorrecta", "parcialmente", "desactualizada", "no es correcta", "error"]
        )
    )

    if necesita_segunda:
        print(f"      Segunda opinion (Grok) para: {afirmacion['texto'][:60]}...")
        segunda = await segunda_opinion_grok(afirmacion, resultado["verificacion_gemini"])
        resultado["segunda_opinion_grok"] = segunda["segunda_opinion"]
        resultado["tiene_segunda_opinion"] = True
    else:
        resultado["segunda_opinion_grok"] = None
        resultado["tiene_segunda_opinion"] = False

    return resultado


# ═══════════════════════════════════════════════════════════════════
# CAPA 3: Cross-validation contra informe de validación original
# ═══════════════════════════════════════════════════════════════════

SYSTEM_CROSS_VALIDATOR = """Eres un auditor de calidad. Tu tarea es comparar una SINTESIS FINAL
contra un INFORME DE VALIDACION que fue generado previamente.

El informe de validacion contiene correcciones y datos actualizados que el
orquestador (GPT-5.4) DEBIA incorporar en la sintesis.

Tu trabajo: verificar si la sintesis incorporo las correcciones o las ignoro.

Responde UNICAMENTE con un JSON valido:
{
    "correcciones_incorporadas": [
        {
            "correccion": "Descripcion de la correccion del informe",
            "incorporada": true,
            "evidencia": "Donde en la sintesis se refleja"
        }
    ],
    "correcciones_ignoradas": [
        {
            "correccion": "Descripcion de la correccion ignorada",
            "impacto": "alto|medio|bajo",
            "texto_incorrecto_en_sintesis": "Lo que dice la sintesis (incorrecto)",
            "texto_correcto_segun_informe": "Lo que deberia decir"
        }
    ],
    "score_incorporacion": 0.85,
    "veredicto": "La sintesis incorporo X de Y correcciones. Resumen en 1 linea."
}"""


async def cross_validate(sintesis: str, informe_validacion: str) -> dict:
    """Compara la sintesis contra el informe de validacion para detectar
    correcciones ignoradas."""
    print("  Capa 3: Cross-validando sintesis vs informe de validacion...")

    if not informe_validacion or len(informe_validacion.strip()) < 100:
        print("    Informe de validacion vacio o muy corto. Omitiendo cross-validation.")
        return {
            "correcciones_incorporadas": [],
            "correcciones_ignoradas": [],
            "score_incorporacion": 1.0,
            "veredicto": "No habia correcciones que incorporar.",
            "omitida": True,
        }

    prompt = f"""Compara la SINTESIS FINAL contra el INFORME DE VALIDACION.

SINTESIS FINAL:
---
{sintesis[:60000]}
---

INFORME DE VALIDACION (correcciones que debian incorporarse):
---
{informe_validacion[:30000]}
---

Identifica que correcciones se incorporaron y cuales se ignoraron."""

    # Usa Claude para cross-validation (neutral — no es GPT-5.4 ni los verificadores)
    resultado = await consultar_sabio(
        sabio_id="claude",
        prompt=prompt,
        system=SYSTEM_CROSS_VALIDATOR,
        reintentos=2,
    )

    if not resultado["exito"]:
        # Fallback a Gemini
        resultado = await consultar_sabio(
            sabio_id="gemini",
            prompt=prompt,
            system=SYSTEM_CROSS_VALIDATOR,
            reintentos=2,
        )

    if not resultado["exito"]:
        return {
            "correcciones_incorporadas": [],
            "correcciones_ignoradas": [],
            "score_incorporacion": -1,
            "veredicto": "No se pudo realizar cross-validation.",
            "error": resultado.get("error", "?"),
        }

    try:
        texto = resultado["respuesta"]
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0]
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0]
        datos = json.loads(texto.strip())
        inc = len(datos.get("correcciones_incorporadas", []))
        ign = len(datos.get("correcciones_ignoradas", []))
        score = datos.get("score_incorporacion", -1)
        print(f"    {inc} incorporadas, {ign} ignoradas, score: {score}")
        return datos
    except (json.JSONDecodeError, IndexError) as e:
        print(f"    Error parseando JSON: {str(e)[:100]}")
        return {
            "correcciones_incorporadas": [],
            "correcciones_ignoradas": [],
            "score_incorporacion": -1,
            "veredicto": f"Error de parseo: {str(e)[:100]}",
        }


# ═══════════════════════════════════════════════════════════════════
# COMPILADOR DE INFORME POST-SÍNTESIS
# ═══════════════════════════════════════════════════════════════════


def compilar_informe_post_sintesis(
    verificaciones: list,
    cross_result: dict,
    sintesis_original: str,
) -> tuple:
    """Compila el informe de validacion post-sintesis.
    Retorna (informe_md, necesita_correccion, problemas_graves)."""

    timestamp = datetime.now().strftime("%d de %B de %Y, %H:%M")

    # Clasificar verificaciones
    problemas = []
    confirmadas = []
    no_verificables = []

    for v in verificaciones:
        texto_v = v.get("verificacion_gemini", "").lower()
        if any(kw in texto_v for kw in ["incorrecta", "error", "no es correcta", "falsa"]):
            problemas.append(v)
        elif any(kw in texto_v for kw in ["parcialmente", "desactualizada", "matiz"]):
            problemas.append(v)
        elif "no_verificable" in texto_v or "no se pudo" in texto_v:
            no_verificables.append(v)
        else:
            confirmadas.append(v)

    # Evaluar cross-validation
    correcciones_ignoradas = cross_result.get("correcciones_ignoradas", [])
    score_incorporacion = cross_result.get("score_incorporacion", 1.0)
    graves_ignoradas = [c for c in correcciones_ignoradas if c.get("impacto") == "alto"]

    # Determinar si necesita correccion
    necesita_correccion = (
        len(problemas) >= 3 or len(graves_ignoradas) >= 1 or (score_incorporacion >= 0 and score_incorporacion < 0.6)
    )

    # Calcular score global
    total_verif = len(verificaciones) if verificaciones else 1
    score_factual = len(confirmadas) / total_verif
    score_cross = score_incorporacion if score_incorporacion >= 0 else 1.0
    score_global = round((score_factual * 0.6 + score_cross * 0.4), 2)

    lines = [
        "# Informe de Validacion Post-Sintesis (Paso 7)",
        "",
        f"**Fecha:** {timestamp}",
        f"**Score global:** {score_global} / 1.00",
        f"**Score factual:** {score_factual:.2f} ({len(confirmadas)}/{total_verif} confirmadas)",
        f"**Score incorporacion:** {score_cross:.2f}",
        f"**Necesita correccion:** {'SI' if necesita_correccion else 'NO'}",
        "",
        "> Este informe fue generado por el Paso 7 del pipeline de consulta-sabios.",
        "> Verifica la sintesis final DESPUES de que GPT-5.4 la genero, usando",
        "> Gemini (grounding) y Grok (segunda opinion) como verificadores independientes.",
        "",
    ]

    # Seccion 1: Problemas detectados
    if problemas:
        lines.append("## Problemas Detectados en la Sintesis")
        lines.append("")
        for i, p in enumerate(problemas, 1):
            riesgo_tag = f"[{p['riesgo'].upper()}]" if p.get("riesgo") else ""
            lines.append(f"### {i}. {riesgo_tag} {p['afirmacion'][:100]}")
            lines.append("")
            lines.append(f"**Seccion:** {p.get('seccion', 'N/A')}")
            lines.append(f"**Tipo:** {p.get('tipo', 'N/A')}")
            lines.append("")
            lines.append("**Verificacion (Gemini):**")
            lines.append(p.get("verificacion_gemini", "N/A"))
            lines.append("")
            if p.get("tiene_segunda_opinion") and p.get("segunda_opinion_grok"):
                lines.append("**Segunda opinion (Grok):**")
                lines.append(p["segunda_opinion_grok"])
                lines.append("")
            lines.append("---")
            lines.append("")

    # Seccion 2: Afirmaciones confirmadas
    if confirmadas:
        lines.append("## Afirmaciones Confirmadas")
        lines.append("")
        for c in confirmadas:
            lines.append(f"- **{c['afirmacion'][:80]}** — Confirmada por {c['verificador']}")
        lines.append("")

    # Seccion 3: Cross-validation
    lines.append("## Cross-Validation: Sintesis vs Informe de Validacion")
    lines.append("")

    if cross_result.get("omitida"):
        lines.append("Cross-validation omitida (no habia informe de validacion previo).")
    else:
        lines.append(f"**Veredicto:** {cross_result.get('veredicto', 'N/A')}")
        lines.append(f"**Score de incorporacion:** {score_incorporacion}")
        lines.append("")

        if correcciones_ignoradas:
            lines.append("### Correcciones Ignoradas por la Sintesis")
            lines.append("")
            for c in correcciones_ignoradas:
                impacto = c.get("impacto", "?")
                lines.append(f"- **[{impacto.upper()}]** {c.get('correccion', 'N/A')}")
                if c.get("texto_incorrecto_en_sintesis"):
                    lines.append(f'  - Sintesis dice: "{c["texto_incorrecto_en_sintesis"][:100]}"')
                if c.get("texto_correcto_segun_informe"):
                    lines.append(f'  - Deberia decir: "{c["texto_correcto_segun_informe"][:100]}"')
            lines.append("")

        inc = cross_result.get("correcciones_incorporadas", [])
        if inc:
            lines.append(f"### Correcciones Correctamente Incorporadas ({len(inc)})")
            lines.append("")
            for c in inc:
                lines.append(f"- {c.get('correccion', 'N/A')}")
            lines.append("")

    # Seccion 4: Resumen ejecutivo
    lines.append("## Resumen Ejecutivo")
    lines.append("")

    if necesita_correccion:
        lines.append("**ACCION REQUERIDA:** La sintesis tiene problemas significativos que requieren correccion.")
        lines.append("")
        lines.append("Razones:")
        if len(problemas) >= 3:
            lines.append(f"- {len(problemas)} afirmaciones con problemas factuales")
        if len(graves_ignoradas) >= 1:
            lines.append(f"- {len(graves_ignoradas)} correcciones de alto impacto fueron ignoradas")
        if score_incorporacion >= 0 and score_incorporacion < 0.6:
            lines.append(f"- Score de incorporacion bajo: {score_incorporacion:.2f}")
    else:
        lines.append(
            "**SINTESIS APROBADA.** Los problemas detectados (si los hay) son menores y no comprometen la integridad del documento."
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generado por validar_sintesis.py — Paso 7 del pipeline consulta-sabios*")
    lines.append(
        "*Verificadores: Gemini 3.1 Pro (primario), Grok 4.20 (segunda opinion), Claude Opus 4.7 (cross-validation)*"
    )

    informe = "\n".join(lines)
    return informe, necesita_correccion, problemas


# ═══════════════════════════════════════════════════════════════════
# CORRECCIÓN AUTOMÁTICA DE SÍNTESIS
# ═══════════════════════════════════════════════════════════════════

SYSTEM_CORRECTOR = """Eres un editor de precision. Tu tarea es corregir una sintesis final
basandote en un informe de validacion post-sintesis que detalla errores factuales
y correcciones ignoradas.

REGLAS ABSOLUTAS:
1. NO reescribas la sintesis completa — solo corrige los errores identificados
2. Mantén la estructura, tono y formato original
3. Marca cada correccion con [CORREGIDO] al inicio del parrafo modificado
4. Si una correccion es ambigua, agrega una nota [NOTA: ...] en lugar de cambiar el texto
5. Al final, agrega una seccion "## Correcciones Aplicadas (Paso 7)" listando cada cambio"""


async def corregir_sintesis(sintesis: str, informe_post: str) -> dict:
    """Corrige la sintesis basandose en el informe de validacion post-sintesis."""
    print("\n  Correccion automatica de la sintesis...")

    prompt = f"""Corrige la siguiente sintesis basandote en el informe de validacion post-sintesis.

SINTESIS ORIGINAL:
---
{sintesis[:80000]}
---

INFORME DE VALIDACION POST-SINTESIS (errores detectados):
---
{informe_post[:30000]}
---

Aplica las correcciones necesarias siguiendo las reglas del system prompt."""

    # GPT-5.4 corrige (es el mejor para edicion precisa)
    resultado = await consultar_sabio(
        sabio_id="gpt54",
        prompt=prompt,
        system=SYSTEM_CORRECTOR,
        reintentos=2,
    )

    if not resultado["exito"]:
        # Fallback a Claude
        resultado = await consultar_sabio(
            sabio_id="claude",
            prompt=prompt,
            system=SYSTEM_CORRECTOR,
            reintentos=2,
        )

    return {
        "sintesis_corregida": resultado["respuesta"] if resultado["exito"] else None,
        "exito": resultado["exito"],
        "corrector": resultado.get("sabio", "desconocido"),
        "error": resultado.get("error"),
    }


# ═══════════════════════════════════════════════════════════════════
# ORQUESTADOR PRINCIPAL DEL PASO 7
# ═══════════════════════════════════════════════════════════════════


async def ejecutar_paso_7(
    sintesis_path: str,
    informe_validacion_path: str,
    output_path: str,
    corregir: bool = True,
    profundidad: str = "normal",
) -> dict:
    """Ejecuta el Paso 7 completo: validacion post-sintesis.

    Returns:
        dict con: score_global, necesita_correccion, correccion_aplicada, paths
    """
    print("\n" + "=" * 60)
    print("  PASO 7: VALIDACION POST-SINTESIS")
    print(f"  Profundidad: {profundidad}")
    print(f"  Correccion automatica: {'SI' if corregir else 'NO'}")
    print("=" * 60)

    # Leer archivos
    with open(sintesis_path, "r", encoding="utf-8") as f:
        sintesis = f.read()

    informe_validacion = ""
    if informe_validacion_path and Path(informe_validacion_path).exists():
        with open(informe_validacion_path, "r", encoding="utf-8") as f:
            informe_validacion = f.read()

    output_dir = Path(output_path).parent

    # CAPA 1: Extraer afirmaciones
    print("\n--- Capa 1: Extraccion de afirmaciones ---")
    datos = await extraer_afirmaciones_sintesis(sintesis, profundidad)
    afirmaciones = datos.get("afirmaciones_criticas", [])
    consensos = datos.get("consensos_declarados", [])

    print(f"  Afirmaciones a verificar: {len(afirmaciones)}")
    print(f"  Consensos declarados: {len(consensos)}")

    # CAPA 2: Verificacion independiente
    print("\n--- Capa 2: Verificacion independiente (Gemini + Grok) ---")
    if afirmaciones:
        tareas = [verificar_afirmacion_completa(af) for af in afirmaciones]
        verificaciones = await asyncio.gather(*tareas)
        exitosas = sum(1 for v in verificaciones if v.get("exito_gemini"))
        print(f"  {exitosas}/{len(verificaciones)} verificaciones completadas")
    else:
        verificaciones = []
        print("  Sin afirmaciones que verificar")

    # CAPA 3: Cross-validation
    print("\n--- Capa 3: Cross-validation ---")
    cross_result = await cross_validate(sintesis, informe_validacion)

    # COMPILAR INFORME
    print("\n--- Compilando informe post-sintesis ---")
    informe, necesita_correccion, problemas = compilar_informe_post_sintesis(verificaciones, cross_result, sintesis)

    # Guardar informe
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(informe)
    print(f"  Informe guardado: {output_path} ({len(informe):,} chars)")

    # CORRECCION AUTOMATICA si es necesario y esta habilitada
    correccion_aplicada = False
    sintesis_corregida_path = None

    if necesita_correccion and corregir:
        print("\n--- Correccion automatica ---")
        resultado_correccion = await corregir_sintesis(sintesis, informe)

        if resultado_correccion["exito"] and resultado_correccion["sintesis_corregida"]:
            sintesis_corregida_path = str(output_dir / "sintesis_corregida.md")
            with open(sintesis_corregida_path, "w", encoding="utf-8") as f:
                f.write(resultado_correccion["sintesis_corregida"])
            correccion_aplicada = True
            print(f"  Sintesis corregida guardada: {sintesis_corregida_path}")
            print(f"  Corrector: {resultado_correccion['corrector']}")
        else:
            print(f"  Error en correccion: {resultado_correccion.get('error', '?')[:100]}")
    elif necesita_correccion and not corregir:
        print("\n  ATENCION: La sintesis necesita correccion pero --corregir no esta habilitado.")

    # Calcular scores
    total_verif = len(verificaciones) if verificaciones else 1
    confirmadas = sum(
        1
        for v in verificaciones
        if not any(
            kw in v.get("verificacion_gemini", "").lower()
            for kw in ["incorrecta", "parcialmente", "error", "no es correcta"]
        )
    )
    score_factual = confirmadas / total_verif
    score_cross = cross_result.get("score_incorporacion", 1.0)
    if score_cross < 0:
        score_cross = 1.0
    score_global = round((score_factual * 0.6 + score_cross * 0.4), 2)

    resultado = {
        "score_global": score_global,
        "score_factual": round(score_factual, 2),
        "score_incorporacion": round(score_cross, 2),
        "afirmaciones_verificadas": len(verificaciones),
        "afirmaciones_con_problemas": len(problemas),
        "correcciones_ignoradas": len(cross_result.get("correcciones_ignoradas", [])),
        "necesita_correccion": necesita_correccion,
        "correccion_aplicada": correccion_aplicada,
        "informe_path": output_path,
        "sintesis_corregida_path": sintesis_corregida_path,
    }

    # Resumen
    print("\n" + "=" * 60)
    print("  PASO 7 COMPLETADO")
    print(f"  Score global: {score_global}")
    print(f"  Score factual: {score_factual:.2f}")
    print(f"  Score incorporacion: {score_cross:.2f}")
    print(f"  Necesita correccion: {'SI' if necesita_correccion else 'NO'}")
    print(f"  Correccion aplicada: {'SI' if correccion_aplicada else 'NO'}")
    print("=" * 60)

    return resultado


# ═══════════════════════════════════════════════════════════════════
# MAIN — CLI
# ═══════════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(
        description="Paso 7: Validacion Post-Sintesis en Tiempo Real",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
    python3.11 validar_sintesis.py \\
        --sintesis /tmp/consulta/sintesis_final.md \\
        --informe-validacion /tmp/consulta/informe_validacion.md \\
        --output /tmp/consulta/validacion_sintesis.md \\
        --corregir
        """,
    )
    parser.add_argument("--sintesis", required=True, help="Ruta a la sintesis final (Paso 6)")
    parser.add_argument("--informe-validacion", default=None, help="Ruta al informe de validacion (Paso 5)")
    parser.add_argument("--output", required=True, help="Ruta de salida para el informe post-sintesis")
    parser.add_argument("--corregir", action="store_true", help="Generar sintesis corregida si hay problemas graves")
    parser.add_argument("--profundidad", choices=["rapida", "normal", "profunda"], default="normal")

    args = parser.parse_args()

    resultado = await ejecutar_paso_7(
        sintesis_path=args.sintesis,
        informe_validacion_path=args.informe_validacion,
        output_path=args.output,
        corregir=args.corregir,
        profundidad=args.profundidad,
    )

    # Guardar metadata
    meta_path = Path(args.output).parent / "paso7_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata guardada: {meta_path}")


if __name__ == "__main__":
    asyncio.run(main())
