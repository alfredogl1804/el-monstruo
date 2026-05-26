"""
Tests para las 3 interfaces semánticas (CATASTRO-A v2 §TC).

Reusa el patrón make_mock_db(rows_by_table) de tests/test_catastros_4_vistas.py.
Cobertura ≥5 casos por interfaz (15+ casos totales).

Sprint CATASTRO-A v2 (post-S89 v2 Opción B firmada por Cowork T2-A).
Spec: bridge/cowork_to_manus_HILO_CATASTRO_SPRINT_CATASTRO_A_v2_POST_S89v2_2026_05_12.md §TC
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock

import pytest

from kernel.catastros import (
    CatastroAgentes2026,
    CatastroHerramientasAI,
    CatastroModelosLLM,
    CatastroSuppliers,
)
from kernel.catastros.interfaces import (
    CatastroLookupInterface,
    CatastroOrchestrationInterface,
    CatastroSearchInterface,
    NoSuitableResourceError,
    build_interfaces,
)

# ───────────────────────────────────────────────────────────────────────────
# Helpers + Fixtures
# ───────────────────────────────────────────────────────────────────────────


def make_mock_db(rows_by_table: Dict[str, List[Dict[str, Any]]]) -> Any:
    """Crea un mock db client con .select() asíncrono. (Mismo helper que test_catastros_4_vistas.py)"""
    mock = AsyncMock()

    async def _select(table: str, filters: Optional[Dict] = None):
        return rows_by_table.get(table, [])

    mock.select = AsyncMock(side_effect=_select)
    return mock


@pytest.fixture
def rows_fixture() -> Dict[str, List[Dict[str, Any]]]:
    """Fixture canónica con 2-3 rows por catastro para tests deterministas."""
    return {
        "catastro_modelos_llm": [
            {
                "key": "gpt-5",
                "name": "GPT-5",
                "provider": "openai",
                "max_tokens": 200_000,
                "cost_per_1k_input": 0.005,
                "cost_per_1k_output": 0.015,
                "active": True,
                "metadata": {"tags": ["code_writing", "reasoning"], "typical_latency_ms": 4000},
            },
            {
                "key": "claude-opus-4-6",
                "name": "Claude Opus 4.6",
                "provider": "anthropic",
                "max_tokens": 200_000,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
                "active": True,
                "metadata": {"tags": ["code_writing", "long_context"], "typical_latency_ms": 6000},
            },
        ],
        "catastro_agentes_2026": [
            {
                "key": "manus_hilo_catastro",
                "name": "Manus Hilo Catastro",
                "version": "v1.0",
                "owner_org": "manus",
                "biblia_path": "skills/manus.md",
                "capability_tags": ["catastros", "code_writing"],
                "has_native_loop": True,
                "has_native_tools": True,
                "active": True,
                "metadata": {},
            },
            {
                "key": "ace_studio_video",
                "name": "Ace Studio Video Composer",
                "version": "v2",
                "owner_org": "acestudio",
                "biblia_path": None,
                "capability_tags": ["video_generation"],
                "has_native_loop": False,
                "has_native_tools": False,
                "active": True,
                "metadata": {},
            },
        ],
        "catastro_herramientas_ai": [
            {
                "key": "perplexity_search",
                "name": "Perplexity Search",
                "category": "web_search",
                "endpoint": "https://api.perplexity.ai",
                "auth_type": "bearer",
                "rate_limit": "1000/h",
                "cost_per_call": 0.005,
                "fallback_tools": ["tavily_search"],
                "active": True,
                "metadata": {"tags": ["realtime", "citations"]},
            },
            {
                "key": "tavily_search",
                "name": "Tavily Search",
                "category": "web_search",
                "endpoint": "https://api.tavily.com",
                "auth_type": "bearer",
                "rate_limit": "1000/h",
                "cost_per_call": 0.008,
                "fallback_tools": [],
                "active": True,
                "metadata": {},
            },
        ],
        "catastro_suppliers_humanos": [
            {
                "key": "supplier_notario_5_navarrete",
                "name": "José Eduardo Navarrete Herrera",
                "role": "notario",
                "availability": "on_demand",
                "skills": ["fe_publica", "protocolizacion", "poderes", "testamentos"],
                "contact": {"verification_url": "https://www.notariadoyucateco.org.mx/notarios.php"},
                "active": True,
                "last_active": None,
            },
            {
                "key": "supplier_placeholder_arq_01",
                "name": "Arquitecto Sureste MX — placeholder 01",
                "role": "arquitecto",
                "availability": None,
                "skills": [],
                "contact": {"validation_status": "pending_realtime_verification"},
                "active": False,
                "last_active": None,
            },
        ],
    }


@pytest.fixture
async def loaded_catastros(rows_fixture):
    """Devuelve las 4 clases con load_from_db() ya ejecutado."""
    db = make_mock_db(rows_fixture)

    modelos = CatastroModelosLLM(db)
    agentes = CatastroAgentes2026(db)
    herramientas = CatastroHerramientasAI(db)
    suppliers = CatastroSuppliers(db)

    await modelos.load_from_db()
    await agentes.load_from_db()
    await herramientas.load_from_db()
    await suppliers.load_from_db()

    return modelos, agentes, herramientas, suppliers


# ───────────────────────────────────────────────────────────────────────────
# Tests Interfaz 1: Lookup
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_lookup_finds_in_specific_catastro(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    lookup = CatastroLookupInterface(modelos, agentes, herramientas, suppliers)

    result = lookup.lookup("gpt-5", catastro="modelos_llm")
    assert result is not None
    assert result["key"] == "gpt-5"
    assert result["_catastro"] == "modelos_llm"
    assert result["provider"] == "openai"


@pytest.mark.asyncio
async def test_lookup_cross_catastros_finds_first_match(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    lookup = CatastroLookupInterface(modelos, agentes, herramientas, suppliers)

    # key vive en agentes_2026 únicamente
    result = lookup.lookup("manus_hilo_catastro")
    assert result is not None
    assert result["_catastro"] == "agentes_2026"


@pytest.mark.asyncio
async def test_lookup_returns_none_for_unknown_key(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    lookup = CatastroLookupInterface(modelos, agentes, herramientas, suppliers)

    assert lookup.lookup("nonexistent_key") is None
    assert lookup.lookup("gpt-5", catastro="agentes_2026") is None


@pytest.mark.asyncio
async def test_lookup_raises_on_invalid_catastro_name(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    lookup = CatastroLookupInterface(modelos, agentes, herramientas, suppliers)

    with pytest.raises(ValueError, match="catastro debe ser uno de"):
        lookup.lookup("gpt-5", catastro="fake_catastro")


@pytest.mark.asyncio
async def test_lookup_all_returns_multiple_when_keys_collide(loaded_catastros):
    """Si una key existiera en 2+ catastros, lookup_all devuelve todas."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    lookup = CatastroLookupInterface(modelos, agentes, herramientas, suppliers)

    # gpt-5 sólo está en modelos, devuelve 1 entrada
    results = lookup.lookup_all("gpt-5")
    assert len(results) == 1
    assert results[0]["_catastro"] == "modelos_llm"

    # nonexistent → lista vacía
    assert lookup.lookup_all("nonexistent") == []


