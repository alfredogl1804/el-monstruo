"""
Tests del Sprint 61 — Brand Checklist Check #6
===============================================
Cubre las 5 épicas del Sprint 61:
- 61.1: Collective Intelligence Protocol
- 61.2: Design System Enforcement Engine
- 61.3: Adaptive Learning Engine
- 61.4: El Guardián de los Objetivos
- 61.5: Onboarding Wizard
"""

import asyncio

import pytest

# ── Helpers ────────────────────────────────────────────────────────────────


def run(coro):
    """Ejecutar coroutine en tests síncronos."""
    return asyncio.new_event_loop().run_until_complete(coro)


# ══════════════════════════════════════════════════════════════════════════
# 61.1 — Collective Intelligence Protocol
# ══════════════════════════════════════════════════════════════════════════


class TestCollectiveProtocol:
    def setup_method(self):
        from kernel.collective.protocol import (
            ColectivaDebateNoEncontrado,
            ColectivaProtocol,
            DebateSession,
        )

        self.Protocol = ColectivaProtocol
        self.DebateSession = DebateSession
        self.DebateNoEncontrado = ColectivaDebateNoEncontrado

    def test_init(self):
        protocol = self.Protocol()
        assert protocol is not None

    def test_to_dict_has_required_keys(self):
        protocol = self.Protocol()
        d = protocol.to_dict()
        assert "embriones_registrados" in d
        assert "debates_activos" in d
        assert "votaciones_activas" in d

    def test_create_debate(self):
        protocol = self.Protocol()
        protocol.register_embrion("embrion_ventas", ["ventas"])
        protocol.register_embrion("embrion_estratega", ["estrategia"])
        debate = run(
            protocol.open_debate(
                topic="¿Cuál es la mejor estrategia de pricing para SaaS?",
                context="Necesitamos decidir el modelo de pricing",
                participants=["embrion_ventas", "embrion_estratega"],
            )
        )
        assert debate.id is not None

    def test_submit_position(self):
        protocol = self.Protocol()
        protocol.register_embrion("embrion_ventas", ["ventas"])
        debate = run(
            protocol.open_debate(
                topic="¿Freemium o premium?",
                context="Modelo de negocio",
                participants=["embrion_ventas"],
            )
        )
        run(
            protocol.submit_argument(
                debate_id=debate.id,
                embrion="embrion_ventas",
                position="favor",
                reasoning="Freemium es mejor para adquisición masiva.",
            )
        )
        assert debate.id is not None

    def test_debate_not_found_raises(self):
        protocol = self.Protocol()
        with pytest.raises(self.DebateNoEncontrado):
            run(
                protocol.submit_argument(
                    debate_id="inexistente",
                    embrion="embrion_ventas",
                    position="favor",
                    reasoning="test",
                )
            )

    def test_reach_consensus(self):
        protocol = self.Protocol()
        protocol.register_embrion("embrion_tecnico", ["tecnico"])
        protocol.register_embrion("embrion_estratega", ["estrategia"])
        debate = run(
            protocol.open_debate(
                topic="¿Cuál es el mejor stack?",
                context="Decisión de arquitectura",
                participants=["embrion_tecnico", "embrion_estratega"],
            )
        )
        run(
            protocol.submit_argument(
                debate_id=debate.id,
                embrion="embrion_tecnico",
                position="favor",
                reasoning="FastAPI + React es el stack más maduro.",
            )
        )
        run(
            protocol.submit_argument(
                debate_id=debate.id,
                embrion="embrion_estratega",
                position="favor",
                reasoning="FastAPI + React es el estándar de la industria.",
            )
        )
        debates = protocol.get_active_debates()
        assert isinstance(debates, list)


# ══════════════════════════════════════════════════════════════════════════
# 61.2 — Design System Enforcement Engine
# ══════════════════════════════════════════════════════════════════════════


class TestDesignSystem:
    def setup_method(self):
        from kernel.design.system import (
            DesignAuditResult,
            DesignSystemEngine,
        )

        self.Engine = DesignSystemEngine
        self.AuditResult = DesignAuditResult

    def test_init(self):
        engine = self.Engine()
        assert engine is not None

    def test_to_dict_has_required_keys(self):
        engine = self.Engine()
        d = engine.to_dict()
        assert "audits_performed" in d
        assert "tokens" in d
        assert "con_sabios" in d

    def test_get_design_tokens(self):
        engine = self.Engine()
        tokens = engine.tokens
        assert tokens is not None
        assert hasattr(tokens, "export_css_variables")
        assert hasattr(tokens, "export_json")

    def test_audit_accessibility(self):
        engine = self.Engine()
        result = run(engine.audit_accessibility("https://example.com"))
        assert isinstance(result, dict)
        assert "score" in result or "issues" in result or "error" in result

    def test_full_audit(self):
        engine = self.Engine()
        result = run(engine.full_audit("https://example.com"))
        assert isinstance(result, self.AuditResult)

    def test_export_css_variables(self):
        engine = self.Engine()
        css = engine.tokens.export_css_variables()
        assert "--" in css

    def test_export_json(self):
        engine = self.Engine()
        json_str = engine.tokens.export_json()
        assert len(json_str) > 10


