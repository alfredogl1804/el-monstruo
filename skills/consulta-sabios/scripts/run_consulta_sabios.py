#!/usr/bin/env python3.11
"""
run_consulta_sabios.py — Entrypoint Oficial End-to-End
=======================================================
Orquesta el flujo COMPLETO de consulta a los sabios en una sola ejecución.
Cada paso es obligatorio y se ejecuta en orden. Genera telemetría por run.

Flujo de 7 pasos:
    1. Pre-vuelo (ping) → Valida APIs
    2. Investigación PRE-CONSULTA → Dossier de Realidad
    3. Preparar contexto → Condensar si necesario
    4. Consultar sabios → Modo enjambre/consejo/iterativo
    5. Quality Gate + Validación POST-CONSULTA → Informe de Validación
    6. Síntesis final → GPT-5.4 con informe de validación inyectado
    7. Validación POST-SÍNTESIS → Gemini+Grok verifican, cross-validation, corrección auto

Uso:
    python3.11 run_consulta_sabios.py \\
        --prompt /ruta/al/prompt.md \\
        --output-dir /ruta/salida/ \\
        [--modo enjambre|consejo|iterativo] \\
        [--profundidad-pre rapida|normal|profunda] \\
        [--profundidad-post rapida|normal|profunda] \\
        [--sabios gpt54,claude,gemini,grok,deepseek,perplexity] \\
           [--skip-investigacion]
        [--skip-validacion]
        [--skip-paso7]
        [--profundidad-paso7 rapida|normal|profunda]
        [--no-corregir]

Creado: 2026-04-08 (P0 auditoría sabios)
"""

import argparse
import asyncio
import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import (
    SABIOS, consultar_sabio, consultar_todos, ping_todos, resumen_resultados
)
from telemetry import (
    generate_run_id, create_run_dir, RunTelemetry,
    write_run_artifact, copy_input_artifact, estimate_tokens
)
from quality_gate import evaluate_all, quality_summary, filter_quality


# ═══════════════════════════════════════════════════════════════════
# PASO 1: PRE-VUELO
# ═══════════════════════════════════════════════════════════════════

async def paso_1_prevuelo(tel: RunTelemetry) -> bool:
    """Valida que las 6 APIs estén operativas."""
    tel.start_step("prevuelo")
    print("\n" + "=" * 60)
    print("🏓 PASO 1: PRE-VUELO — Validando APIs")
    print("=" * 60)

    resultados = await ping_todos()
    exitosos = sum(1 for r in resultados if r.get("exito"))
    total = len(resultados)

    print(resumen_resultados(resultados))

    if exitosos < 3:
        print(f"\n🛑 ABORTANDO: Solo {exitosos}/{total} sabios operativos. Mínimo requerido: 3.")
        tel.end_step("prevuelo", success=False, extra={"sabios_ok": exitosos, "sabios_total": total})
        return False

    if exitosos < total:
        print(f"\n⚠️ ADVERTENCIA: {total - exitosos} sabios no disponibles. Continuando con {exitosos}.")

    tel.end_step("prevuelo", success=True, extra={"sabios_ok": exitosos, "sabios_total": total})
    return True


# ═══════════════════════════════════════════════════════════════════
# PASO 2: INVESTIGACIÓN PRE-CONSULTA
# ═══════════════════════════════════════════════════════════════════

