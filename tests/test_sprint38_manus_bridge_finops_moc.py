"""
Sprint 38 Tests — Manus Bridge Fix, Stubs Eliminados, FinOps Dashboard, MOC Panel
==================================================================================

Tests que verifican:
1. manus_bridge: tool_dispatch usa handle_manus_bridge (no execute_manus_bridge)
2. Stubs eliminados: engine.py y nodes.py lanzan error real cuando no hay router
3. FinOps dashboard: finops_routes.py tiene los endpoints /summary y /history
4. MOC Panel: moc_screen.dart y gateway /api/moc existen con el contenido correcto

Sprint 38 — 2026-04-30
"""

import ast
import os
import re

import pytest

# ── Paths ─────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KERNEL = os.path.join(ROOT, "kernel")
TOOLS = os.path.join(ROOT, "tools")
APPS = os.path.join(ROOT, "apps", "mobile")


# ══════════════════════════════════════════════════════════════════════
# 1. Manus Bridge — tool_dispatch fix
# ══════════════════════════════════════════════════════════════════════

class TestManusBridgeDispatchFix:
    """Verifica que tool_dispatch usa handle_manus_bridge (no execute_manus_bridge)."""

    def _read(self, path: str) -> str:
        with open(path) as f:
            return f.read()

    def test_tool_dispatch_imports_handle_manus_bridge(self):
        """tool_dispatch.py debe importar handle_manus_bridge, no execute_manus_bridge."""
        content = self._read(os.path.join(KERNEL, "tool_dispatch.py"))
        assert "handle_manus_bridge" in content, (
            "tool_dispatch debe importar handle_manus_bridge"
        )

    def test_tool_dispatch_no_execute_manus_bridge(self):
        """tool_dispatch.py NO debe usar execute_manus_bridge (no existe)."""
        content = self._read(os.path.join(KERNEL, "tool_dispatch.py"))
        assert "execute_manus_bridge" not in content, (
            "execute_manus_bridge no existe en manus_bridge.py — debe usarse handle_manus_bridge"
        )

    def test_manus_bridge_has_handle_function(self):
        """tools/manus_bridge.py debe exponer handle_manus_bridge."""
        content = self._read(os.path.join(TOOLS, "manus_bridge.py"))
        assert "def handle_manus_bridge" in content, (
            "manus_bridge.py debe tener la función handle_manus_bridge"
        )

    def test_tool_dispatch_uses_run_in_executor(self):
        """tool_dispatch.py debe usar run_in_executor para llamar a la función síncrona."""
        content = self._read(os.path.join(KERNEL, "tool_dispatch.py"))
        assert "run_in_executor" in content, (
            "handle_manus_bridge es síncrona — debe ejecutarse en run_in_executor"
        )

    def test_manus_bridge_tool_spec_exists(self):
        """tool_dispatch.py debe tener el ToolSpec de manus_bridge registrado."""
        content = self._read(os.path.join(KERNEL, "tool_dispatch.py"))
        assert 'name="manus_bridge"' in content or "name='manus_bridge'" in content, (
            "El ToolSpec de manus_bridge debe estar registrado en get_tool_specs()"
        )


# ══════════════════════════════════════════════════════════════════════
# 2. Stubs eliminados
# ══════════════════════════════════════════════════════════════════════

