"""
El Catastro · Radar Classifier.

LLM-as-parser que extrae repos descubiertos del Markdown del agents-radar
(https://agents-radar-mcp.duanyytop.workers.dev) a estructuras tipadas para
persistir en `catastro_repos`.

Patrón reusado: 39va semilla — LLM-as-parser con Pydantic Structured Outputs
(idéntico al de `coding_classifier.py`, validado por 22 tests del Sprint 86.5).
Anti-regex sobre Markdown LLM-generated.

Capa Memento:
- Si `OPENAI_API_KEY` no está disponible, el parser degrada a heuristic mode
  (extracción simple por enlaces github/huggingface). Nunca bloquea al embrión.

Spec referencia: bridge/sprint86_5_preinvestigation/spec_integracion_radar_catastro.md
DSC referencia:  DSC-MO-009, DSC-G-007 v1.1

[Hilo Manus B - Ejecutor Tecnico] · Sprint CATASTRO-C-SLICE-001 · 2026-05-11
"""
import logging
import os
import re
from typing import Optional

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


# ============================================================================
# VOCABULARIO CONTROLADO DE FUENTES (matchea agents_radar.REPORT_TYPES)
# ============================================================================

RADAR_FUENTES_VOCABULARY = (
    "github_trending",
    "huggingface",
    "product_hunt",
    "hacker_news",
    "arxiv",
    "anthropic_blog",
    "openai_blog",
    "dev_to",
    "lobsters",
    "claude_code_skills",
)


# ============================================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================================

class RadarRepo(BaseModel):
    """Un repo individual extraído del Markdown del radar."""

    id: str = Field(
        ...,
        description="ID compuesto: 'github:owner/repo', 'hf:owner/repo', 'prodhunt:slug', etc."
    )
    nombre: str = Field(..., description="Nombre legible (ej. 'AutoGPT').")
    proveedor: str = Field(..., description="Owner/org (ej. 'Significant-Gravitas').")
    url: str = Field(..., description="URL completa al repo o producto.")
    descripcion: Optional[str] = Field(None, description="Descripción corta (1-2 oraciones).")
    fuente: str = Field(
        ...,
        description=f"Fuente del radar. Vocabulario: {', '.join(RADAR_FUENTES_VOCABULARY)}"
    )
    stars_count: Optional[int] = Field(None, description="Stars de GitHub (si aplica).")
    topics: list[str] = Field(default_factory=list, description="Tags/topics detectados.")


class RadarParseResult(BaseModel):
    """Output estructurado del parser sobre un reporte completo."""

    repos: list[RadarRepo] = Field(default_factory=list)
    total_extraidos: int = Field(0, description="Cantidad total extraída.")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confianza del parser.")
    notes: str = Field("", description="Notas del parser (warnings, etc.).")


# ============================================================================
# RADAR CLASSIFIER
# ============================================================================