async def paso_2_investigacion(
    prompt_path: str, output_dir: Path, profundidad: str, tel: RunTelemetry
) -> str:
    """Ejecuta la investigación en tiempo real."""
    tel.start_step("investigacion_pre")
    print("\n" + "=" * 60)
    print("🔬 PASO 2: INVESTIGACIÓN PRE-CONSULTA")
    print("=" * 60)

    dossier_path = output_dir / "dossier_realidad.md"

    from investigar_contexto import analizar_prompt, investigar_tema_perplexity, compilar_dossier

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()

    analisis = await analizar_prompt(prompt, profundidad)
    temas = analisis.get("temas_a_investigar", [])

    if not temas:
        print("✅ No se requiere investigación en tiempo real.")
        dossier = (
            "# Dossier de Realidad\n\n"
            f"**Fecha:** {datetime.now().strftime('%d de %B de %Y, %H:%M')}\n\n"
            "El análisis determinó que no hay temas que requieran verificación en tiempo real.\n"
        )
        with open(dossier_path, "w", encoding="utf-8") as f:
            f.write(dossier)
        tel.end_step("investigacion_pre", success=True, output_chars=len(dossier),
                     extra={"temas_investigados": 0})
        return str(dossier_path)

    tareas = [investigar_tema_perplexity(t) for t in temas]
    hallazgos = await asyncio.gather(*tareas)
    exitosos = sum(1 for h in hallazgos if h["exito"])

    dossier = compilar_dossier(analisis, hallazgos, prompt)
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write(dossier)

    print(f"✅ Dossier generado: {len(dossier):,} chars ({exitosos}/{len(temas)} temas)")
    tel.end_step("investigacion_pre", success=True, output_chars=len(dossier),
                 extra={"temas_investigados": len(temas), "temas_exitosos": exitosos})
    return str(dossier_path)


# ═══════════════════════════════════════════════════════════════════
# PASO 3: PREPARAR CONTEXTO
# ═══════════════════════════════════════════════════════════════════

async def paso_3_preparar_contexto(
    prompt_path: str, dossier_path: str, output_dir: Path, tel: RunTelemetry
) -> tuple:
    """Combina prompt + dossier y condensa si es necesario."""
    tel.start_step("preparar_contexto")
    print("\n" + "=" * 60)
    print("📦 PASO 3: PREPARAR CONTEXTO")
    print("=" * 60)

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()

    dossier = ""
    if dossier_path and Path(dossier_path).exists():
        with open(dossier_path, "r", encoding="utf-8") as f:
            dossier = f.read()

    # Prompt completo = prompt + dossier
    prompt_completo = prompt
    if dossier:
        prompt_completo += f"\n\n---\n\n{dossier}"

    completo_path = output_dir / "prompt_completo.md"
    with open(completo_path, "w", encoding="utf-8") as f:
        f.write(prompt_completo)

    tokens_est = estimate_tokens(prompt_completo)
    print(f"📄 Prompt completo: {len(prompt_completo):,} chars (~{tokens_est:,} tokens)")

    # Condensar para sabios de 128K si es necesario
    condensado_path = None
    if tokens_est > 30_000:  # ~112K chars → necesita condensación para DeepSeek/Perplexity
        print("📝 Condensando para sabios de 128K (DeepSeek, Perplexity)...")
        from condensar_contexto import condensar

        condensado = await condensar(prompt_completo)
        condensado_path = output_dir / "prompt_condensado.md"
        with open(condensado_path, "w", encoding="utf-8") as f:
            f.write(condensado)
        print(f"✅ Condensado: {len(condensado):,} chars (~{estimate_tokens(condensado):,} tokens)")

    tel.end_step("preparar_contexto", success=True,
                 input_chars=len(prompt_completo),
                 output_chars=len(prompt_completo),
                 extra={"tokens_est": tokens_est, "condensado": condensado_path is not None})

    return str(completo_path), str(condensado_path) if condensado_path else None


# ═══════════════════════════════════════════════════════════════════
# PASO 4: CONSULTAR SABIOS
# ═══════════════════════════════════════════════════════════════════

