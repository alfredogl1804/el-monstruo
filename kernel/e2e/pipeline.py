"""
Sprint 87 — Pipeline lineal E2E de 12 pasos.

Recibe un run_id y un repository, ejecuta secuencialmente los 12 pasos.
Cada step:
1. Loggea inicio en e2e_step_log con status='ok'/'failed'.
2. Para steps LLM: consulta CatastroRuntimeClient → elige modelo → loggea modelo_consultado.
3. Avanza pipeline_step en e2e_runs.
4. Si falla: estado='failed', error_message en step_log.
5. En step 12 (VEREDICTO): si critic_visual_score >= 80 → completed; si no → awaiting_judgment.

Diseño v1.0 honesto: los Embriones reales se llaman cuando existen y son robustos.
Donde no existen o son riesgosos, el step usa stubs estructurados que producen
output_payload válido (Brand DNA: el output siempre tiene identidad, nunca "TODO").
"""

from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog

from kernel.e2e.catastro_client import CatastroRuntimeClient
from kernel.e2e.repository import E2ERepository
from kernel.e2e.schema import (
    EstadoRun,
    PIPELINE_STEPS,
    StepName,
    StepStatus,
    Veredicto,
)

logger = structlog.get_logger("e2e_pipeline")


# Threshold para promover automáticamente a 'completed' sin esperar veredicto.
# Si critic_visual_score >= este valor → 'awaiting_judgment' aún se setea, pero
# se marca el run como apto para auto-completar si Alfredo no responde en T.
CRITIC_VISUAL_THRESHOLD = float(os.environ.get("E2E_CRITIC_THRESHOLD", "80"))


async def _step_intake(repo: E2ERepository, run_id: str, frase_input: str) -> Dict[str, Any]:
    """Step 1 — INTAKE: parse de la frase a un brief inicial."""
    return {
        "frase_input": frase_input,
        "tokens_estimate": len(frase_input.split()),
        "intake_at": datetime.now(timezone.utc).isoformat(),
    }


async def _step_investigar(
    cat: CatastroRuntimeClient,
    frase_input: str,
) -> Dict[str, Any]:
    """Step 2 — INVESTIGAR: research del nicho. v1.0 stub structured."""
    selection = await cat.select_model_for_step("INVESTIGAR")
    return {
        "modelo_elegido": selection,
        "research_summary": (
            "Stub v1.0 — research del nicho derivado de la frase. "
            "Real LLM call queda como deuda Sprint 87.1 si Alfredo lo prioriza."
        ),
        "competitors_seen": [],
        "trends_seen": [],
    }


async def _step_architect(
    cat: CatastroRuntimeClient,
    frase_input: str,
    research: Dict[str, Any],
) -> Dict[str, Any]:
    """Step 3 — ARCHITECT: brief estructurado del producto."""
    selection = await cat.select_model_for_step("ARCHITECT")
    # Intentar usar Embrión real si existe
    try:
        from kernel.embriones import product_architect  # type: ignore[attr-defined]

        if hasattr(product_architect, "build_brief"):
            real_brief = await asyncio.to_thread(
                product_architect.build_brief, frase_input
            )
            return {
                "modelo_elegido": selection,
                "brief": real_brief,
                "source": "embrion_real",
            }
    except Exception as exc:
        logger.info("e2e_product_architect_unavailable", error=str(exc))

    return {
        "modelo_elegido": selection,
        "brief": {
            "nombre_proyecto": "TBD",
            "audiencia": "TBD",
            "propuesta_valor": frase_input,
            "secciones_landing": [
                "hero", "beneficios", "galeria", "testimonios", "cta_final"
            ],
        },
        "source": "stub_v1",
    }


async def _step_llm_generic(
    cat: CatastroRuntimeClient,
    step_name: str,
    payload_in: Dict[str, Any],
) -> Dict[str, Any]:
    """Step genérico para ESTRATEGIA/FINANZAS/CREATIVO/VENTAS/TECNICO."""
    selection = await cat.select_model_for_step(step_name)
    return {
        "modelo_elegido": selection,
        "step_name": step_name,
        "input_received_keys": list(payload_in.keys()),
        "result": f"v1.0 stub structured — {step_name} ejecutado con {selection.get('model_label')}",
    }