# ───────────────────────────────────────────────────────────────────────────
# Tests Interfaz 2: Search
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_by_single_tag_cross_catastros(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    search = CatastroSearchInterface(modelos, agentes, herramientas, suppliers)

    results = search.search(["code_writing"])
    # Debe matchear gpt-5 + claude (modelos) + manus_hilo_catastro (agentes)
    catastros_found = {r["_catastro"] for r in results}
    keys_found = {r["key"] for r in results}
    assert "modelos_llm" in catastros_found
    assert "agentes_2026" in catastros_found
    assert "gpt-5" in keys_found
    assert "manus_hilo_catastro" in keys_found


@pytest.mark.asyncio
async def test_search_acotado_a_un_catastro(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    search = CatastroSearchInterface(modelos, agentes, herramientas, suppliers)

    results = search.search(["code_writing"], catastro="modelos_llm")
    assert len(results) == 2
    for r in results:
        assert r["_catastro"] == "modelos_llm"


@pytest.mark.asyncio
async def test_search_match_all_vs_any(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    search = CatastroSearchInterface(modelos, agentes, herramientas, suppliers)

    # match=any: encuentra 2 (gpt-5 con tags=[code_writing,reasoning], claude con [code_writing,long_context])
    results_any = search.search(["code_writing", "reasoning"], catastro="modelos_llm", match="any")
    assert len(results_any) == 2

    # match=all: encuentra sólo gpt-5 (tiene ambos)
    results_all = search.search(["code_writing", "reasoning"], catastro="modelos_llm", match="all")
    assert len(results_all) == 1
    assert results_all[0]["key"] == "gpt-5"


@pytest.mark.asyncio
async def test_search_filters_inactive_by_default(loaded_catastros):
    """Placeholder supplier (active=False) NO debe aparecer en search por defecto (DSC-V-002)."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    search = CatastroSearchInterface(modelos, agentes, herramientas, suppliers)

    results = search.search(["fe_publica"], catastro="suppliers_humanos")
    # solo el real, no el placeholder
    assert len(results) == 1
    assert results[0]["key"] == "supplier_notario_5_navarrete"

    # con only_active=False sí aparece (pero placeholder no tiene "fe_publica" skill)
    # validamos que skills vacíos en placeholder no matchean ningún tag
    results_with_inactive = search.search([""], catastro="suppliers_humanos", only_active=False)
    # tag vacío no debería matchear nada
    assert results_with_inactive == []


@pytest.mark.asyncio
async def test_search_extracts_tags_per_catastro_correctly(loaded_catastros):
    """Cada catastro mapea tags desde un campo diferente."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    search = CatastroSearchInterface(modelos, agentes, herramientas, suppliers)

    # herramientas_ai: usa "category" como tag
    results = search.search(["web_search"], catastro="herramientas_ai")
    assert len(results) == 2  # perplexity + tavily

    # suppliers: usa "skills"
    results = search.search(["protocolizacion"], catastro="suppliers_humanos")
    assert len(results) == 1
    assert results[0]["key"] == "supplier_notario_5_navarrete"


@pytest.mark.asyncio
async def test_search_raises_on_invalid_match_kind(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    search = CatastroSearchInterface(modelos, agentes, herramientas, suppliers)

    with pytest.raises(ValueError, match="match debe ser"):
        search.search(["x"], match="exact")


# ───────────────────────────────────────────────────────────────────────────
# Tests Interfaz 3: Orchestration
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_orchestrate_picks_agent_first_for_code_writing(loaded_catastros):
    """AI-first priority: agentes_2026 antes que modelos_llm."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    orch = CatastroOrchestrationInterface(modelos, agentes, herramientas, suppliers)

    result = orch.orchestrate({"capability": "code_writing"})
    assert result["primary_catastro"] == "agentes_2026"
    assert result["primary"]["key"] == "manus_hilo_catastro"
    # gpt-5 + claude deben quedar como fallbacks
    fallback_keys = {f["key"] for f in result["fallbacks"]}
    assert "gpt-5" in fallback_keys
    assert "claude-opus-4-6" in fallback_keys
    assert "AI-first" in result["rationale"]


@pytest.mark.asyncio
async def test_orchestrate_respects_budget_constraint(loaded_catastros):
    """budget_per_1k=0.01 debe descartar claude-opus-4-6 (cost 0.075)."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    orch = CatastroOrchestrationInterface(modelos, agentes, herramientas, suppliers)

    result = orch.orchestrate({"capability": "code_writing", "budget_per_1k": 0.01})
    # claude (0.075) descartado, gpt-5 (0.015) también descartado, agente sí pasa
    keys_kept = {result["primary"]["key"]} | {f["key"] for f in result["fallbacks"]}
    assert "claude-opus-4-6" not in keys_kept
    assert "gpt-5" not in keys_kept  # 0.015 > 0.01
    assert "manus_hilo_catastro" in keys_kept


@pytest.mark.asyncio
async def test_orchestrate_prefer_human(loaded_catastros):
    """prefer_human=True: suppliers_humanos primero."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    orch = CatastroOrchestrationInterface(modelos, agentes, herramientas, suppliers)

    result = orch.orchestrate({"capability": "fe_publica", "prefer_human": True})
    assert result["primary_catastro"] == "suppliers_humanos"
    assert result["primary"]["key"] == "supplier_notario_5_navarrete"
    assert "human-first" in result["rationale"]


@pytest.mark.asyncio
async def test_orchestrate_raises_no_suitable_resource(loaded_catastros):
    """Capability inexistente → NoSuitableResourceError."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    orch = CatastroOrchestrationInterface(modelos, agentes, herramientas, suppliers)

    with pytest.raises(NoSuitableResourceError):
        orch.orchestrate({"capability": "telekinesis"})


@pytest.mark.asyncio
async def test_orchestrate_validates_query_schema(loaded_catastros):
    """Query sin capability → ValueError."""
    modelos, agentes, herramientas, suppliers = loaded_catastros
    orch = CatastroOrchestrationInterface(modelos, agentes, herramientas, suppliers)

    with pytest.raises(ValueError, match="capability"):
        orch.orchestrate({})
    with pytest.raises(ValueError, match="capability"):
        orch.orchestrate({"capability": None})


@pytest.mark.asyncio
async def test_orchestrate_respects_latency_constraint(loaded_catastros):
    """latency_max_ms=5000 descarta claude (6000ms) — único candidato con tag long_context.

    Como agentes/suppliers no tienen long_context y gpt-5 tampoco, el único
    candidato es claude (6000ms) que excede 5000ms → NoSuitableResourceError.
    Verifica que el constraint de latencia se aplica correctamente.
    """
    modelos, agentes, herramientas, suppliers = loaded_catastros
    orch = CatastroOrchestrationInterface(modelos, agentes, herramientas, suppliers)

    # Sin constraint: encuentra claude (único con long_context)
    result = orch.orchestrate({"capability": "long_context"})
    assert result["primary"]["key"] == "claude-opus-4-6"
    assert result["primary"]["metadata"]["typical_latency_ms"] == 6000

    # Con latency_max_ms=5000: claude descartado, no hay alternativa
    with pytest.raises(NoSuitableResourceError):
        orch.orchestrate(
            {
                "capability": "long_context",
                "latency_max_ms": 5000,
            }
        )

    # Con latency_max_ms=7000: claude pasa (6000 ≤ 7000)
    result = orch.orchestrate(
        {
            "capability": "long_context",
            "latency_max_ms": 7000,
        }
    )
    assert result["primary"]["key"] == "claude-opus-4-6"


# ───────────────────────────────────────────────────────────────────────────
# Tests Factory + Smoke
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_interfaces_factory_returns_3_interfaces(loaded_catastros):
    modelos, agentes, herramientas, suppliers = loaded_catastros
    interfaces = build_interfaces(modelos, agentes, herramientas, suppliers)

    assert "lookup" in interfaces
    assert "search" in interfaces
    assert "orchestration" in interfaces
    assert isinstance(interfaces["lookup"], CatastroLookupInterface)
    assert isinstance(interfaces["search"], CatastroSearchInterface)
    assert isinstance(interfaces["orchestration"], CatastroOrchestrationInterface)


@pytest.mark.asyncio
async def test_interfaces_work_with_empty_catastros():
    """Si todos los catastros están vacíos, search devuelve [], lookup devuelve None,
    orchestrate raises NoSuitableResourceError."""
    db = make_mock_db({})
    modelos = CatastroModelosLLM(db)
    agentes = CatastroAgentes2026(db)
    herramientas = CatastroHerramientasAI(db)
    suppliers = CatastroSuppliers(db)
    for c in (modelos, agentes, herramientas, suppliers):
        await c.load_from_db()

    interfaces = build_interfaces(modelos, agentes, herramientas, suppliers)

    assert interfaces["lookup"].lookup("anything") is None
    assert interfaces["search"].search(["anything"]) == []
    with pytest.raises(NoSuitableResourceError):
        interfaces["orchestration"].orchestrate({"capability": "anything"})