async def paso_4_consultar(
    completo_path: str, condensado_path: str, output_dir: Path,
    sabios_list: list, system: str, tel: RunTelemetry
) -> list:
    """Consulta a los sabios en paralelo."""
    tel.start_step("consultar_sabios")
    print("\n" + "=" * 60)
    print("🧠 PASO 4: CONSULTAR A LOS SABIOS")
    print("=" * 60)

    with open(completo_path, "r", encoding="utf-8") as f:
        prompt_completo = f.read()

    prompt_condensado = None
    if condensado_path and Path(condensado_path).exists():
        with open(condensado_path, "r", encoding="utf-8") as f:
            prompt_condensado = f.read()

    salida_dir = output_dir / "respuestas"
    salida_dir.mkdir(exist_ok=True)

    resultados = await consultar_todos(
        prompt_completo=prompt_completo,
        prompt_condensado=prompt_condensado,
        system=system,
        sabios=sabios_list,
        guardar_en=str(salida_dir),
    )

    # Registrar métricas por sabio
    for r in resultados:
        tel.record_sabio_metric(r)

    exitosos = sum(1 for r in resultados if r.get("exito"))
    print(f"\n{resumen_resultados(resultados)}")

    # Generar archivo combinado
    combinado_path = output_dir / "respuestas_combinadas.md"
    lines = []
    for r in resultados:
        if r.get("exito"):
            lines.append(f"# Respuesta de {r['sabio']} ({r['modelo']})")
            lines.append(f"*Tiempo: {r['tiempo_seg']}s*\n")
            lines.append(r["respuesta"])
            lines.append("\n---\n")

    with open(combinado_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    tel.end_step("consultar_sabios", success=exitosos >= 3,
                 extra={"sabios_exitosos": exitosos, "sabios_total": len(resultados)})

    return resultados


# ═══════════════════════════════════════════════════════════════════
# PASO 5: QUALITY GATE + VALIDACIÓN POST-CONSULTA
# ═══════════════════════════════════════════════════════════════════

async def paso_5_validacion(
    resultados: list, prompt_path: str, output_dir: Path,
    profundidad: str, skip_validacion: bool, tel: RunTelemetry
) -> str:
    """Evalúa calidad y valida contra realidad actual."""
    tel.start_step("validacion_post")
    print("\n" + "=" * 60)
    print("🔬 PASO 5: QUALITY GATE + VALIDACIÓN POST-CONSULTA")
    print("=" * 60)

    # 5a. Quality Gate
    with open(prompt_path, "r", encoding="utf-8") as f:
        pregunta = f.read()

    evaluaciones = evaluate_all(resultados, pregunta)
    qg_summary = quality_summary(evaluaciones)
    print(f"\n{qg_summary}")

    qg_path = output_dir / "quality_gate.md"
    with open(qg_path, "w", encoding="utf-8") as f:
        f.write(qg_summary)

    # Guardar scores para telemetría
    write_run_artifact(tel.run_dir, "scores.json", evaluaciones)

    # 5b. Validación en tiempo real
    informe_path = output_dir / "informe_validacion.md"

    if skip_validacion:
        print("\n⏭️ Validación post-consulta omitida (--skip-validacion)")
        informe = (
            "# Informe de Validación\n\n"
            "Validación post-consulta omitida por instrucción del usuario.\n"
        )
        with open(informe_path, "w", encoding="utf-8") as f:
            f.write(informe)
    else:
        from validar_respuestas import extraer_afirmaciones, verificar_afirmacion, investigar_tema_faltante, compilar_informe

        combinado_path = output_dir / "respuestas_combinadas.md"
        with open(combinado_path, "r", encoding="utf-8") as f:
            respuestas_text = f.read()

        datos = await extraer_afirmaciones(respuestas_text, profundidad)
        afirmaciones = datos.get("afirmaciones", [])
        temas_faltantes = datos.get("temas_no_mencionados", [])

        if afirmaciones or temas_faltantes:
            print(f"\n🌐 Verificando {len(afirmaciones)} afirmaciones y {len(temas_faltantes)} temas nuevos...")
            tareas_v = [verificar_afirmacion(af) for af in afirmaciones]
            tareas_t = [investigar_tema_faltante(t) for t in temas_faltantes]
            todos = await asyncio.gather(*(tareas_v + tareas_t))
            verificaciones = todos[:len(afirmaciones)]
            temas_nuevos = todos[len(afirmaciones):]

            informe = compilar_informe(verificaciones, temas_nuevos)
        else:
            informe = (
                "# Informe de Validación\n\n"
                "No se identificaron afirmaciones verificables.\n"
            )

        with open(informe_path, "w", encoding="utf-8") as f:
            f.write(informe)
        print(f"✅ Informe de validación: {len(informe):,} chars")

    tel.end_step("validacion_post", success=True, output_chars=len(informe))
    return str(informe_path)


# ═══════════════════════════════════════════════════════════════════
# PASO 6: SÍNTESIS FINAL
# ═══════════════════════════════════════════════════════════════════

async def paso_6_sintesis(
    output_dir: Path, prompt_path: str, informe_path: str, tel: RunTelemetry
) -> str:
    """GPT-5.4 sintetiza con informe de validación inyectado."""
    tel.start_step("sintesis")
    print("\n" + "=" * 60)
    print("📝 PASO 6: SÍNTESIS FINAL (GPT-5.4 como Orquestador)")
    print("=" * 60)

    from sintetizar_gpt54 import sintetizar

    combinado_path = str(output_dir / "respuestas_combinadas.md")
    sintesis_path = str(output_dir / "sintesis_final.md")

    meta = await sintetizar(
        input_path=combinado_path,
        output_path=sintesis_path,
        pregunta_original=prompt_path,
        informe_validacion=informe_path,
    )

    tel.end_step("sintesis", success=meta["exito"],
                 input_chars=meta.get("chars_entrada", 0),
                 output_chars=meta.get("chars_salida", 0),
                 extra={"modelo_usado": meta.get("modelo_usado"),
                        "fallback_usado": meta.get("fallback_usado", False),
                        "informe_inyectado": meta.get("informe_validacion_inyectado", False)})

    return sintesis_path


# ═══════════════════════════════════════════════════════════════════
# MAIN — ORQUESTADOR END-TO-END
# ═══════════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(
        description="Consulta a los Sabios — Entrypoint Oficial End-to-End",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
    python3.11 run_consulta_sabios.py \\
        --prompt /tmp/mi_pregunta.md \\
        --output-dir /tmp/consulta_001/
        """,
    )
    parser.add_argument("--prompt", required=True, help="Ruta al archivo con el prompt")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")
    parser.add_argument("--modo", choices=["enjambre", "consejo", "iterativo"], default="enjambre")
    parser.add_argument("--profundidad-pre", choices=["rapida", "normal", "profunda"], default="normal")
    parser.add_argument("--profundidad-post", choices=["rapida", "normal", "profunda"], default="normal")
    parser.add_argument("--sabios", default=None, help="Lista de sabios separada por comas")
    parser.add_argument("--system", default="Eres un experto analista y estratega de primer nivel mundial.",
                        help="System prompt para los sabios")
    parser.add_argument("--skip-investigacion", action="store_true", help="Omitir investigación pre-consulta")
    parser.add_argument("--skip-validacion", action="store_true", help="Omitir validación post-consulta")
    parser.add_argument("--skip-paso7", action="store_true", help="Omitir validación post-síntesis (Paso 7)")
    parser.add_argument("--profundidad-paso7", choices=["rapida", "normal", "profunda"], default="normal",
                        help="Profundidad de validación post-síntesis")
    parser.add_argument("--no-corregir", action="store_true", help="No generar síntesis corregida aunque haya errores")

    args = parser.parse_args()

    # Parsear lista de sabios
    sabios_list = args.sabios.split(",") if args.sabios else list(SABIOS.keys())

    # Inicializar run
    run_id = generate_run_id()
    run_dir = create_run_dir(run_id)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tel = RunTelemetry(
        run_id=run_id,
        run_dir=run_dir,
        modo=args.modo,
        profundidad_pre=args.profundidad_pre,
        profundidad_post=args.profundidad_post,
    )

    # Registrar fingerprint del prompt
    with open(args.prompt, "r", encoding="utf-8") as f:
        prompt_text = f.read()
    tel.set_prompt_fingerprint(prompt_text)

    # Copiar input al run
    copy_input_artifact(run_dir, args.prompt, "prompt_original.md")

    print("\n" + "█" * 60)
    print(f"  CONSULTA A LOS SABIOS — Run: {run_id}")
    print(f"  Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print(f"  Modo: {args.modo}")
    print(f"  Sabios: {', '.join(sabios_list)}")
    print("█" * 60)

    status = "success"

    try:
        # PASO 1: Pre-vuelo
        ok = await paso_1_prevuelo(tel)
        if not ok:
            status = "aborted_prevuelo"
            tel.finalize(status=status)
            sys.exit(1)

        # PASO 2: Investigación pre-consulta
        if args.skip_investigacion:
            print("\n⏭️ Investigación pre-consulta omitida (--skip-investigacion)")
            tel.start_step("investigacion_pre")
            tel.end_step("investigacion_pre", success=True, extra={"skipped": True})
            dossier_path = None
        else:
            dossier_path = await paso_2_investigacion(
                args.prompt, output_dir, args.profundidad_pre, tel
            )

        # PASO 3: Preparar contexto
        completo_path, condensado_path = await paso_3_preparar_contexto(
            args.prompt, dossier_path, output_dir, tel
        )

        # PASO 4: Consultar sabios
        resultados = await paso_4_consultar(
            completo_path, condensado_path, output_dir,
            sabios_list, args.system, tel
        )

        exitosos = sum(1 for r in resultados if r.get("exito"))
        if exitosos < 3:
            print(f"\n🛑 Solo {exitosos} sabios respondieron. Mínimo 3 requerido.")
            status = "insufficient_responses"
            tel.finalize(status=status)
            sys.exit(1)

        # PASO 5: Quality Gate + Validación
        informe_path = await paso_5_validacion(
            resultados, args.prompt, output_dir,
            args.profundidad_post, args.skip_validacion, tel
        )

        # PASO 6: Síntesis final
        sintesis_path = await paso_6_sintesis(
            output_dir, args.prompt, informe_path, tel
        )

        # PASO 7: Validación Post-Síntesis
        if args.skip_paso7:
            print("\n⏭️ Validación post-síntesis omitida (--skip-paso7)")
            tel.start_step("validacion_post_sintesis")
            tel.end_step("validacion_post_sintesis", success=True, extra={"skipped": True})
        else:
            tel.start_step("validacion_post_sintesis")
            print("\n" + "=" * 60)
            print("🔬 PASO 7: VALIDACIÓN POST-SÍNTESIS")
            print("=" * 60)

            from validar_sintesis import ejecutar_paso_7

            validacion_sintesis_path = str(output_dir / "validacion_sintesis.md")
            paso7_result = await ejecutar_paso_7(
                sintesis_path=str(output_dir / "sintesis_final.md"),
                informe_validacion_path=informe_path,
                output_path=validacion_sintesis_path,
                corregir=not args.no_corregir,
                profundidad=getattr(args, 'profundidad_paso7', 'normal'),
            )

            tel.end_step("validacion_post_sintesis", success=True,
                         extra={
                             "score_global": paso7_result["score_global"],
                             "score_factual": paso7_result["score_factual"],
                             "score_incorporacion": paso7_result["score_incorporacion"],
                             "necesita_correccion": paso7_result["necesita_correccion"],
                             "correccion_aplicada": paso7_result["correccion_aplicada"],
                             "afirmaciones_verificadas": paso7_result["afirmaciones_verificadas"],
                             "afirmaciones_con_problemas": paso7_result["afirmaciones_con_problemas"],
                         })

            if paso7_result["correccion_aplicada"]:
                print(f"\n✅ Síntesis corregida generada: {paso7_result['sintesis_corregida_path']}")

        # Copiar artefactos principales al run dir
        for f_name in ["sintesis_final.md", "respuestas_combinadas.md",
                       "informe_validacion.md", "quality_gate.md",
                       "validacion_sintesis.md", "sintesis_corregida.md",
                       "paso7_metadata.json"]:
            src = output_dir / f_name
            if src.exists():
                shutil.copy2(src, run_dir / "output" / f_name)

    except Exception as e:
        status = f"error: {str(e)[:200]}"
        print(f"\n🛑 ERROR: {e}")

    # Finalizar telemetría
    run_record = tel.finalize(status=status)

    print("\n" + "█" * 60)
    print(f"  CONSULTA COMPLETADA")
    print(f"  Run: {run_id}")
    print(f"  Status: {status}")
    print(f"  Duración: {run_record['duration_ms_total'] / 1000:.1f}s")
    print(f"  Sabios exitosos: {run_record.get('sabios_successful', '?')}/{run_record.get('sabios_requested', '?')}")
    print(f"  Telemetría: {run_dir}/telemetry.json")
    print(f"  Salida: {output_dir}/")
    print("█" * 60)


if __name__ == "__main__":
    asyncio.run(main())