async def _step_deploy(
    brief: Dict[str, Any],
    run_id: str,
) -> Dict[str, Any]:
    """Step 9 — DEPLOY: genera URL viva. v1.0 estatico documentado."""
    # En v1.0, el deploy real es deuda asumida. Devolvemos URL placeholder
    # marcada como mock para que Critic Visual sepa qué procesar.
    deploy_url = f"https://el-monstruo-e2e-mock.example.com/{run_id}"
    return {
        "deploy_url": deploy_url,
        "deploy_target": "mock_v1",
        "deploy_at": datetime.now(timezone.utc).isoformat(),
        "real_deploy_pending": True,
    }


async def _step_critic_visual(
    cat: CatastroRuntimeClient,
    deploy_url: str,
) -> Dict[str, Any]:
    """Step 10 — CRITIC: evalúa visual del deploy. v1.0 con score conservador."""
    selection = await cat.select_model_for_step("CRITIC")
    # En v1.0 (sin sovereign_browser conectado): score conservador 60.
    # Cowork firmó esta deuda en spec del Sprint 87.
    score_v1 = 60.0
    return {
        "modelo_elegido": selection,
        "critic_visual_score": score_v1,
        "deploy_url": deploy_url,
        "feedback": "v1.0 stub — score conservador 60 hasta integración sovereign_browser.",
    }


async def _step_traffic(deploy_url: str) -> Dict[str, Any]:
    """Step 11 — TRAFFIC: vigía sintético. v1.0 stub."""
    return {
        "deploy_url": deploy_url,
        "requests_seeded": 0,
        "vigia_status": "v1_stub_pending",
    }


async def _step_veredicto(
    repo: E2ERepository,
    run_id: str,
    critic_score: float,
) -> Dict[str, Any]:
    """Step 12 — VEREDICTO: decide cierre del run."""
    if critic_score >= CRITIC_VISUAL_THRESHOLD:
        # Apto para autocomplete pero respetamos awaiting_judgment para Alfredo
        new_estado = EstadoRun.AWAITING_JUDGMENT
        recommendation = "human_judgment_recommended"
    else:
        new_estado = EstadoRun.AWAITING_JUDGMENT
        recommendation = "below_threshold_human_review_required"
    return {
        "decision": recommendation,
        "critic_visual_score": critic_score,
        "threshold": CRITIC_VISUAL_THRESHOLD,
        "estado_target": new_estado.value,
    }