class TestStubsEliminated:
    """Verifica que los stubs de fallback fueron eliminados."""

    def _read(self, path: str) -> str:
        with open(path) as f:
            return f.read()

    def test_engine_no_stub_response(self):
        """kernel/engine.py NO debe tener el stub '[stub] {model} would respond'."""
        content = self._read(os.path.join(KERNEL, "engine.py"))
        assert "[stub]" not in content, (
            "El stub '[stub] {model} would respond...' debe ser eliminado de engine.py"
        )

    def test_nodes_no_stub_response(self):
        """kernel/nodes.py NO debe tener el stub '[stub] {model} would respond'."""
        content = self._read(os.path.join(KERNEL, "nodes.py"))
        assert "[stub]" not in content, (
            "El stub '[stub] {model} would respond...' debe ser eliminado de nodes.py"
        )

    def test_engine_has_real_error_on_no_router(self):
        """kernel/engine.py debe emitir un error real cuando no hay router."""
        content = self._read(os.path.join(KERNEL, "engine.py"))
        assert "stream_no_router" in content, (
            "engine.py debe loggear 'stream_no_router' cuando el router no está disponible"
        )

    def test_nodes_raises_on_no_router(self):
        """kernel/nodes.py debe lanzar RuntimeError cuando no hay router."""
        content = self._read(os.path.join(KERNEL, "nodes.py"))
        assert "execute_no_router" in content, (
            "nodes.py debe loggear 'execute_no_router' y lanzar RuntimeError"
        )
        assert "RuntimeError" in content, (
            "nodes.py debe lanzar RuntimeError cuando el router no está disponible"
        )


# ══════════════════════════════════════════════════════════════════════
# 3. FinOps Dashboard
# ══════════════════════════════════════════════════════════════════════

class TestFinOpsDashboard:
    """Verifica que el FinOps dashboard está correctamente implementado."""

    def _read(self, path: str) -> str:
        with open(path) as f:
            return f.read()

    def test_finops_routes_file_exists(self):
        """kernel/finops_routes.py debe existir."""
        path = os.path.join(KERNEL, "finops_routes.py")
        assert os.path.exists(path), "kernel/finops_routes.py debe existir"

    def test_finops_routes_has_summary_endpoint(self):
        """finops_routes.py debe tener el endpoint /summary."""
        content = self._read(os.path.join(KERNEL, "finops_routes.py"))
        assert '"/summary"' in content or "'/summary'" in content, (
            "finops_routes.py debe tener el endpoint GET /summary"
        )

    def test_finops_routes_has_history_endpoint(self):
        """finops_routes.py debe tener el endpoint /history."""
        content = self._read(os.path.join(KERNEL, "finops_routes.py"))
        assert '"/history"' in content or "'/history'" in content, (
            "finops_routes.py debe tener el endpoint GET /history"
        )

    def test_finops_routes_has_set_deps(self):
        """finops_routes.py debe tener set_finops_deps para inyección de dependencias."""
        content = self._read(os.path.join(KERNEL, "finops_routes.py"))
        assert "def set_finops_deps" in content, (
            "finops_routes.py debe exponer set_finops_deps(db, finops)"
        )

    def test_finops_routes_registered_in_main(self):
        """main.py debe registrar el router de finops_routes."""
        content = self._read(os.path.join(KERNEL, "main.py"))
        assert "finops_routes" in content, (
            "main.py debe importar y registrar finops_routes"
        )
        assert "finops_dashboard_routes_registered" in content, (
            "main.py debe loggear 'finops_dashboard_routes_registered'"
        )

    def test_finops_summary_queries_run_costs(self):
        """finops_routes.py debe consultar la tabla run_costs."""
        content = self._read(os.path.join(KERNEL, "finops_routes.py"))
        assert "run_costs" in content, (
            "finops_routes.py debe consultar la tabla run_costs para el dashboard"
        )

    def test_finops_summary_queries_job_executions(self):
        """finops_routes.py debe consultar job_executions para costos de jobs autónomos."""
        content = self._read(os.path.join(KERNEL, "finops_routes.py"))
        assert "job_executions" in content, (
            "finops_routes.py debe consultar job_executions para costos de jobs"
        )

    def test_gateway_finops_uses_summary_endpoint(self):
        """gateway/server.py debe usar /v1/finops/summary en lugar de /v1/usage/summary."""
        content = self._read(os.path.join(APPS, "gateway", "server.py"))
        assert "/v1/finops/summary" in content, (
            "El gateway debe usar /v1/finops/summary (nuevo endpoint real)"
        )
        assert "/v1/usage/summary" not in content, (
            "El gateway no debe usar el viejo /v1/usage/summary (devuelve 404)"
        )


# ══════════════════════════════════════════════════════════════════════
# 4. MOC Panel Flutter
# ══════════════════════════════════════════════════════════════════════

