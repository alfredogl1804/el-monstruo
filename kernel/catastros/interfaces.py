"""
Interfaces semánticas sobre los 4 catastros canónicos DSC-G-007.1.

Sprint CATASTRO-A v2 (post-S89 v2 Opción B firmada por Cowork T2-A).
Spec: bridge/cowork_to_manus_HILO_CATASTRO_SPRINT_CATASTRO_A_v2_POST_S89v2_2026_05_12.md §TC

Estas 3 interfaces NO duplican la lógica de las 4 abstracciones de Ejecutor 1
(CatastroModelosLLM, CatastroAgentes2026, CatastroHerramientasAI, CatastroSuppliers).
Las consumen vía composición (no herencia) y agregan 3 operaciones cross-catastros:

  - Lookup: encontrar un recurso por key (opcionalmente acotado a un catastro)
  - Search: encontrar recursos por tags/capabilities (cross-catastros o acotado)
  - Orchestration: elegir el mejor recurso para una capability + constraints

Diseño:
  - Composición sobre herencia: las interfaces toman las 4 instancias como dependencias.
  - Sync (no async) en los métodos públicos: las 4 clases base cachean en memoria
    via `load_from_db()`, por lo que `get()` y `list()` son operaciones O(1)/O(N) sync.
  - El caller es responsable de hacer `await catastro.load_from_db()` antes de
    instanciar/usar las interfaces.
  - El campo `_catastro` se inyecta en cada dict devuelto para trazabilidad cross-catastros.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Optional

from kernel.catastros.agentes_2026 import CatastroAgentes2026
from kernel.catastros.herramientas_ai import CatastroHerramientasAI
from kernel.catastros.modelos_llm import CatastroModelosLLM
from kernel.catastros.suppliers_humanos import CatastroSuppliers

logger = logging.getLogger(__name__)

# Tipo canónico para nombres de catastro (alineado con DSC-G-007.1)
CatastroName = Literal[
    "modelos_llm",
    "agentes_2026",
    "herramientas_ai",
    "suppliers_humanos",
]

_VALID_CATASTROS = ("modelos_llm", "agentes_2026", "herramientas_ai", "suppliers_humanos")


def _validate_catastro_name(name: Optional[str]) -> None:
    if name is not None and name not in _VALID_CATASTROS:
        raise ValueError(f"catastro debe ser uno de {list(_VALID_CATASTROS)} — got {name!r}")


def _extract_tags(row: Dict[str, Any], catastro_name: str) -> List[str]:
    """Extrae tags/capabilities según el catastro.

    - modelos_llm: usa metadata.tags si existe (jsonb).
    - agentes_2026: usa capability_tags (TEXT[]).
    - herramientas_ai: usa category como tag único + metadata.tags si existe.
    - suppliers_humanos: usa skills (TEXT[]).
    """
    tags: List[str] = []

    if catastro_name == "modelos_llm":
        metadata = row.get("metadata") or {}
        if isinstance(metadata, dict):
            mtags = metadata.get("tags") or []
            if isinstance(mtags, list):
                tags.extend(str(t) for t in mtags)

    elif catastro_name == "agentes_2026":
        ctags = row.get("capability_tags") or []
        if isinstance(ctags, list):
            tags.extend(str(t) for t in ctags)

    elif catastro_name == "herramientas_ai":
        category = row.get("category")
        if category:
            tags.append(str(category))
        metadata = row.get("metadata") or {}
        if isinstance(metadata, dict):
            mtags = metadata.get("tags") or []
            if isinstance(mtags, list):
                tags.extend(str(t) for t in mtags)

    elif catastro_name == "suppliers_humanos":
        skills = row.get("skills") or []
        if isinstance(skills, list):
            tags.extend(str(s) for s in skills)

    return tags


# =========================================================================
# Interfaz 1 — Lookup cross-catastros
# =========================================================================


class CatastroLookupInterface:
    """Interfaz 1: lookup by-key, opcionalmente acotado a un catastro.

    Casos de uso:
      - El embrión recibe `key="gpt-5"` y quiere saber qué tipo de recurso es.
      - Pre-flight validation: ¿existe esta key en algún catastro antes de delegar?
    """

    def __init__(
        self,
        modelos_llm: CatastroModelosLLM,
        agentes_2026: CatastroAgentes2026,
        herramientas_ai: CatastroHerramientasAI,
        suppliers_humanos: CatastroSuppliers,
    ) -> None:
        self._catastros: Dict[str, Any] = {
            "modelos_llm": modelos_llm,
            "agentes_2026": agentes_2026,
            "herramientas_ai": herramientas_ai,
            "suppliers_humanos": suppliers_humanos,
        }

    def lookup(self, key: str, catastro: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find by key.

        Args:
            key: identificador único del recurso.
            catastro: si especificado, sólo busca en ese catastro. Si None,
                      busca en los 4 y devuelve la primera coincidencia.

        Returns:
            dict con la row (incluye campo virtual `_catastro` con el origen)
            o None si no encontró match.

        Raises:
            ValueError si `catastro` no es uno de los 4 canónicos.
        """
        _validate_catastro_name(catastro)

        if catastro is not None:
            entry = self._catastros[catastro].get(key)
            if entry is None:
                return None
            return {**entry, "_catastro": catastro}

        # Cross-catastros: primer match gana.
        for name, catastro_inst in self._catastros.items():
            entry = catastro_inst.get(key)
            if entry is not None:
                return {**entry, "_catastro": name}
        return None

    def lookup_all(self, key: str) -> List[Dict[str, Any]]:
        """Find by key en TODOS los catastros (puede haber colisión de keys)."""
        results: List[Dict[str, Any]] = []
        for name, catastro_inst in self._catastros.items():
            entry = catastro_inst.get(key)
            if entry is not None:
                results.append({**entry, "_catastro": name})
        return results


