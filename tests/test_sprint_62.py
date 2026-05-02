"""
tests/test_sprint_62.py
Tests del Sprint 62 — Brand Checklist Check #6

Cubre:
- 62.1 Plugin Architecture (PluginManager)
- 62.2 Data Portability Engine (PortabilityEngine)
- 62.3 Component Library (ComponentRegistry)
- 62.4 Marketplace de Templates (Marketplace)
- 62.5 Cost Optimization Engine (CostOptimizer)
"""

import asyncio

import pytest

# ===== 62.1 — Plugin Architecture =====


class TestPluginManager:
    def test_import(self):
        from kernel.plugins.plugin_manager import PluginManager, PluginMetadata

        assert PluginManager is not None
        assert PluginMetadata is not None

    def test_init(self):
        from kernel.plugins.plugin_manager import PluginManager

        pm = PluginManager()
        assert pm is not None

    def test_list_plugins_empty(self):
        from kernel.plugins.plugin_manager import PluginManager

        pm = PluginManager()
        assert pm.list_plugins() == []

    def test_to_dict(self):
        from kernel.plugins.plugin_manager import PluginManager

        pm = PluginManager()
        d = pm.to_dict()
        assert "total_plugins" in d
        assert "habilitados" in d
        assert "deshabilitados" in d
        assert "plugins" in d

    def test_plugin_no_encontrado(self):
        from kernel.plugins.plugin_manager import PluginManager, PluginNoEncontrado

        pm = PluginManager()
        with pytest.raises(PluginNoEncontrado):
            pm.get_plugin("inexistente")

    def test_plugin_ya_registrado_exception_exists(self):
        from kernel.plugins.plugin_manager import PluginYaRegistrado

        exc = PluginYaRegistrado("test-plugin")
        assert "test-plugin" in str(exc)

    def test_plugin_seguridad_exception_exists(self):
        from kernel.plugins.plugin_manager import PluginSeguridad

        exc = PluginSeguridad("test-plugin", "usa eval()")
        assert "test-plugin" in str(exc)
        assert "eval()" in str(exc)


# ===== 62.2 — Data Portability Engine =====


class TestPortabilityEngine:
    def test_import(self):
        from kernel.portability.portability_engine import PortabilityEngine

        assert PortabilityEngine is not None

    def test_init(self):
        from kernel.portability.portability_engine import PortabilityEngine

        pe = PortabilityEngine()
        assert pe is not None

    def test_to_dict(self):
        from kernel.portability.portability_engine import EXPORT_TABLES, PortabilityEngine

        pe = PortabilityEngine()
        d = pe.to_dict()
        assert "tablas_soportadas" in d
        assert d["tablas_soportadas"] == len(EXPORT_TABLES)
        assert "export_version" in d
        assert "exports_realizados" in d

    def test_export_tables_not_empty(self):
        from kernel.portability.portability_engine import EXPORT_TABLES

        assert len(EXPORT_TABLES) > 0
        assert "projects" in EXPORT_TABLES
        assert "causal_events" in EXPORT_TABLES

    def test_export_version(self):
        from kernel.portability.portability_engine import EXPORT_VERSION

        assert EXPORT_VERSION == "1.0.0"

    def test_exportacion_fallida_exception(self):
        from kernel.portability.portability_engine import ExportacionFallida

        exc = ExportacionFallida("conexión rechazada")
        assert "conexión rechazada" in str(exc)

    def test_manifiesto_invalido_exception(self):
        from kernel.portability.portability_engine import ManifiestoInvalido

        exc = ManifiestoInvalido()
        assert "manifiesto" in str(exc).lower() or "Manifiesto" in str(exc)

    def test_export_no_supabase_returns_empty(self):
        from kernel.portability.portability_engine import DataExporter

        exporter = DataExporter(supabase=None)
        result = asyncio.new_event_loop().run_until_complete(exporter._export_table("projects"))
        assert result == []

    def test_import_invalid_mode(self):
        from kernel.portability.portability_engine import DataImporter, ImportacionFallida

        importer = DataImporter(supabase=None)
        with pytest.raises(ImportacionFallida):
            asyncio.new_event_loop().run_until_complete(importer.import_from_zip(b"fake", modo="invalid_mode"))


# ===== 62.3 — Component Library =====


class TestComponentRegistry:
    def test_import(self):
        from kernel.components.registry import ComponentRegistry

        assert ComponentRegistry is not None

    def test_init(self):
        from kernel.components.registry import ComponentRegistry

        cr = ComponentRegistry()
        assert cr is not None
        assert not cr._loaded

    def test_load_builtin(self):
        from kernel.components.registry import ComponentRegistry

        cr = ComponentRegistry()
        count = asyncio.new_event_loop().run_until_complete(cr.load_all())
        assert count >= 26
        assert cr._loaded

    def test_get_by_id(self):
        from kernel.components.registry import ComponentRegistry

        cr = ComponentRegistry()
        asyncio.new_event_loop().run_until_complete(cr.load_all())
        navbar = cr.get_by_id("navbar")
        assert navbar.id == "navbar"
        assert navbar.category == "navigation"

    def test_get_by_id_not_found(self):
        from kernel.components.registry import ComponenteNoEncontrado, ComponentRegistry

        cr = ComponentRegistry()
        asyncio.new_event_loop().run_until_complete(cr.load_all())
        with pytest.raises(ComponenteNoEncontrado):
            cr.get_by_id("componente_inexistente")

    def test_get_by_category(self):
        from kernel.components.registry import ComponentRegistry

        cr = ComponentRegistry()
        asyncio.new_event_loop().run_until_complete(cr.load_all())
        nav_components = cr.get_by_category("navigation")
        assert len(nav_components) >= 4

    def test_get_for_project_type(self):
        from kernel.components.registry import ComponentRegistry

        cr = ComponentRegistry()
        asyncio.new_event_loop().run_until_complete(cr.load_all())
        saas_components = cr.get_for_project_type("saas")
        assert len(saas_components) > 0

    def test_to_dict(self):
        from kernel.components.registry import ComponentRegistry

        cr = ComponentRegistry()
        asyncio.new_event_loop().run_until_complete(cr.load_all())
        d = cr.to_dict()
        assert "total_componentes" in d
        assert d["total_componentes"] >= 26
        assert "categorias" in d


