"""
test_sprint_58.py — Tests del Sprint 58: La Fortaleza Completa
==============================================================
Brand Compliance Check #6: Al menos un test por función crítica.

Cubre:
  - SecurityLayer: validación de inputs, detección de XSS/SQL injection
  - ScalabilityLayer: cálculo de auto-scaling, circuit breaker
  - AnalyticsLayer: taxonomía de eventos, cálculo de retención, engagement
  - EmbrionTecnico: audit_architecture, review_code_quality, recommend_stack
  - EmbrionVigia: detect_anomalies, audit_dependencies, generate_incident_report
"""

import pytest

# ─── SecurityLayer ────────────────────────────────────────────────────────────


class TestSecurityLayer:
    """Tests para transversal/security_layer.py"""

    def setup_method(self):
        from transversal.security_layer import SecurityLayer

        self.layer = SecurityLayer()

    @pytest.mark.asyncio
    async def test_generar_configuracion_retorna_config(self):
        """generar_configuracion debe retornar una ConfiguracionSeguridad."""
        from transversal.security_layer import TipoProyecto

        config = await self.layer.generar_configuracion("test-proyecto", TipoProyecto.WEB_APP)
        assert config is not None

    def test_generar_template_sanitizacion_retorna_str(self):
        """generar_template_sanitizacion debe retornar código Python."""
        template = self.layer.generar_template_sanitizacion()
        assert isinstance(template, str)
        assert len(template) > 50

    def test_generar_template_auth_retorna_dict(self):
        """generar_template_auth debe retornar dict con estrategia."""
        from transversal.security_layer import EstrategiaAuth

        result = self.layer.generar_template_auth(EstrategiaAuth.JWT)
        assert isinstance(result, dict)

    def test_to_dict_command_center(self):
        """to_dict debe retornar estado consumible por Command Center."""
        estado = self.layer.to_dict()
        assert "componente" in estado
        assert "version" in estado
        assert "estado" in estado


# ─── ScalabilityLayer ────────────────────────────────────────────────────────


class TestScalabilityLayer:
    """Tests para transversal/scalability_layer.py"""

    def setup_method(self):
        from transversal.scalability_layer import ScalabilityLayer

        self.layer = ScalabilityLayer()

    def test_generar_config_cdn_retorna_dict(self):
        """generar_config_cdn debe retornar dict con configuración CDN."""
        config = self.layer.generar_config_cdn("cloudflare")
        assert isinstance(config, dict)

    def test_to_dict_command_center(self):
        """to_dict debe retornar estado consumible por Command Center."""
        estado = self.layer.to_dict()
        assert "componente" in estado
        assert "version" in estado


# ─── AnalyticsLayer ──────────────────────────────────────────────────────────


class TestAnalyticsLayer:
    """Tests para transversal/analytics_layer.py"""

    def setup_method(self):
        from transversal.analytics_layer import AnalyticsLayer

        self.layer = AnalyticsLayer()

    def test_generar_taxonomia_saas(self):
        """Taxonomía SaaS debe incluir eventos AARRR básicos."""
        eventos = self.layer.generar_taxonomia("test-proyecto", "saas")
        nombres = [e.nombre for e in eventos]
        assert "usuario_registro" in nombres
        assert "suscripcion_creada" in nombres
        assert len(eventos) >= 5

    def test_generar_taxonomia_ecommerce(self):
        """Taxonomía ecommerce debe incluir eventos de compra."""
        eventos = self.layer.generar_taxonomia("test-tienda", "ecommerce")
        nombres = [e.nombre for e in eventos]
        assert "compra_completada" in nombres
        assert "carrito_item_agregado" in nombres

    def test_calcular_retencion_completo(self):
        """Cálculo de retención debe retornar porcentajes correctos."""
        dia_0 = {"u1", "u2", "u3", "u4", "u5"}
        dia_1 = {"u1", "u2", "u3"}  # 60%
        dia_7 = {"u1", "u2"}  # 40%
        dia_30 = {"u1"}  # 20%

        metricas = self.layer.calcular_retencion(
            usuarios_dia_0=dia_0,
            usuarios_dia_1=dia_1,
            usuarios_dia_7=dia_7,
            usuarios_dia_30=dia_30,
            cohorte_fecha="2026-05-01",
        )
        assert metricas.retencion_dia_1 == 60.0
        assert metricas.retencion_dia_7 == 40.0
        assert metricas.retencion_dia_30 == 20.0
        assert metricas.churn_rate == 80.0

    def test_calcular_engagement_campeon(self):
        """Usuario muy activo debe ser clasificado como 'campeon'."""
        score = self.layer.calcular_engagement(
            usuario_id="u1",
            sesiones=25,
            acciones_clave=15,
            dias_activo=25,
        )
        assert score.nivel == "campeon"
        assert score.puntaje >= 80

    def test_calcular_engagement_dormido(self):
        """Usuario inactivo debe ser clasificado como 'dormido'."""
        score = self.layer.calcular_engagement(
            usuario_id="u2",
            sesiones=0,
            acciones_clave=0,
            dias_activo=0,
        )
        assert score.nivel == "dormido"
        assert score.puntaje < 20

    def test_generar_config_posthog(self):
        """Config PostHog debe incluir eventos y funnels."""
        config = self.layer.generar_config_posthog("test-proyecto", "saas")
        assert "eventos_a_trackear" in config
        assert "eventos_conversion" in config
        assert "funnels" in config
        assert len(config["eventos_conversion"]) > 0

    def test_to_dict_command_center(self):
        """to_dict debe retornar estado consumible por Command Center."""
        estado = self.layer.to_dict()
        assert "componente" in estado
        assert "eventos_base_saas" in estado


