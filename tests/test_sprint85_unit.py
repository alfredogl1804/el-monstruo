"""
Test Suite Sprint 85 — Unit Tests
====================================
Tests unitarios sin red para los 6 Bloques del Sprint 85.

Cobertura:
- Bloque 1: ProductArchitect (estructura del Brief, validación, vertical detection)
- Bloque 2: TaskPlanner heurística _es_proyecto_web + wiring del Brief
- Bloque 3: CriticVisual rúbrica + scoring sintético
- Bloque 4: SQL schema (verificación de archivo, no ejecución)
- Bloque 5: generate_hero_image en modo placeholder
- Bloque 6: Verticals YAML files (parsing + estructura)

Run:
    pytest tests/test_sprint85_unit.py -v

NO requiere: Supabase, Anthropic API, Replicate, Browserless.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# ── Bloque 6: Verticals ──────────────────────────────────────────────────────
class TestBloque6Verticals:
    """6 archivos YAML deben existir y parsear con schema mínimo."""

    EXPECTED_VERTICALS = [
        "education_arts",
        "saas_b2b",
        "restaurant",
        "professional_services",
        "ecommerce_artisanal",
        "marketplace_services",
    ]

    def test_all_yaml_files_exist(self):
        verticals_dir = REPO / "kernel" / "brand" / "verticals"
        assert verticals_dir.is_dir(), "Carpeta kernel/brand/verticals/ no existe"
        for v in self.EXPECTED_VERTICALS:
            f = verticals_dir / f"{v}.yaml"
            assert f.is_file(), f"Falta {v}.yaml"

    def test_yaml_files_parse(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML no instalado en el environment")

        verticals_dir = REPO / "kernel" / "brand" / "verticals"
        for v in self.EXPECTED_VERTICALS:
            with open(verticals_dir / f"{v}.yaml") as f:
                data = yaml.safe_load(f)
            assert isinstance(data, dict), f"{v}.yaml no es dict"
            # El schema real usa vertical_id (no vertical) y defaults (no brand_defaults)
            assert data.get("vertical_id") == v, f"{v}.yaml: vertical_id key incorrecta"
            assert "defaults" in data, f"{v}.yaml: falta defaults"
            # display_name + description son requeridos por el Product Architect
            assert "display_name" in data, f"{v}.yaml: falta display_name"
            assert "description" in data, f"{v}.yaml: falta description"


# ── Bloque 4: SQL schema ─────────────────────────────────────────────────────
class TestBloque4SqlSchema:
    """El archivo SQL existe y tiene las tablas + índices del SPEC."""

    SQL_PATH = REPO / "scripts" / "016_sprint85_briefs_deployments.sql"

    def test_sql_file_exists(self):
        assert self.SQL_PATH.is_file(), "Falta scripts/016_sprint85_briefs_deployments.sql"

    def test_sql_has_briefs_and_deployments_tables(self):
        sql = self.SQL_PATH.read_text()
        assert "CREATE TABLE" in sql.upper()
        assert "briefs" in sql.lower(), "Tabla briefs ausente"
        assert "deployments" in sql.lower(), "Tabla deployments ausente"

    def test_sql_has_critic_score_column(self):
        sql = self.SQL_PATH.read_text().lower()
        assert "critic_score" in sql, "Columna critic_score ausente"
        assert "quality_passed" in sql, "Columna quality_passed ausente"


# ── Bloque 1: ProductArchitect ───────────────────────────────────────────────
class TestBloque1ProductArchitect:
    """ProductArchitect debe instanciarse y producir Brief con estructura mínima."""

    def setup_method(self):
        # Mock structlog si necesario
        try:
            import structlog  # noqa
        except ImportError:
            sys.modules["structlog"] = type(sys)("structlog")
            sys.modules["structlog"].get_logger = lambda *a, **k: type(
                "L", (), {
                    "info": lambda s, *a, **k: None,
                    "warning": lambda s, *a, **k: None,
                    "error": lambda s, *a, **k: None,
                }
            )()

    def test_import_and_instantiate(self):
        from kernel.embriones.product_architect import ProductArchitect
        pa = ProductArchitect(_sabios=None, _db=None)
        assert pa.EMBRION_ID == "product-architect"

    def test_estado(self):
        from kernel.embriones.product_architect import ProductArchitect
        pa = ProductArchitect(_sabios=None, _db=None)
        e = pa.estado()
        assert e["embrion_id"] == "product-architect"
        # Schema real expone verticales_soportados
        assert "verticales_soportados" in e
        assert len(e["verticales_soportados"]) == 6


# ── Bloque 2: TaskPlanner Brief wiring ───────────────────────────────────────
class TestBloque2PlannerBrief:
    """task_planner.py tiene la heurística + el wiring del Brief."""

    def test_keywords_constant_loaded(self):
        # Cargar solo la constante via AST sin instanciar
        import ast
        src = (REPO / "kernel" / "task_planner.py").read_text()
        tree = ast.parse(src)
        found_constant = False
        found_helper = False
        found_flag = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "WEB_PROJECT_KEYWORDS":
                        found_constant = True
                    if isinstance(tgt, ast.Name) and tgt.id == "USE_PRODUCT_ARCHITECT":
                        found_flag = True
            if isinstance(node, ast.FunctionDef) and node.name == "_es_proyecto_web":
                found_helper = True

        assert found_constant
        assert found_flag
        assert found_helper

    def test_brief_block_in_planning_prompt(self):
        src = (REPO / "kernel" / "task_planner.py").read_text()
        assert "BRIEF DEL PRODUCT ARCHITECT" in src
        assert "REGLAS DE CONTRATO" in src
        assert 'plan_context["brief"]' in src

    @pytest.mark.parametrize("text,expected", [
        ("hazme una landing del taller de Yuna", True),
        ("dame un curso de pintura al óleo", True),
        ("monta un restaurante online con menú y reserva", True),
        ("construye un dashboard SaaS para mi startup", True),
        ("calcula 2+2", False),
        ("manda un mensaje al usuario", False),
        ("redeploy del kernel", False),
    ])
    def test_es_proyecto_web_logic(self, text, expected):
        # Replicar lógica leyendo la constante del archivo
        src = (REPO / "kernel" / "task_planner.py").read_text()
        lines = src.split("\n")
        inside = False
        block = []
        for line in lines:
            if line.startswith("WEB_PROJECT_KEYWORDS = ["):
                inside = True
                block.append(line)
                continue
            if inside:
                block.append(line)
                if line.strip() == "]":
                    break
        ns = {}
        exec("\n".join(block), ns)
        keywords = ns["WEB_PROJECT_KEYWORDS"]

        def es_web(t: str) -> bool:
            tl = t.lower()
            return any(kw in tl for kw in keywords)

        assert es_web(text) == expected


# ── Bloque 3: CriticVisual rúbrica ───────────────────────────────────────────
class TestBloque3CriticVisual:

    def setup_method(self):
        try:
            import structlog  # noqa
        except ImportError:
            sys.modules["structlog"] = type(sys)("structlog")
            sys.modules["structlog"].get_logger = lambda *a, **k: type(
                "L", (), {
                    "info": lambda s, *a, **k: None,
                    "warning": lambda s, *a, **k: None,
                    "error": lambda s, *a, **k: None,
                }
            )()

    def test_rubric_sums_100(self):
        from kernel.embriones.critic_visual import RUBRICA_PESOS
        assert sum(RUBRICA_PESOS.values()) == 100

    def test_perfect_synthetic_site_passes(self):
        from kernel.embriones.critic_visual import CriticVisual
        critic = CriticVisual(_sabios=None, _db=None)
        brief_ok = {
            "brief_id": "test-001",
            "vertical": "education_arts",
            "structure": {
                "sections": [{"id": "hero"}, {"id": "what_youll_learn"},
                             {"id": "instructor"}, {"id": "pricing"}, {"id": "faq"}],
                "primary_cta": "Inscribirme ahora",
                "secondary_cta": "Ver programa",
            },
            "client_brand": {"name": "Taller Yuna", "voice": "warm"},
            "data_missing": [],
        }
        body = (
            "Taller Yuna. Hero principal. What you'll learn: técnicas avanzadas. "
            "Instructor experimentado. Pricing accesible. FAQ con preguntas. "
            "Aprende a pintar al óleo paso a paso con metodología clara y proyectos reales. "
            "Cada sesión incluye demostraciones prácticas y materiales incluidos."
        )
        scores, _ = critic._aplicar_rubrica(
            brief=brief_ok,
            hero_text="Taller Yuna",
            cta_text="Inscribirme ahora",
            body_text=body,
            head_text="<title>Yuna</title><meta property='og:title' content='X'>",
            perf_metrics={"ttfb_ms": 200, "lcp_ms": 1500, "load_time_ms": 1800},
            screenshot_mobile_path=None,
        )
        assert sum(scores.values()) >= 70

    def test_lorem_ipsum_blocks(self):
        from kernel.embriones.critic_visual import CriticVisual
        critic = CriticVisual(_sabios=None, _db=None)
        brief = {
            "brief_id": "t",
            "vertical": "education_arts",
            "structure": {"sections": [], "primary_cta": ""},
            "client_brand": {"name": "X"},
            "data_missing": [],
        }
        scores, findings = critic._aplicar_rubrica(
            brief=brief,
            hero_text="",
            cta_text="",
            body_text="Lorem ipsum dolor sit amet",
            head_text="",
            perf_metrics={},
            screenshot_mobile_path=None,
        )
        lorem_blocker = next(
            (f for f in findings if "lorem" in f.descripcion.lower()),
            None,
        )
        assert lorem_blocker is not None
        assert lorem_blocker.severity == "blocker"


# ── Bloque 5: generate_hero_image placeholder ────────────────────────────────
class TestBloque5HeroImage:

    def setup_method(self):
        try:
            import structlog  # noqa
        except ImportError:
            sys.modules["structlog"] = type(sys)("structlog")
            sys.modules["structlog"].get_logger = lambda *a, **k: type(
                "L", (), {
                    "info": lambda s, *a, **k: None,
                    "warning": lambda s, *a, **k: None,
                    "error": lambda s, *a, **k: None,
                }
            )()
        os.environ.pop("MEDIA_GEN_LIVE", None)

    def test_placeholder_mode(self):
        from tools.generate_hero_image import generate_hero_image
        result = asyncio.run(generate_hero_image(
            prompt="A warm artisan studio with sunlight",
            style="warm_artisan",
        ))
        assert result["is_placeholder"] is True
        assert "placehold" in result["url"]
        assert result["cost_usd"] == 0.0

    def test_empty_prompt_raises(self):
        from tools.generate_hero_image import generate_hero_image, HeroImageError
        with pytest.raises(HeroImageError):
            asyncio.run(generate_hero_image(prompt="", style="warm_artisan"))

    def test_aspect_ratio(self):
        from tools.generate_hero_image import _aspect_ratio_string
        assert _aspect_ratio_string(1920, 1080) == "16:9"
        assert _aspect_ratio_string(1024, 1024) == "1:1"