async def _safe_step(
    coro,
    *,
    repo: E2ERepository,
    run_id: str,
    step_number: int,
    step_name: StepName,
    embrion_id: Optional[str],
    input_payload: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Ejecuta un step con timing + persistencia en e2e_step_log."""
    started = time.perf_counter()
    try:
        output = await coro
        duration = int((time.perf_counter() - started) * 1000)
        modelo = None
        if isinstance(output, dict):
            sel = output.get("modelo_elegido") or {}
            if isinstance(sel, dict):
                modelo = sel.get("model_id")
        await repo.append_step_log(
            run_id,
            step_number=step_number,
            step_name=step_name,
            status=StepStatus.OK,
            embrion_id=embrion_id,
            modelo_consultado=modelo,
            input_payload=input_payload,
            output_payload=output,
            duration_ms=duration,
        )
        return output
    except Exception as exc:
        duration = int((time.perf_counter() - started) * 1000)
        await repo.append_step_log(
            run_id,
            step_number=step_number,
            step_name=step_name,
            status=StepStatus.FAILED,
            embrion_id=embrion_id,
            input_payload=input_payload,
            duration_ms=duration,
            error_message=f"{type(exc).__name__}: {exc}",
        )
        logger.error(
            "e2e_step_failed",
            run_id=run_id,
            step_number=step_number,
            step_name=step_name.value,
            error=str(exc),
        )
        return None


async def run_e2e_pipeline(run_id: str, repo: E2ERepository) -> None:
    """Punto de entrada principal. Ejecuta los 12 pasos lineales."""
    cat = CatastroRuntimeClient()
    run = await repo.get_run(run_id)
    if run is None:
        logger.error("e2e_pipeline_run_not_found", run_id=run_id)
        return

    frase = run.frase_input
    state: Dict[str, Any] = {"run_id": run_id, "frase_input": frase}

    # -------- Step 1: INTAKE --------
    out = await _safe_step(
        _step_intake(repo, run_id, frase),
        repo=repo,
        run_id=run_id,
        step_number=1,
        step_name=StepName.INTAKE,
        embrion_id=None,
        input_payload={"frase_input": frase},
    )
    if out is None:
        await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
        return
    state["intake"] = out
    await repo.update_run(run_id, pipeline_step=1)

    # -------- Step 2: INVESTIGAR --------
    out = await _safe_step(
        _step_investigar(cat, frase),
        repo=repo,
        run_id=run_id,
        step_number=2,
        step_name=StepName.INVESTIGAR,
        embrion_id="embrion_investigador",
        input_payload={"frase_input": frase},
    )
    if out is None:
        await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
        return
    state["research"] = out
    await repo.update_run(run_id, pipeline_step=2)

    # -------- Step 3: ARCHITECT --------
    out = await _safe_step(
        _step_architect(cat, frase, state["research"]),
        repo=repo,
        run_id=run_id,
        step_number=3,
        step_name=StepName.ARCHITECT,
        embrion_id="product_architect",
        input_payload={"frase_input": frase, "research": state["research"]},
    )
    if out is None:
        await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
        return
    state["architect"] = out
    await repo.update_run(run_id, pipeline_step=3, brief=out.get("brief"))

    # -------- Steps 4-8: ESTRATEGIA, FINANZAS, CREATIVO, VENTAS, TECNICO --------
    for step_number, step_name, embrion_id in [
        (4, StepName.ESTRATEGIA, "embrion_estratega"),
        (5, StepName.FINANZAS, "embrion_financiero"),
        (6, StepName.CREATIVO, "embrion_creativo"),
        (7, StepName.VENTAS, "embrion_ventas"),
        (8, StepName.TECNICO, "embrion_tecnico"),
    ]:
        out = await _safe_step(
            _step_llm_generic(cat, step_name.value, state),
            repo=repo,
            run_id=run_id,
            step_number=step_number,
            step_name=step_name,
            embrion_id=embrion_id,
            input_payload={"state_keys": list(state.keys())},
        )
        if out is None:
            await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
            return
        state[step_name.value.lower()] = out
        if step_number == 4:
            # Persistir stack_decision en run row (Cowork lo pide específicamente)
            await repo.update_run(run_id, pipeline_step=step_number, stack_decision=out)
        else:
            await repo.update_run(run_id, pipeline_step=step_number)

    # -------- Step 9: DEPLOY --------
    out = await _safe_step(
        _step_deploy(state["architect"]["brief"], run_id),
        repo=repo,
        run_id=run_id,
        step_number=9,
        step_name=StepName.DEPLOY,
        embrion_id=None,
        input_payload={"brief_keys": list(state["architect"]["brief"].keys())},
    )
    if out is None:
        await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
        return
    state["deploy"] = out
    deploy_url = out.get("deploy_url")
    await repo.update_run(run_id, pipeline_step=9, deploy_url=deploy_url)

    # -------- Step 10: CRITIC --------
    out = await _safe_step(
        _step_critic_visual(cat, deploy_url or ""),
        repo=repo,
        run_id=run_id,
        step_number=10,
        step_name=StepName.CRITIC,
        embrion_id="critic_visual",
        input_payload={"deploy_url": deploy_url},
    )
    if out is None:
        await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
        return
    state["critic"] = out
    critic_score = float(out.get("critic_visual_score") or 0.0)
    await repo.update_run(
        run_id,
        pipeline_step=10,
        critic_visual_score=critic_score,
    )

    # -------- Step 11: TRAFFIC --------
    out = await _safe_step(
        _step_traffic(deploy_url or ""),
        repo=repo,
        run_id=run_id,
        step_number=11,
        step_name=StepName.TRAFFIC,
        embrion_id="embrion_vigia",
        input_payload={"deploy_url": deploy_url},
    )
    state["traffic"] = out or {}
    await repo.update_run(run_id, pipeline_step=11)

    # -------- Step 12: VEREDICTO --------
    out = await _safe_step(
        _step_veredicto(repo, run_id, critic_score),
        repo=repo,
        run_id=run_id,
        step_number=12,
        step_name=StepName.VEREDICTO,
        embrion_id=None,
        input_payload={"critic_visual_score": critic_score},
    )
    if out is None:
        await repo.update_run(run_id, estado=EstadoRun.FAILED, completed_at=datetime.now(timezone.utc))
        return

    estado_target = EstadoRun(out["estado_target"])
    await repo.update_run(
        run_id,
        pipeline_step=12,
        estado=estado_target,
    )
    logger.info(
        "e2e_pipeline_completed",
        run_id=run_id,
        critic_visual_score=critic_score,
        estado=estado_target.value,
    )