class RadarClassifier:
    """
    Parser estructurado de reportes Markdown del agents-radar.

    Input:  Markdown crudo (ej. output de `agents_radar.get_daily_digest()`)
    Output: RadarParseResult con repos tipados listos para INSERT en catastro_repos.
    """

    def __init__(self, *, use_llm: bool = True, model: str = "gpt-4o-mini") -> None:
        """
        Args:
            use_llm: Si True, intenta LLM-as-parser. Si False o no disponible,
                     heuristic mode (regex sobre links + headings).
            model:   Modelo OpenAI a usar (default: gpt-4o-mini, barato).
        """
        self.use_llm = use_llm
        self.model = model

    def parse(self, markdown: str, *, fuente_hint: Optional[str] = None) -> RadarParseResult:
        """
        Parsea un reporte del radar y devuelve repos estructurados.

        Args:
            markdown:    Texto Markdown del reporte (de get_daily_digest()).
            fuente_hint: Fuente esperada (matchea RADAR_FUENTES_VOCABULARY).
                         Si se pasa, ayuda al parser a sesgar la clasificación.

        Returns:
            RadarParseResult con lista de RadarRepo extraídos y validados.
        """
        if not markdown or len(markdown.strip()) < 20:
            return RadarParseResult(
                repos=[], total_extraidos=0, confidence=0.0,
                notes="markdown vacío o muy corto",
            )

        if self.use_llm and self._llm_available():
            try:
                return self._parse_with_llm(markdown, fuente_hint)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "radar_classifier_llm_failed_fallback",
                    extra={"error": str(e), "fuente_hint": fuente_hint},
                )
                return self._parse_heuristic(markdown, fuente_hint)
        return self._parse_heuristic(markdown, fuente_hint)

    def _llm_available(self) -> bool:
        """Capa Memento: lee env var en runtime, nunca cachea."""
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _parse_with_llm(
        self, markdown: str, fuente_hint: Optional[str]
    ) -> RadarParseResult:
        """LLM-as-parser con Structured Outputs Pydantic (39va semilla)."""
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("openai SDK no instalado") from e

        # Truncar markdown a límite razonable (8K chars ~ 2K tokens)
        truncated = markdown[:8000]

        client = OpenAI()
        prompt = self._build_prompt(truncated, fuente_hint)

        response = client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos un parser estricto de reportes Markdown del "
                        "agents-radar (digest diario de IA). Extraés repos "
                        "individuales con sus metadatos al schema dado. "
                        "NO inventás repos que no estén en el texto."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format=RadarParseResult,
        )

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("LLM devolvió None en structured parse")

        # Validar fuentes contra vocabulario controlado
        valid_repos: list[RadarRepo] = []
        for repo in parsed.repos:
            if repo.fuente not in RADAR_FUENTES_VOCABULARY:
                logger.debug(
                    "radar_classifier_invalid_fuente_descartada",
                    extra={"id": repo.id, "fuente": repo.fuente},
                )
                continue
            valid_repos.append(repo)

        parsed.repos = valid_repos
        parsed.total_extraidos = len(valid_repos)
        return parsed

    def _parse_heuristic(
        self, markdown: str, fuente_hint: Optional[str]
    ) -> RadarParseResult:
        """Fallback determinístico: extrae links GitHub + HuggingFace por regex."""
        repos: list[RadarRepo] = []
        seen_ids: set[str] = set()

        # GitHub repos
        for match in re.finditer(
            r"https?://github\.com/([\w.\-]+)/([\w.\-]+)", markdown
        ):
            owner, name = match.group(1), match.group(2).rstrip(".,)").rstrip("/")
            repo_id = f"github:{owner}/{name}"
            if repo_id in seen_ids:
                continue
            seen_ids.add(repo_id)
            repos.append(RadarRepo(
                id=repo_id,
                nombre=name,
                proveedor=owner,
                url=f"https://github.com/{owner}/{name}",
                fuente=fuente_hint or "github_trending",
                topics=[],
            ))

        # HuggingFace models
        for match in re.finditer(
            r"https?://huggingface\.co/([\w.\-]+)/([\w.\-]+)", markdown
        ):
            owner, name = match.group(1), match.group(2).rstrip(".,)").rstrip("/")
            if owner in {"datasets", "spaces"}:
                continue
            repo_id = f"hf:{owner}/{name}"
            if repo_id in seen_ids:
                continue
            seen_ids.add(repo_id)
            repos.append(RadarRepo(
                id=repo_id,
                nombre=name,
                proveedor=owner,
                url=f"https://huggingface.co/{owner}/{name}",
                fuente="huggingface",
                topics=[],
            ))

        return RadarParseResult(
            repos=repos,
            total_extraidos=len(repos),
            confidence=0.4,  # heuristic = baja confianza
            notes=f"heuristic mode (regex github+hf), {len(repos)} repos",
        )

    def _build_prompt(self, markdown: str, fuente_hint: Optional[str]) -> str:
        vocab_str = ", ".join(RADAR_FUENTES_VOCABULARY)
        hint_line = (
            f"Pista de fuente (sesgar clasificación): {fuente_hint}\n"
            if fuente_hint else ""
        )
        return (
            f"{hint_line}"
            f"Vocabulario controlado de fuentes (USAR SOLO ESTOS): {vocab_str}\n\n"
            f"Reporte Markdown del agents-radar:\n"
            f"---\n{markdown}\n---\n\n"
            f"Extraé cada repo/proyecto/producto IA mencionado como un objeto "
            f"RadarRepo. Reglas:\n"
            f"- id: 'github:owner/repo' para GitHub, 'hf:owner/repo' para HF, "
            f"'prodhunt:slug' para Product Hunt, 'arxiv:paper-id' para arXiv.\n"
            f"- fuente: SIEMPRE del vocabulario de arriba.\n"
            f"- topics: 1-5 tags semánticos breves (lowercase, hyphenated).\n"
            f"- NO inventés stars_count si no está explícito en el texto.\n"
            f"- Devolvé máximo 30 repos. Priorizá los más prominentes."
        )