# ===== 62.4 — Marketplace =====


class TestMarketplace:
    def test_import(self):
        from kernel.marketplace.marketplace import Marketplace

        assert Marketplace is not None

    def test_init(self):
        from kernel.marketplace.marketplace import Marketplace

        m = Marketplace()
        assert m is not None

    def test_load_catalog(self):
        from kernel.marketplace.marketplace import BUILTIN_TEMPLATES, Marketplace

        m = Marketplace()
        count = asyncio.new_event_loop().run_until_complete(m.load_catalog())
        assert count >= len(BUILTIN_TEMPLATES)
        assert m._loaded

    def test_get_by_id(self):
        from kernel.marketplace.marketplace import Marketplace

        m = Marketplace()
        asyncio.new_event_loop().run_until_complete(m.load_catalog())
        template = m.get_by_id("saas-starter")
        assert template.id == "saas-starter"
        assert template.vertical == "saas"

    def test_get_by_id_not_found(self):
        from kernel.marketplace.marketplace import Marketplace, TemplateNoEncontrado

        m = Marketplace()
        asyncio.new_event_loop().run_until_complete(m.load_catalog())
        with pytest.raises(TemplateNoEncontrado):
            m.get_by_id("template_inexistente")

    def test_search_by_vertical(self):
        from kernel.marketplace.marketplace import Marketplace

        m = Marketplace()
        asyncio.new_event_loop().run_until_complete(m.load_catalog())
        results = m.search(vertical="saas")
        assert len(results) >= 1
        assert all(t.vertical == "saas" for t in results)

    def test_search_free_only(self):
        from kernel.marketplace.marketplace import Marketplace

        m = Marketplace()
        asyncio.new_event_loop().run_until_complete(m.load_catalog())
        results = m.search(free_only=True)
        assert all(t.price == 0.0 for t in results)

    def test_to_dict(self):
        from kernel.marketplace.marketplace import Marketplace

        m = Marketplace()
        asyncio.new_event_loop().run_until_complete(m.load_catalog())
        d = m.to_dict()
        assert "total_templates" in d
        assert d["total_templates"] >= 10
        assert "verticals" in d


# ===== 62.5 — Cost Optimizer =====


class TestCostOptimizer:
    def test_import(self):
        from kernel.cost_optimizer import CostOptimizer

        assert CostOptimizer is not None

    def test_init(self):
        from kernel.cost_optimizer import CostOptimizer

        co = CostOptimizer(daily_budget_usd=10.0)
        assert co.daily_budget_usd == 10.0
        assert co._gasto_hoy == 0.0

    def test_select_model_clasificacion(self):
        from kernel.cost_optimizer import CostOptimizer, TipoTarea

        co = CostOptimizer(daily_budget_usd=10.0)
        decision = co.select_model(TipoTarea.CLASIFICACION)
        assert decision.modelo_seleccionado is not None
        assert decision.costo_estimado >= 0

    def test_select_model_codigo(self):
        from kernel.cost_optimizer import CostOptimizer, TipoTarea

        co = CostOptimizer(daily_budget_usd=10.0)
        decision = co.select_model(TipoTarea.CODIGO)
        assert decision.modelo_seleccionado is not None
        # Código debe usar modelo más capaz que clasificación
        decision_clasif = co.select_model(TipoTarea.CLASIFICACION)
        assert decision.costo_estimado >= decision_clasif.costo_estimado

    def test_budget_agotado(self):
        from kernel.cost_optimizer import BudgetAgotado, CostOptimizer, TipoTarea

        co = CostOptimizer(daily_budget_usd=0.0)
        co._gasto_hoy = 0.01  # Simular budget agotado
        with pytest.raises(BudgetAgotado):
            co.select_model(TipoTarea.GENERACION)

    def test_register_actual_cost(self):
        from kernel.cost_optimizer import CostOptimizer

        co = CostOptimizer(daily_budget_usd=10.0)
        costo = co.register_actual_cost("gpt-4o-mini", 1000, 500)
        assert costo > 0
        assert co._gasto_hoy == costo

    def test_to_dict(self):
        from kernel.cost_optimizer import CostOptimizer

        co = CostOptimizer(daily_budget_usd=5.0)
        d = co.to_dict()
        assert "gasto_hoy_usd" in d
        assert "budget_diario_usd" in d
        assert "budget_restante_usd" in d
        assert "modelos_disponibles" in d

    def test_clasificacion_cheaper_than_razonamiento(self):
        from kernel.cost_optimizer import CostOptimizer, TipoTarea

        co = CostOptimizer(daily_budget_usd=10.0)
        d_clasif = co.select_model(TipoTarea.CLASIFICACION, input_tokens=1000, output_tokens=100)
        d_razon = co.select_model(TipoTarea.RAZONAMIENTO, input_tokens=1000, output_tokens=100)
        assert d_clasif.costo_estimado <= d_razon.costo_estimado