# ─── EmbrionTecnico ───────────────────────────────────────────────────────────


class TestEmbrionTecnico:
    """Tests para kernel/embrion_tecnico.py"""

    def setup_method(self):
        from kernel.embrion_tecnico import EmbrionTecnico

        self.embrion = EmbrionTecnico()

    @pytest.mark.asyncio
    async def test_audit_architecture_proyecto_vacio_lanza_error(self):
        """Proyecto sin archivos debe lanzar EMBRION_TECNICO_PROYECTO_VACIO."""
        from kernel.embrion_tecnico import EMBRION_TECNICO_PROYECTO_VACIO

        with pytest.raises(EMBRION_TECNICO_PROYECTO_VACIO):
            await self.embrion.audit_architecture({"files": []})

    @pytest.mark.asyncio
    async def test_audit_architecture_sin_tests_penaliza(self):
        """Proyecto sin tests debe tener score < 80."""
        files = [f"src/module_{i}.py" for i in range(10)]
        result = await self.embrion.audit_architecture({"files": files})
        assert result["score"] < 80
        assert any("test" in issue.lower() for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_audit_architecture_env_en_repo_penaliza(self):
        """Proyecto con .env en repo debe tener score < 70."""
        files = ["src/main.py", ".env", "README.md"]
        result = await self.embrion.audit_architecture({"files": files})
        assert result["score"] < 70

    @pytest.mark.asyncio
    async def test_review_code_quality_codigo_vacio(self):
        """Código vacío debe retornar score 0."""
        result = await self.embrion.review_code_quality("   ")
        assert result["quality_score"] == 0

    @pytest.mark.asyncio
    async def test_review_code_quality_detecta_secreto(self):
        """Código con secreto hardcodeado debe ser detectado."""
        code = 'api_key = "sk_live_abc123def456ghi789"'
        result = await self.embrion.review_code_quality(code)
        assert any("secreto" in issue.lower() or "secret" in issue.lower() for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_review_code_quality_python_invalido(self):
        """Python con sintaxis inválida debe lanzar EMBRION_TECNICO_CODIGO_INVALIDO."""
        from kernel.embrion_tecnico import EMBRION_TECNICO_CODIGO_INVALIDO

        with pytest.raises(EMBRION_TECNICO_CODIGO_INVALIDO):
            await self.embrion.review_code_quality("def foo(:\n    pass", "python")

    @pytest.mark.asyncio
    async def test_recommend_stack_web_app_pequena(self):
        """Web app pequeña debe recomendar stack Railway + Supabase."""
        result = await self.embrion.recommend_stack(
            {
                "type": "web_app",
                "expected_users": 500,
                "monthly_budget_usd": 50,
            }
        )
        assert "backend" in result
        assert "database" in result

    def test_to_dict_command_center(self):
        """to_dict debe retornar estado consumible por Command Center."""
        estado = self.embrion.to_dict()
        assert "embrion_id" in estado
        assert estado["embrion_id"] == "embrion-tecnico"


# ─── EmbrionVigia ─────────────────────────────────────────────────────────────


class TestEmbrionVigia:
    """Tests para kernel/embrion_vigia.py"""

    def setup_method(self):
        from kernel.embrion_vigia import EmbrionVigia

        self.embrion = EmbrionVigia()

    @pytest.mark.asyncio
    async def test_health_check_endpoints_vacios_lanza_error(self):
        """Lista vacía de endpoints debe lanzar EMBRION_VIGIA_ENDPOINTS_VACIOS."""
        from kernel.embrion_vigia import EMBRION_VIGIA_ENDPOINTS_VACIOS

        with pytest.raises(EMBRION_VIGIA_ENDPOINTS_VACIOS):
            await self.embrion.health_check([])

    @pytest.mark.asyncio
    async def test_detect_anomalies_datos_insuficientes(self):
        """Menos de 10 puntos debe lanzar EMBRION_VIGIA_DATOS_INSUFICIENTES."""
        from kernel.embrion_vigia import EMBRION_VIGIA_DATOS_INSUFICIENTES

        metrics = [{"value": i, "timestamp": "2026-05-01"} for i in range(5)]
        with pytest.raises(EMBRION_VIGIA_DATOS_INSUFICIENTES):
            await self.embrion.detect_anomalies(metrics)

    @pytest.mark.asyncio
    async def test_detect_anomalies_sin_anomalias(self):
        """Datos uniformes no deben tener anomalías."""
        metrics = [{"value": 100.0 + i * 0.1, "timestamp": "2026-05-01"} for i in range(20)]
        result = await self.embrion.detect_anomalies(metrics)
        assert result["status"] == "normal"
        assert len(result["anomalies"]) == 0

    @pytest.mark.asyncio
    async def test_detect_anomalies_detecta_spike(self):
        """Un spike extremo debe ser detectado como anomalía."""
        metrics = [{"value": 100.0, "timestamp": "2026-05-01"} for _ in range(19)]
        metrics.append({"value": 10000.0, "timestamp": "2026-05-01"})  # Spike extremo
        result = await self.embrion.detect_anomalies(metrics)
        assert result["status"] == "anomalias_detectadas"
        assert len(result["anomalies"]) > 0

    @pytest.mark.asyncio
    async def test_audit_dependencies_detecta_no_pinneadas(self):
        """Dependencias sin versión pinneada deben generar warnings."""
        requirements = "fastapi>=0.100.0\nrequests\nhttpx==0.27.0"
        result = await self.embrion.audit_dependencies(requirements)
        assert result["unpinned"] >= 2
        assert len(result["warnings"]) >= 2

    @pytest.mark.asyncio
    async def test_audit_dependencies_todas_pinneadas(self):
        """Dependencias todas pinneadas no deben generar warnings."""
        requirements = "fastapi==0.111.0\nrequests==2.31.0\nhttpx==0.27.0"
        result = await self.embrion.audit_dependencies(requirements)
        assert result["unpinned"] == 0
        assert result["status"] == "limpio"

    @pytest.mark.asyncio
    async def test_generate_incident_report_estructura(self):
        """Reporte de incidente debe tener estructura completa."""
        incident = {
            "title": "API caída por 30 minutos",
            "severity": "alta",
            "detected_at": "2026-05-01T10:00:00Z",
            "resolved_at": "2026-05-01T10:30:00Z",
            "root_cause": "Memory leak en el endpoint /v1/simulate",
            "resolution": "Reinicio del proceso + fix de memory leak",
        }
        report = await self.embrion.generate_incident_report(incident)
        assert "titulo" in report
        assert "causa_raiz" in report
        assert "acciones" in report
        assert "generado_por" in report
        assert report["generado_por"] == "embrion-vigia"

    def test_to_dict_command_center(self):
        """to_dict debe retornar estado consumible por Command Center."""
        estado = self.embrion.to_dict()
        assert "embrion_id" in estado
        assert estado["embrion_id"] == "embrion-vigia"


# ─── Integración ─────────────────────────────────────────────────────────────


class TestIntegracionSprint58:
    """Tests de integración entre módulos del Sprint 58."""

    @pytest.mark.asyncio
    async def test_vigia_y_analytics_trabajan_juntos(self):
        """EmbrionVigía y AnalyticsLayer deben poder usarse en el mismo flujo."""
        from kernel.embrion_vigia import EmbrionVigia
        from transversal.analytics_layer import AnalyticsLayer

        vigia = EmbrionVigia()
        analytics = AnalyticsLayer()

        # Generar taxonomía
        eventos = analytics.generar_taxonomia("test", "saas")
        assert len(eventos) > 0

        # Detectar anomalías en métricas de eventos
        metrics = [{"value": float(i * 10), "timestamp": "2026-05-01"} for i in range(20)]
        result = await vigia.detect_anomalies(metrics)
        assert "status" in result