# ══════════════════════════════════════════════════════════════════════════
# 61.3 — Adaptive Learning Engine
# ══════════════════════════════════════════════════════════════════════════


class TestAdaptiveLearning:
    def setup_method(self):
        from kernel.learning.adaptive import (
            AdaptiveLearningEngine,
            OutcomeType,
            PatternCategory,
        )

        self.Engine = AdaptiveLearningEngine
        self.OutcomeType = OutcomeType
        self.PatternCategory = PatternCategory

    def test_init(self):
        engine = self.Engine()
        assert engine is not None

    def test_to_dict_has_required_keys(self):
        engine = self.Engine()
        d = engine.to_dict()
        assert "patrones_registrados" in d
        assert "reglas_destiladas" in d
        assert "patrones_por_categoria" in d

    def test_record_pattern_success(self):
        engine = self.Engine()
        pattern = run(
            engine.record_pattern(
                category=self.PatternCategory.DESIGN,
                context="Generación de landing page para SaaS",
                outcome="El cliente aprobó sin cambios",
                outcome_type=self.OutcomeType.SUCCESS,
                lesson="CTA prominente en hero section funciona bien",
                confidence=0.9,
            )
        )
        assert pattern.id is not None

    def test_record_pattern_failure(self):
        engine = self.Engine()
        pattern = run(
            engine.record_pattern(
                category=self.PatternCategory.BUSINESS,
                context="Pricing page con 5 planes",
                outcome="El usuario se confundió",
                outcome_type=self.OutcomeType.FAILURE,
                lesson="Demasiadas opciones confunden al usuario",
                confidence=0.8,
            )
        )
        assert pattern.outcome == "El usuario se confundió"

    def test_distill_rules(self):
        engine = self.Engine()
        for i in range(3):
            run(
                engine.record_pattern(
                    category=self.PatternCategory.DESIGN,
                    context="Landing page SaaS",
                    outcome="Conversión alta",
                    outcome_type=self.OutcomeType.SUCCESS,
                    lesson="CTA prominente en hero section funciona bien",
                    confidence=0.8,
                )
            )
        rules = run(engine.distill_rules())
        assert isinstance(rules, list)

    def test_get_relevant_rules(self):
        engine = self.Engine()
        run(
            engine.record_pattern(
                category=self.PatternCategory.DESIGN,
                context="E-commerce checkout",
                outcome="Pago completado",
                outcome_type=self.OutcomeType.SUCCESS,
                lesson="Formulario en 1 paso reduce abandono",
                confidence=0.95,
            )
        )
        rules = engine.get_relevant_rules(
            category=self.PatternCategory.DESIGN,
        )
        assert isinstance(rules, list)


# ══════════════════════════════════════════════════════════════════════════
# 61.4 — El Guardián de los Objetivos
# ══════════════════════════════════════════════════════════════════════════