# =========================================================================
# Interfaz 2 — Search by-tags cross-catastros
# =========================================================================


class CatastroSearchInterface:
    """Interfaz 2: search by-tags, opcionalmente acotado a un catastro.

    Casos de uso:
      - Embrión busca recursos con tag "code_writing" → modelos LLM + agentes.
      - Busca capabilities cross-catastros sin saber a priori en cuál vive.
    """

    def __init__(
        self,
        modelos_llm: CatastroModelosLLM,
        agentes_2026: CatastroAgentes2026,
        herramientas_ai: CatastroHerramientasAI,
        suppliers_humanos: CatastroSuppliers,
    ) -> None:
        self._catastros: Dict[str, Any] = {
            "modelos_llm": modelos_llm,
            "agentes_2026": agentes_2026,
            "herramientas_ai": herramientas_ai,
            "suppliers_humanos": suppliers_humanos,
        }

    def search(
        self,
        tags: List[str],
        catastro: Optional[str] = None,
        match: str = "any",
        only_active: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search by tags.

        Args:
            tags: lista de tags/capabilities a buscar (lowercase comparison).
            catastro: si especificado, sólo busca en ese catastro.
            match: "any" devuelve rows que matchean ≥1 tag; "all" requiere todos.
            only_active: filtra rows con active=False (default True por DSC-V-002).

        Returns:
            Lista de rows (cada una con campo `_catastro` agregado).

        Raises:
            ValueError si `catastro` no es válido o `match` no es "any"/"all".
        """
        _validate_catastro_name(catastro)
        if match not in ("any", "all"):
            raise ValueError(f"match debe ser 'any' o 'all' — got {match!r}")

        tags_lower = {t.lower() for t in tags}
        if not tags_lower:
            return []

        targets = [(catastro, self._catastros[catastro])] if catastro is not None else list(self._catastros.items())

        results: List[Dict[str, Any]] = []

        for name, catastro_inst in targets:
            for row in catastro_inst.list():
                if only_active and row.get("active") is False:
                    continue
                row_tags = {t.lower() for t in _extract_tags(row, name)}
                if match == "all":
                    if not tags_lower.issubset(row_tags):
                        continue
                else:  # any
                    if not (tags_lower & row_tags):
                        continue
                results.append({**row, "_catastro": name})

        return results


# =========================================================================
# Interfaz 3 — Orchestration cross-catastros
# =========================================================================


class NoSuitableResourceError(RuntimeError):
    """No resource matches the orchestration query under given constraints."""


class CatastroOrchestrationInterface:
    """Interfaz 3: orquestación cross-catastros.

    Caso de uso típico:
      "Necesito 'code_writing' bajo $0.10/1k y prefiero AI" →
      escoge entre modelos LLM, agentes 2026 y herramientas el mejor match,
      devuelve primary + fallbacks ordenados.

    Si `prefer_human=True`, prioriza suppliers humanos primero (ej:
    'notarial_certification' donde no hay AI viable).
    """

    # Prioridad por defecto: AI primero (agentes > modelos > herramientas > humanos).
    _PRIORITY_AI_FIRST = (
        "agentes_2026",
        "modelos_llm",
        "herramientas_ai",
        "suppliers_humanos",
    )
    _PRIORITY_HUMAN_FIRST = (
        "suppliers_humanos",
        "agentes_2026",
        "herramientas_ai",
        "modelos_llm",
    )

    def __init__(
        self,
        modelos_llm: CatastroModelosLLM,
        agentes_2026: CatastroAgentes2026,
        herramientas_ai: CatastroHerramientasAI,
        suppliers_humanos: CatastroSuppliers,
    ) -> None:
        self._catastros: Dict[str, Any] = {
            "modelos_llm": modelos_llm,
            "agentes_2026": agentes_2026,
            "herramientas_ai": herramientas_ai,
            "suppliers_humanos": suppliers_humanos,
        }
        # Reusar SearchInterface internamente para no duplicar lógica de tags.
        self._search = CatastroSearchInterface(modelos_llm, agentes_2026, herramientas_ai, suppliers_humanos)

    def orchestrate(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Find best resource matching query + fallbacks.

        Query schema (dict-based para alinear con spec §TC):
            {
              "capability": "code_writing",      # REQUIRED, string
              "budget_per_1k": 0.10,             # opcional, USD per 1k tokens/actions
              "latency_max_ms": 5000,            # opcional, int
              "prefer_human": false,             # opcional, default false
              "match": "any",                    # opcional, "any"|"all", default "any"
            }

        Returns:
            {
              "primary": {...row..., "_catastro": "..."},
              "primary_catastro": "...",
              "fallbacks": [{...row..., "_catastro": "..."}, ...],
              "rationale": "Selected X from Y (...)",
            }

        Raises:
            ValueError si query no tiene "capability".
            NoSuitableResourceError si ningún recurso matchea constraints.
        """
        capability = query.get("capability")
        if not capability or not isinstance(capability, str):
            raise ValueError(f"query['capability'] es obligatorio y debe ser string — got {capability!r}")

        budget = query.get("budget_per_1k")
        latency_max = query.get("latency_max_ms")
        prefer_human = bool(query.get("prefer_human", False))
        match = query.get("match", "any")

        priority = self._PRIORITY_HUMAN_FIRST if prefer_human else self._PRIORITY_AI_FIRST

        # Recolectar candidatos siguiendo el orden de prioridad.
        candidates: List[Dict[str, Any]] = []
        for name in priority:
            matches = self._search.search([capability], catastro=name, match=match)
            for row in matches:
                if not self._matches_constraints(row, name, budget, latency_max):
                    continue
                candidates.append(row)

        if not candidates:
            raise NoSuitableResourceError(
                f"No resource matches capability={capability!r}, "
                f"budget={budget}, latency_max_ms={latency_max}, "
                f"prefer_human={prefer_human}"
            )

        primary = candidates[0]
        fallbacks = candidates[1:]

        rationale = (
            f"Selected {primary.get('key', '?')} from "
            f"{primary.get('_catastro')} "
            f"({'human-first' if prefer_human else 'AI-first'} priority). "
            f"{len(fallbacks)} fallbacks available."
        )

        return {
            "primary": primary,
            "primary_catastro": primary.get("_catastro"),
            "fallbacks": fallbacks,
            "rationale": rationale,
        }

    @staticmethod
    def _matches_constraints(
        row: Dict[str, Any],
        catastro_name: str,
        budget: Optional[float],
        latency_max_ms: Optional[int],
    ) -> bool:
        """Apply budget + latency constraints to a candidate row.

        Heurísticas por catastro (ya que los campos difieren):
          - modelos_llm: budget se compara con max(cost_per_1k_input, cost_per_1k_output)
          - herramientas_ai: budget se compara con cost_per_call
          - agentes_2026 y suppliers_humanos: budget no aplica (no expone costo en vista)
          - latency: metadata.typical_latency_ms si existe
        """
        if budget is not None:
            cost: Optional[float] = None
            if catastro_name == "modelos_llm":
                ci = row.get("cost_per_1k_input")
                co = row.get("cost_per_1k_output")
                costs = [c for c in (ci, co) if isinstance(c, (int, float))]
                cost = max(costs) if costs else None
            elif catastro_name == "herramientas_ai":
                c = row.get("cost_per_call")
                if isinstance(c, (int, float)):
                    cost = c
            # agentes/suppliers: no enforce de budget (None → pasa).
            if cost is not None and cost > budget:
                return False

        if latency_max_ms is not None:
            metadata = row.get("metadata") or {}
            if isinstance(metadata, dict):
                lat = metadata.get("typical_latency_ms")
                if isinstance(lat, (int, float)) and lat > latency_max_ms:
                    return False

        return True


# =========================================================================
# Factory conveniente
# =========================================================================


def build_interfaces(
    modelos_llm: CatastroModelosLLM,
    agentes_2026: CatastroAgentes2026,
    herramientas_ai: CatastroHerramientasAI,
    suppliers_humanos: CatastroSuppliers,
) -> Dict[str, Any]:
    """Factory que crea las 3 interfaces sobre las 4 instancias ya cargadas.

    Uso típico:
        modelos = CatastroModelosLLM(db); await modelos.load_from_db()
        agentes = CatastroAgentes2026(db); await agentes.load_from_db()
        tools = CatastroHerramientasAI(db); await tools.load_from_db()
        suppliers = CatastroSuppliers(db); await suppliers.load_from_db()
        interfaces = build_interfaces(modelos, agentes, tools, suppliers)
        result = interfaces["orchestration"].orchestrate({"capability": "code_writing"})
    """
    return {
        "lookup": CatastroLookupInterface(modelos_llm, agentes_2026, herramientas_ai, suppliers_humanos),
        "search": CatastroSearchInterface(modelos_llm, agentes_2026, herramientas_ai, suppliers_humanos),
        "orchestration": CatastroOrchestrationInterface(modelos_llm, agentes_2026, herramientas_ai, suppliers_humanos),
    }


__all__ = [
    "CatastroLookupInterface",
    "CatastroSearchInterface",
    "CatastroOrchestrationInterface",
    "NoSuitableResourceError",
    "build_interfaces",
]