class TestMocPanelFlutter:
    """Verifica que el MOC Panel está correctamente implementado en Flutter."""

    def _read(self, path: str) -> str:
        with open(path) as f:
            return f.read()

    def test_moc_screen_exists(self):
        """apps/mobile/lib/features/moc/moc_screen.dart debe existir."""
        path = os.path.join(APPS, "lib", "features", "moc", "moc_screen.dart")
        assert os.path.exists(path), "moc_screen.dart debe existir"

    def test_moc_screen_has_moc_screen_class(self):
        """moc_screen.dart debe definir la clase MocScreen."""
        content = self._read(
            os.path.join(APPS, "lib", "features", "moc", "moc_screen.dart")
        )
        assert "class MocScreen" in content, (
            "moc_screen.dart debe definir la clase MocScreen"
        )

    def test_moc_screen_has_synthesis_trigger(self):
        """moc_screen.dart debe tener el botón de síntesis manual."""
        content = self._read(
            os.path.join(APPS, "lib", "features", "moc", "moc_screen.dart")
        )
        assert "triggerMocSynthesis" in content or "sintetizar" in content.lower(), (
            "moc_screen.dart debe tener un botón para disparar síntesis manual"
        )

    def test_moc_screen_shows_insights(self):
        """moc_screen.dart debe mostrar los insights del MOC."""
        content = self._read(
            os.path.join(APPS, "lib", "features", "moc", "moc_screen.dart")
        )
        assert "latest_insights" in content or "_InsightCard" in content, (
            "moc_screen.dart debe mostrar los insights del MOC"
        )

    def test_kernel_service_has_get_moc_status(self):
        """KernelService debe tener el método getMocStatus."""
        content = self._read(
            os.path.join(APPS, "lib", "services", "kernel_service.dart")
        )
        assert "getMocStatus" in content, (
            "KernelService debe tener el método getMocStatus()"
        )

    def test_kernel_service_has_trigger_synthesis(self):
        """KernelService debe tener el método triggerMocSynthesis."""
        content = self._read(
            os.path.join(APPS, "lib", "services", "kernel_service.dart")
        )
        assert "triggerMocSynthesis" in content, (
            "KernelService debe tener el método triggerMocSynthesis()"
        )

    def test_config_has_moc_endpoint(self):
        """AppConfig debe tener mocEndpoint."""
        content = self._read(
            os.path.join(APPS, "lib", "core", "config.dart")
        )
        assert "mocEndpoint" in content, (
            "AppConfig debe tener la constante mocEndpoint"
        )

    def test_router_has_moc_route(self):
        """router.dart debe tener la ruta /moc."""
        content = self._read(
            os.path.join(APPS, "lib", "core", "router.dart")
        )
        assert "'/moc'" in content or '"/moc"' in content, (
            "router.dart debe tener la ruta '/moc'"
        )
        assert "MocScreen" in content, (
            "router.dart debe usar MocScreen en la ruta /moc"
        )

    def test_shell_scaffold_has_moc_drawer_item(self):
        """ShellScaffold debe tener el item MOC en el drawer."""
        content = self._read(
            os.path.join(APPS, "lib", "widgets", "shell_scaffold.dart")
        )
        assert "'/moc'" in content or '"/moc"' in content, (
            "ShellScaffold debe tener el item MOC en el drawer"
        )
        assert "MOC" in content, (
            "El drawer debe mostrar 'MOC' como label"
        )

    def test_gateway_has_moc_endpoint(self):
        """gateway/server.py debe tener el endpoint /api/moc."""
        content = self._read(os.path.join(APPS, "gateway", "server.py"))
        assert '"/api/moc"' in content or "'/api/moc'" in content, (
            "El gateway debe tener el endpoint GET /api/moc"
        )

    def test_gateway_has_moc_sintetizar_endpoint(self):
        """gateway/server.py debe tener el endpoint POST /api/moc/sintetizar."""
        content = self._read(os.path.join(APPS, "gateway", "server.py"))
        assert "sintetizar" in content, (
            "El gateway debe tener el endpoint POST /api/moc/sintetizar"
        )