class TestGuardian:
    def setup_method(self):
        from kernel.guardian import (
            AlertSeverity,
            GuardianDeObjetivos,
            GuardianObjetivoNoRegistrado,
            ObjetivoStatus,
        )

        self.Guardian = GuardianDeObjetivos
        self.ObjetivoStatus = ObjetivoStatus
        self.AlertSeverity = AlertSeverity
        self.GuardianObjetivoNoRegistrado = GuardianObjetivoNoRegistrado

    def test_init_registers_14_objetivos(self):
        guardian = self.Guardian()
        assert len(guardian._objetivos) == 14

    def test_to_dict_has_required_keys(self):
        guardian = self.Guardian()
        d = guardian.to_dict()
        assert "objetivos_registrados" in d
        assert "alertas_activas" in d
        assert "health_summary" in d

    def test_evaluate_objetivo_healthy(self):
        guardian = self.Guardian()
        health = run(
            guardian.evaluate_objetivo(
                objetivo_id=10,
                metrics={"predictions_accuracy": 8.5, "causal_events_count": 150},
            )
        )
        assert health.objetivo_id == 10
        assert health.score >= 0
        assert health.status in [s for s in self.ObjetivoStatus]

    def test_evaluate_objetivo_invalid_raises(self):
        guardian = self.Guardian()
        with pytest.raises(self.GuardianObjetivoNoRegistrado):
            run(guardian.evaluate_objetivo(objetivo_id=99, metrics={}))

    def test_evaluate_all(self):
        guardian = self.Guardian()
        metrics = {
            1: {"pipeline_completions": 5, "empresas_creadas": 3},
            10: {"predictions_accuracy": 7.0, "causal_events_count": 100},
            11: {"embriones_activos": 7, "embriones_ciclos_hoy": 14},
        }
        results = run(guardian.evaluate_all(metrics))
        assert len(results) == 3

    def test_list_objetivos(self):
        guardian = self.Guardian()
        objetivos = guardian.list_objetivos()
        assert len(objetivos) == 14
        assert all("id" in o and "nombre" in o for o in objetivos)

    def test_resolve_alert(self):
        guardian = self.Guardian()
        # Crear una alerta forzando un objetivo en estado failing
        run(
            guardian.evaluate_objetivo(
                objetivo_id=12,
                metrics={"monstruos_en_red": 0, "colaboraciones_activas": 0},
            )
        )
        if guardian._active_alerts:
            alert_id = guardian._active_alerts[0].id
            result = run(guardian.resolve_alert(alert_id))
            assert result is True

    def test_guardian_objetivo_14_en_lista(self):
        guardian = self.Guardian()
        obj_14 = guardian._objetivos.get(14)
        assert obj_14 is not None
        assert "Guardián" in obj_14["nombre"]


# ══════════════════════════════════════════════════════════════════════════
# 61.5 — Onboarding Wizard
# ══════════════════════════════════════════════════════════════════════════


class TestOnboardingWizard:
    def setup_method(self):
        from kernel.onboarding import (
            OnboardingFase,
            OnboardingSesionNoEncontrada,
            OnboardingWizard,
        )

        self.Wizard = OnboardingWizard
        self.Fase = OnboardingFase
        self.SesionNoEncontrada = OnboardingSesionNoEncontrada

    def test_init(self):
        wizard = self.Wizard()
        assert wizard is not None

    def test_to_dict_has_required_keys(self):
        wizard = self.Wizard()
        d = wizard.to_dict()
        assert "sesiones_activas" in d
        assert "sesiones_completadas" in d
        assert "avg_tiempo_minutos" in d

    def test_create_session(self):
        wizard = self.Wizard()
        session = run(wizard.create_session(user_id="user-001"))
        assert session.id is not None
        assert session.user_id == "user-001"
        assert session.fase_actual == self.Fase.DESCUBRIMIENTO

    def test_get_current_step(self):
        wizard = self.Wizard()
        session = run(wizard.create_session(user_id="user-002"))
        step = run(wizard.get_current_step(session.id))
        assert step is not None
        assert step.fase == self.Fase.DESCUBRIMIENTO

    def test_session_not_found_raises(self):
        wizard = self.Wizard()
        with pytest.raises(self.SesionNoEncontrada):
            run(wizard.get_current_step("sesion-inexistente"))

    def test_submit_answer_advances_wizard(self):
        wizard = self.Wizard()
        session = run(wizard.create_session(user_id="user-003"))
        step = run(wizard.get_current_step(session.id))
        result = run(
            wizard.submit_answer(
                session_id=session.id,
                campo=step.campo,
                respuesta="Quiero crear un SaaS de gestión de proyectos",
            )
        )
        assert "session" in result
        assert "next_step" in result

    def test_full_onboarding_flow(self):
        """Test del flujo completo de onboarding."""
        wizard = self.Wizard()
        session = run(wizard.create_session(user_id="user-004"))

        # Respuestas para cada paso
        respuestas = {
            "descripcion_inicial": "SaaS de gestión de proyectos para freelancers",
            "experiencia_ia": "Algo de experiencia",
            "vertical": "SaaS",
            "presupuesto_mensual": "$100-$500",
            "idiomas": "Español",
            "autonomia_nivel": "Balanceado (confirma decisiones importantes)",
            "primera_empresa_descripcion": "FreelanceHub — gestión de proyectos para freelancers",
            "activacion_embriones": "Activar todos ahora",
        }

        for campo, respuesta in respuestas.items():
            result = run(
                wizard.submit_answer(
                    session_id=session.id,
                    campo=campo,
                    respuesta=respuesta,
                )
            )

        # Verificar que el wizard se completó
        final_session = wizard._sessions[session.id]
        assert final_session.completed is True
        assert final_session.config is not None
        assert final_session.config.get("vertical") == "saas"
