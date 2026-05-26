"""
Primer test E2E real anti-Dory contra api.manus.ai — bypasea mocks que escondieron el F-pattern §4 del bridge D5_RESULT.

Sprint:        MANUS-ANTI-DORY-002-v1
Fase:          D5-FIX-PAYLOAD (post-D5 RED root cause analysis)
Owner:         Manus Hilo Ejecutor 1
Autoridad:     T1 Alfredo (Opción A autorizada 2026-05-14)
Audit + merge: Cowork T2-A (regla evolucionada CLAUDE.md)

Por qué este test debe existir:
- D5 RAP-001 LIVE detectó que `tools/manus_bridge.py:274` enviaba `{"prompt": prompt}` mientras
  el contrato real `api.manus.ai/v2/task.create` (skill manus-api/docs/v2/openapi_v2.json) exige
  `{"message": {"content": prompt}}`.
- El bug no se detectó antes porque toda la suite previa mockea el HTTP request (ver
  `test_manus_bridge_integration.py` y `test_rap_002_harness.py`).
- Sin un test E2E real, cualquier futuro drift del contrato volverá a colarse.

Política de ejecución:
- Marker `@pytest.mark.live` (no registrado intencionalmente en pyproject.toml para respetar la
  regla NO-CRUCE del sprint D5-FIX-PAYLOAD; canonización del marker queda para sprint posterior).
- `pytest.skip` automático si `MANUS_API_KEY_GOOGLE` no está en env → CI sin credenciales no se rompe.
- Comando para invocar en sandbox con credenciales: `pytest tests/anti_dory/test_manus_bridge_e2e_live.py -v -m live`
- Comando para ejecutar baseline sin live: `pytest tests/anti_dory/ -v -m "not live"`

Acceptance criterion implícito:
- `status_code != 400 invalid_argument: message.content is required`
- response contiene `task_id` (o `id`) string no vacío
- `ok: true` en la envoltura del response

NOTA: este test NO verifica `attach_context=True` ni hidratación del snapshot canónico — eso lo
valida el re-test D5 RAP-001 LIVE post-merge según §SECUENCIA del kickoff D5-FIX.
"""

from __future__ import annotations

import os

import pytest

# Marker: live → tests que tocan APIs externas reales (no mock)
pytestmark = pytest.mark.live


@pytest.fixture
def manus_api_key() -> str:
    """Skip si la credencial no está disponible — CI sin secrets no debe romper."""
    key = os.environ.get("MANUS_API_KEY_GOOGLE")
    if not key:
        pytest.skip(
            "MANUS_API_KEY_GOOGLE no presente en env — test live skip en CI sin credenciales. "
            "Para ejecutar: `source /tmp/anti_dory_d5_env.sh && pytest -m live tests/anti_dory/test_manus_bridge_e2e_live.py -v`"
        )
    return key


def test_create_task_payload_v2_contract_real(manus_api_key: str) -> None:
    """
    Verifica que `create_task` envía el payload con el schema v2 actual
    (`{"message": {"content": ...}}`) y que `api.manus.ai` responde con `ok: true`
    + `task_id` no vacío en lugar del `HTTP 400 invalid_argument: message.content is required`
    que produjo el F-pattern descubierto en D5 RAP-001 LIVE.

    Este test NO usa `attach_context=True` — eso lo valida el re-test D5 post-merge.
    """
    # Importación tardía para que el skip se evalúe antes (tools/manus_bridge importa httpx etc.)
    from tools.manus_bridge import create_task

    response = create_task(
        prompt="ping D5 fix verification",
        account="google",
        attach_context=False,
    )

    # Asserción binaria: si el payload sigue mal, response sería un dict de error o create_task
    # tiraría ManusBridgeError. Si llegamos aquí, status_code != 400.
    assert isinstance(response, dict), f"Expected dict, got {type(response)!r}: {response!r}"

    # El response del wrapper unwrappea `data` automáticamente; verificamos task_id presente.
    task_id = response.get("task_id") or response.get("id")
    assert task_id, (
        f"Esperaba task_id/id no vacío en response — recibí: {response!r}. "
        "Si este assert falla con 400, el payload del fix se rompió."
    )
    assert isinstance(task_id, str) and len(task_id) > 0, f"task_id debe ser string no vacío, recibí: {task_id!r}"
